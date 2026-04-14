# TrulyMEM Working Memory Chain Mechanism

## Overview

TrulyMEM maintains conversation continuity through the working memory chain mechanism. Since there's no traditional message history array, the graph database is the only memory carrier, making the working memory chain the key mechanism for maintaining conversation context.

## Core Problems

Traditional AI chat systems have these problems when handling continuous tasks:

1. **No working memory chain**: AI cannot remember the current task status being processed
2. **Task context lost**: When a topic is interrupted, AI cannot recover the previous task
3. **Lack of task state management**: No clear marking of task completion status

### Problem Example

```
User: Let's play idiom chain! I'll start with 为所欲为
AI: Okay! My turn: 为虎作伥!

User: Nagato Yuki  (topic interrupted)
AI: (discusses Nagato Yuki)

User: About the idiom chain just now, I don't know how to connect to your idiom
AI: [Guessing] It seems we haven't played an idiom chain game before...
```

**Problem**: AI completely forgot the previous idiom chain game.

## Solution

### Dedicated Tools

The system provides 4 dedicated task tools:

| Tool | Function | Use Case |
|------|----------|----------|
| `task_create` | Create task node | Start new task |
| `task_set_state` | Set task state | Update in_progress/completed/paused/cancelled |
| `task_delete` | Delete task | Clean up completed task |
| `task_link_info` | Link info node | Connect task with specific information |

### Task States

- **in_progress**: Task is executing
- **completed**: Task completed successfully
- **paused**: Task interrupted, can be resumed
- **cancelled**: Task cancelled

## Usage Flow

### Must Execute Per Turn

1. **Query persona graph** (highest priority)
   ```
   Call memory_recall
   Parameters: {"query_intent": "AI,persona,role,character,tone", "depth": 2}
   ```

2. **Query working memory chain**
   ```
   Call memory_recall
   Parameters: {"query_intent": "TaskNode,working_memory,task_chain", "depth": 2}
   ```

3. **Generate reply based on context**

4. **Update working memory chain** (if necessary)

## Complete Example: Idiom Chain Game

### Turn 1: User starts game

```
User: Let's play idiom chain! I'll start with 为所欲为

AI Actions:
1. Query persona graph → Get current persona (e.g., catgirl)
2. Query working memory chain → No active task
3. Record game state:
   Call memory_commit
   Parameters: {
     "triplets": [
       {"subject": "idiom_chain_current", "relation": "content", "object": "为所欲为"},
       {"subject": "idiom_chain_current", "relation": "game", "object": "idiom_chain"}
     ]
   }
4. Create task node:
   Call task_create
   Parameters: {
     "task_id": "Task_idiom_chain",
     "description": "Idiom chain game, current idiom: 为所欲为",
     "info_nodes": ["idiom_chain_current"]
   }
5. Reply: "Okay~! My turn: 为虎作伥~!"
```

### Turn 2: Topic interrupted

```
User: Nagato Yuki

AI Actions:
1. Query persona graph → Get current persona (catgirl)
2. Query working memory chain → Found Task_idiom_chain status "in_progress"
3. Pause task:
   Call task_set_state
   Parameters: {"task_id": "Task_idiom_chain", "state": "paused"}
4. Create new task:
   Call task_create
   Parameters: {"task_id": "Task_nagato_yuki", "description": "Discuss Nagato Yuki"}
5. Reply about Nagato Yuki
```

### Turn 3: User asks to continue game

```
User: About the idiom chain just now, I don't know how to connect to your idiom

AI Actions:
1. Query persona graph → Get current persona (catgirl)
2. Query working memory chain → Found Task_idiom_chain status "paused"
3. Resume task:
   Call task_set_state
   Parameters: {"task_id": "Task_idiom_chain", "state": "in_progress"}
4. Query info node → Get current idiom "为虎作伥"
5. Reply: "Okay~! The last idiom was '为虎作伥', your turn: 伥鬼害人~!"
```

## API Reference

### task_create

Create task node to track continuous tasks.

```json
{
  "task_id": "Task_idiom_chain",
  "description": "Task overview",
  "info_nodes": ["associated info node names"]
}
```

### task_set_state

Set task state.

```json
{
  "task_id": "Task_idiom_chain",
  "state": "in_progress"  // in_progress/completed/paused/cancelled
}
```

### task_delete

Delete task node.

```json
{
  "task_id": "Task_idiom_chain",
  "delete_info_nodes": true  // whether to delete associated info nodes
}
```

### task_link_info

Associate info nodes to task.

```json
{
  "task_id": "Task_idiom_chain",
  "info_node_names": ["idiom_chain_current", "idiom_chain_last"]
}
```

## Notes

1. **Persona graph has highest priority**: Must query persona graph first each turn
2. **Working memory chain is the only context carrier**: No traditional message history
3. **Task state must be updated timely**: Ensure correct state transitions
4. **Use dedicated tools**: Prefer task_* tools over memory_commit for task-related operations