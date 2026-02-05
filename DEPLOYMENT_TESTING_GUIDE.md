# Deployment and Testing Guide

## 🚀 Quick Deployment Options

### **Option 1: Install Dapr CLI (Recommended for Testing)**

This is the fastest way to test full functionality locally.

#### **Step 1: Install Dapr CLI**

**Windows (PowerShell as Administrator):**
```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**Or download installer:**
- Visit: https://docs.dapr.io/getting-started/install-dapr-cli/
- Download Windows installer
- Run installer

#### **Step 2: Initialize Dapr**
```bash
dapr init
```
This installs:
- Dapr runtime
- Redis (for state store)
- Zipkin (for tracing)
- Placement service

#### **Step 3: Run Chat API with Dapr**
```bash
cd "E:\Python.py\Hackaton 2(1)\backend"

dapr run --app-id chat-api --app-port 8001 --dapr-http-port 3500 --dapr-grpc-port 50001 --components-path ../k8s/dapr -- python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

#### **Step 4: Run Recurring Task Service (Optional - in new terminal)**
```bash
cd "E:\Python.py\Hackaton 2(1)\backend"

dapr run --app-id recurring-task --app-port 8002 --dapr-http-port 3501 --dapr-grpc-port 50002 --components-path ../k8s/dapr -- python -m uvicorn src.services.recurring-task.main:app --host 0.0.0.0 --port 8002
```

---

### **Option 2: Standalone Mode (Current - Limited Functionality)**

Already running on port 8001. Works for:
- ✅ API documentation
- ✅ Health checks
- ✅ Basic endpoint testing
- ⚠️ No state persistence
- ⚠️ No event publishing

---

## 🧪 Test Scenarios

### **Test 1: Basic Task CRUD (Requires Dapr)**

**Create Task:**
```bash
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Test Task\", \"priority\": \"high\", \"tags\": [\"test\"]}"
```

**List Tasks:**
```bash
curl http://localhost:8001/api/v1/tasks
```

**Update Task:**
```bash
curl -X PUT http://localhost:8001/api/v1/tasks/{task-id} \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Updated Task\", \"priority\": \"medium\"}"
```

**Complete Task:**
```bash
curl -X PATCH http://localhost:8001/api/v1/tasks/{task-id}/complete
```

**Delete Task:**
```bash
curl -X DELETE http://localhost:8001/api/v1/tasks/{task-id}
```

---

### **Test 2: Recurring Tasks (Requires Dapr + Recurring Task Service)**

**Create Daily Recurring Task:**
```bash
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Daily standup\",
    \"priority\": \"high\",
    \"dueDate\": \"2026-02-07\",
    \"dueTime\": \"09:00\",
    \"recurrencePattern\": \"daily\"
  }"
```

**Create Weekly Recurring Task:**
```bash
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Team meeting\",
    \"priority\": \"medium\",
    \"dueDate\": \"2026-02-10\",
    \"dueTime\": \"14:00\",
    \"recurrencePattern\": \"every monday\"
  }"
```

**Complete Recurring Task (triggers next instance creation):**
```bash
# Get task ID from list
curl http://localhost:8001/api/v1/tasks

# Complete the task
curl -X PATCH http://localhost:8001/api/v1/tasks/{task-id}/complete

# Wait 2 seconds for event processing
sleep 2

# List tasks again - should see new instance
curl http://localhost:8001/api/v1/tasks
```

---

### **Test 3: Task Tags**

**Create Task with Tags:**
```bash
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Review proposal\",
    \"priority\": \"high\",
    \"tags\": [\"work\", \"urgent\", \"review\"]
  }"
```

**Filter by Tags:**
```bash
# Single tag
curl "http://localhost:8001/api/v1/tasks?tags=work"

# Multiple tags
curl "http://localhost:8001/api/v1/tasks?tags=work,urgent"
```

**Update Tags:**
```bash
curl -X PUT http://localhost:8001/api/v1/tasks/{task-id} \
  -H "Content-Type: application/json" \
  -d "{\"tags\": [\"work\", \"completed\"]}"
```

---

### **Test 4: User Preferences**

**Get Preferences:**
```bash
curl http://localhost:8001/api/v1/preferences
```

**Update Preferences:**
```bash
curl -X PUT http://localhost:8001/api/v1/preferences \
  -H "Content-Type: application/json" \
  -d "{
    \"timezone\": \"America/New_York\",
    \"defaultPriority\": \"high\",
    \"reminderAdvanceTime\": 48
  }"
```

---

### **Test 5: Combined Filters**

```bash
# Pending high-priority tasks tagged with "urgent"
curl "http://localhost:8001/api/v1/tasks?status=pending&priority=high&tags=urgent"

# Completed tasks tagged with "work"
curl "http://localhost:8001/api/v1/tasks?status=completed&tags=work"
```

---

## 📊 Expected Results

### **With Dapr (Full Functionality):**
- ✅ Tasks persist across restarts
- ✅ Events published to Kafka/Redis
- ✅ Recurring tasks create next instances automatically
- ✅ User preferences saved
- ✅ State management working
- ✅ All CRUD operations functional

### **Without Dapr (Standalone):**
- ✅ API documentation works
- ✅ Health checks work
- ✅ Endpoints respond
- ⚠️ Tasks not persisted (500 errors)
- ⚠️ Events not published
- ⚠️ Recurring tasks don't auto-create

---

## 🔍 Verification Checklist

**After starting with Dapr:**

1. **Check Dapr is running:**
```bash
dapr --version
dapr list
```

2. **Check service health:**
```bash
curl http://localhost:8001/health
```

3. **Check API documentation:**
```
http://localhost:8001/docs
```

4. **Create and retrieve a task:**
```bash
# Create
TASK_ID=$(curl -s -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "priority": "high"}' | jq -r '.id')

# Retrieve
curl http://localhost:8001/api/v1/tasks/$TASK_ID
```

5. **Test recurring task:**
```bash
# Create recurring task
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Daily task", "recurrencePattern": "daily", "dueDate": "2026-02-07", "dueTime": "09:00"}'

# Complete it
curl -X PATCH http://localhost:8001/api/v1/tasks/{task-id}/complete

# Check for next instance (wait 2 seconds)
sleep 2
curl http://localhost:8001/api/v1/tasks
```

---

## 🐛 Troubleshooting

**Issue: "Dapr health check timed out"**
- Solution: Install and initialize Dapr CLI
- Run: `dapr init`

**Issue: Port already in use**
- Solution: Change port in dapr run command
- Use: `--app-port 8002 --dapr-http-port 3502`

**Issue: Components not found**
- Solution: Specify components path
- Use: `--components-path ../k8s/dapr`

**Issue: Recurring tasks not creating next instance**
- Solution: Ensure Recurring Task Service is running
- Check: Both services must be running with Dapr

---

## 📝 Quick Start Commands

**Terminal 1 - Chat API:**
```bash
cd "E:\Python.py\Hackaton 2(1)\backend"
dapr run --app-id chat-api --app-port 8001 --dapr-http-port 3500 --components-path ../k8s/dapr -- python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

**Terminal 2 - Recurring Task Service:**
```bash
cd "E:\Python.py\Hackaton 2(1)\backend"
dapr run --app-id recurring-task --app-port 8002 --dapr-http-port 3501 --components-path ../k8s/dapr -- python -m uvicorn src.services.recurring-task.main:app --host 0.0.0.0 --port 8002
```

**Terminal 3 - Testing:**
```bash
# Run test script
cd "E:\Python.py\Hackaton 2(1)"
bash test-api.sh
```

---

## 🎯 Success Criteria

- [ ] Dapr CLI installed and initialized
- [ ] Chat API running with Dapr sidecar
- [ ] Tasks can be created and retrieved
- [ ] Tasks persist across service restarts
- [ ] Recurring tasks create next instances
- [ ] Tag filtering works
- [ ] User preferences can be saved
- [ ] All API endpoints respond correctly

---

**Next Step:** Install Dapr CLI and run the commands above to test full functionality!
