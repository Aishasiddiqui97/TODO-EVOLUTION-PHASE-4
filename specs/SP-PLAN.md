# SP Implementation Plan - Phase III

## Summary

This plan implements the remaining MCP tools for the AI-powered Todo Chatbot (Phase III). The system already has:
- ✅ Chat endpoint with stateless architecture
- ✅ AI agent integration (OpenAI)
- ✅ MCP server infrastructure
- ✅ `add_task` tool

**What we need to implement**:
- 4 remaining MCP tools: `list_tasks`, `complete_task`, `update_task`, `delete_task`
- Tool registry configuration to register all tools
- Verification of the complete chat flow

## Proposed Changes

### Backend MCP Tools

#### [NEW] [list_tasks.py](file:///E:/Python.py/Hackaton%202(1)/backend/src/mcp/tools/list_tasks.py)
Create MCP tool for retrieving and filtering tasks. Will support:
- Filter by status (all, pending, completed)
- Filter by due date (today, overdue)
- Search by title/description
- Return structured task list

**Key Implementation Details**:
- Use `TaskService` for database queries
- Support multiple filter combinations
- Return empty list gracefully (not an error)
- Include task count in response

#### [NEW] [complete_task.py](file:///E:/Python.py/Hackaton%202(1)/backend/src/mcp/tools/complete_task.py)
Create MCP tool for marking tasks as complete. Will support:
- Match by task ID (exact)
- Match by task title (fuzzy)
- Handle task not found gracefully
- Return updated task details

**Key Implementation Details**:
- Use `TaskService.update_task()` to set `completed=True`
- Implement task matching logic (try ID first, then title)
- Return friendly error if task not found
- Include completion timestamp

#### [NEW] [update_task.py](file:///E:/Python.py/Hackaton%202(1)/backend/src/mcp/tools/update_task.py)
Create MCP tool for updating task details. Will support:
- Update title, description, due_date, priority
- Partial updates (only specified fields)
- Match by task ID or title
- Handle task not found gracefully

**Key Implementation Details**:
- Use `TaskService.update_task()` with partial updates
- Only update fields that are provided
- Implement task matching logic
- Return updated task details

#### [NEW] [delete_task.py](file:///E:/Python.py/Hackaton%202(1)/backend/src/mcp/tools/delete_task.py)
Create MCP tool for deleting tasks. Will support:
- Match by task ID or title
- Handle task not found gracefully
- Return deleted task details for confirmation

**Key Implementation Details**:
- Use `TaskService.delete_task()`
- Implement task matching logic
- Return task details before deletion for confirmation
- Soft delete vs hard delete (check existing implementation)

---

### Backend Registry

#### [MODIFY] [registry.py](file:///E:/Python.py/Hackaton%202(1)/backend/src/mcp/registry.py)
Update tool registry to register all 5 MCP tools:
- Uncomment and update tool imports
- Register all tools in `register_all()` method
- Verify registration count

**Changes**:
- Lines 46-59: Uncomment imports and registration calls
- Update to import all 5 tools
- Add logging for each registered tool

---

### Backend Main Application

#### [MODIFY] [main.py](file:///E:/Python.py/Hackaton%202(1)/backend/src/main.py)
Ensure tool initialization happens at startup:
- Call `initialize_tools()` on application startup
- Verify tools are registered before accepting requests

**Changes**:
- Add startup event handler if not present
- Call `initialize_tools()` from registry

---

## Verification Plan

### Automated Tests

#### Unit Tests for MCP Tools
Create test files for each new tool:

**File**: `backend/tests/unit/test_list_tasks_tool.py`
```bash
cd backend
pytest tests/unit/test_list_tasks_tool.py -v
```
Tests to include:
- List all tasks
- Filter by pending
- Filter by completed
- Filter by today
- Search by title
- Empty list handling

**File**: `backend/tests/unit/test_complete_task_tool.py`
```bash
cd backend
pytest tests/unit/test_complete_task_tool.py -v
```
Tests to include:
- Complete by task ID
- Complete by task title
- Task not found error
- Already completed task

**File**: `backend/tests/unit/test_update_task_tool.py`
```bash
cd backend
pytest tests/unit/test_update_task_tool.py -v
```
Tests to include:
- Update title
- Update due date
- Update priority
- Partial update
- Task not found error

**File**: `backend/tests/unit/test_delete_task_tool.py`
```bash
cd backend
pytest tests/unit/test_delete_task_tool.py -v
```
Tests to include:
- Delete by task ID
- Delete by task title
- Task not found error

#### Integration Tests

**File**: `backend/tests/integration/test_chat_endpoint.py`
```bash
cd backend
pytest tests/integration/test_chat_endpoint.py -v
```
Tests to include:
- Create task via chat
- List tasks via chat
- Complete task via chat
- Update task via chat
- Delete task via chat
- Multi-turn conversation
- Error handling

### Manual Verification

#### Test Chat Flow End-to-End

1. **Start Backend**:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn src.main:app --reload
```

2. **Test with curl or Postman**:

Create task:
```bash
curl -X POST http://localhost:8000/api/1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "Add buy groceries to my list"}'
```

List tasks:
```bash
curl -X POST http://localhost:8000/api/1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "Show me my tasks", "conversation_id": "<conv_id>"}'
```

Complete task:
```bash
curl -X POST http://localhost:8000/api/1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "Mark buy groceries as done", "conversation_id": "<conv_id>"}'
```

3. **Verify Database**:
```bash
# Check tasks were created/updated/deleted
psql $DATABASE_URL -c "SELECT * FROM tasks WHERE user_id = '1';"
# Check conversation history
psql $DATABASE_URL -c "SELECT * FROM messages WHERE conversation_id = '<conv_id>';"
```

4. **Test Error Scenarios**:
- Try to complete non-existent task
- Try ambiguous task reference
- Test with invalid input

**Expected Results**:
- All operations complete successfully
- Responses are conversational and friendly
- Errors are handled gracefully
- Conversation history persists correctly

### User Acceptance Testing

Once backend is verified, test with frontend:

1. Start frontend: `cd frontend && npm run dev`
2. Open browser to `http://localhost:3000/chat`
3. Test all user stories from SP-SPECIFICATION.md
4. Verify intent mapping accuracy
5. Measure response time (should be < 2s)

## Risk Mitigation

### Risk: Task Matching Ambiguity
**Issue**: Multiple tasks might match a title search  
**Mitigation**: Return error asking user to be more specific, suggest matches

### Risk: Performance with Large Task Lists
**Issue**: Listing 1000+ tasks could be slow  
**Mitigation**: Implement pagination, limit default results to 50

### Risk: Tool Registration Failure
**Issue**: Tools might not register at startup  
**Mitigation**: Add startup health check, fail fast if tools not registered

## Success Criteria

- [ ] All 5 MCP tools implemented and tested
- [ ] Tool registry successfully registers all tools
- [ ] Chat endpoint correctly routes to all tools
- [ ] Intent mapping accuracy > 90%
- [ ] Response time < 2 seconds
- [ ] All error scenarios handled gracefully
- [ ] Conversation history persists correctly
- [ ] All automated tests pass
