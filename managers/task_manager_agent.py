"""
Task Manager Agent

Purpose:
- Receive incoming task/event
- Decide which worker agent should handle it
- Manage handoff between agents
- Maintain execution flow

Examples:
- new lead -> Lead Triage Agent
- qualified lead -> Engagement Agent
- campaign review request -> Campaign Optimization Agent
"""