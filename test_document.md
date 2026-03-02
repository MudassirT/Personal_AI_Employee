---
type: test_document
priority: normal
status: pending
---

# Test Document for Bronze Tier

This is a sample document to test the AI Employee Bronze Tier workflow.

## Purpose

This file demonstrates the File System Watcher functionality. When you drop this file into the `Inbox/` folder while the watcher is running, it should:

1. Detect the new file
2. Create an action file in `Needs_Action/`
3. The Orchestrator should then create a plan in `Plans/`

## Test Steps

1. Start the File System Watcher:
   ```bash
   python watchers/filesystem_watcher.py
   ```

2. Start the Orchestrator in a new terminal:
   ```bash
   python orchestrator.py
   ```

3. Copy this file to the `AI_Employee_Vault/Inbox/` folder

4. Watch the logs in:
   - `AI_Employee_Vault/Logs/`
   - Terminal output from both processes

5. Process with Claude Code:
   ```bash
   claude --cwd "AI_Employee_Vault" "Process all files in /Needs_Action"
   ```

## Expected Result

- Action file created in `Needs_Action/`
- Plan file created in `Plans/`
- Dashboard.md updated with activity
- Logs written to `Logs/` folder

---

*This is a test document for Bronze Tier validation*
