#!/bin/bash
# Test script for Event-Driven Todo Chatbot API

set -e

BASE_URL="http://localhost:8000"

echo "🧪 Testing Event-Driven Todo Chatbot API"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
response=$(curl -s "$BASE_URL/health")
echo "Response: $response"
if echo "$response" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi
echo ""

# Test 2: Root Endpoint
echo "Test 2: Root Endpoint"
echo "---------------------"
response=$(curl -s "$BASE_URL/")
echo "Response: $response"
if echo "$response" | grep -q "chat-api"; then
    echo "✅ Root endpoint passed"
else
    echo "❌ Root endpoint failed"
    exit 1
fi
echo ""

# Test 3: Create Task
echo "Test 3: Create Task"
echo "-------------------"
response=$(curl -s -X POST "$BASE_URL/api/v1/tasks" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Test Task from API",
        "description": "This is a test task",
        "priority": "high",
        "tags": ["test", "api"]
    }')
echo "Response: $response"
task_id=$(echo "$response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
if [ -n "$task_id" ]; then
    echo "✅ Task created with ID: $task_id"
else
    echo "❌ Task creation failed"
    exit 1
fi
echo ""

# Test 4: List Tasks
echo "Test 4: List Tasks"
echo "------------------"
response=$(curl -s "$BASE_URL/api/v1/tasks")
echo "Response: $response"
if echo "$response" | grep -q "$task_id"; then
    echo "✅ Task listing passed"
else
    echo "❌ Task listing failed"
    exit 1
fi
echo ""

# Test 5: Get Task by ID
echo "Test 5: Get Task by ID"
echo "----------------------"
response=$(curl -s "$BASE_URL/api/v1/tasks/$task_id")
echo "Response: $response"
if echo "$response" | grep -q "Test Task from API"; then
    echo "✅ Get task by ID passed"
else
    echo "❌ Get task by ID failed"
    exit 1
fi
echo ""

# Test 6: Update Task
echo "Test 6: Update Task"
echo "-------------------"
response=$(curl -s -X PUT "$BASE_URL/api/v1/tasks/$task_id" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Updated Test Task",
        "priority": "medium"
    }')
echo "Response: $response"
if echo "$response" | grep -q "Updated Test Task"; then
    echo "✅ Task update passed"
else
    echo "❌ Task update failed"
    exit 1
fi
echo ""

# Test 7: Complete Task
echo "Test 7: Complete Task"
echo "---------------------"
response=$(curl -s -X PATCH "$BASE_URL/api/v1/tasks/$task_id/complete")
echo "Response: $response"
if echo "$response" | grep -q "completed"; then
    echo "✅ Task completion passed"
else
    echo "❌ Task completion failed"
    exit 1
fi
echo ""

# Test 8: Chat Endpoint
echo "Test 8: Chat Endpoint"
echo "---------------------"
response=$(curl -s -X POST "$BASE_URL/api/v1/chat" \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Show me my tasks"
    }')
echo "Response: $response"
if echo "$response" | grep -q "conversationId"; then
    echo "✅ Chat endpoint passed"
else
    echo "❌ Chat endpoint failed"
    exit 1
fi
echo ""

# Test 9: Delete Task
echo "Test 9: Delete Task"
echo "-------------------"
response=$(curl -s -X DELETE "$BASE_URL/api/v1/tasks/$task_id" -w "%{http_code}")
http_code="${response: -3}"
if [ "$http_code" = "204" ]; then
    echo "✅ Task deletion passed"
else
    echo "❌ Task deletion failed (HTTP $http_code)"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ All tests passed!"
echo "=========================================="
