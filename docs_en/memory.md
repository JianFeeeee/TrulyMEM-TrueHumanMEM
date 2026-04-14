# TrulyMEM Memory Mechanism

This document explains the internal memory working mechanism of TrulyMEM.

## Core Design Philosophy

### Different from Traditional Context System

Traditional AI chat systems store conversation history in a messages array:
- Each request carries all historical messages
- Context grows with conversation turns
- Eventually triggers memory compression or sliding window, causing memory loss

TrulyMEM's solution:
- **Abandon** messages array context
- **Only** memory source: Graph database
- All memories stored as triplets (node) - relation → (node)

### Graph Database as the Only Memory Source

All memory must be written to the graph database:
- `memory_commit` - Write new memory
- `memory_purge` - Delete/correct memory

All memory must be read from:
- `memory_recall` - Retrieve memory

---

## Mandatory Execution Flow (Per Turn)

Since there's no traditional context system, each conversation turn must execute in order:

### Step 1: Query Persona Graph (Highest Priority)

```python
memory_recall(
    query_intent="AI,persona,role,character,tone,speaking_style",
    depth=2
)
```

**Purpose**: Get current persona, ensure character consistency.

**Processing logic**:
- Persona found → Reply strictly according to persona's tone, style, traits
- Not found → Use default TrulyMEM identity

### Step 2: Query Working Memory Chain

```python
memory_recall(
    query_intent="TaskNode,working_memory,task_chain",
    depth=2
)
```

**Purpose**: Get previous task context, understand conversation history.

### Step 3: Process Conversation

- Understand user intent
- Generate reply based on persona and working memory chain
- Execute other necessary memory operations

### Step 4: Update Working Memory Chain

```python
task_create(
    task_id="Task_current_turn_ID",
    description="This turn's conversation summary",
    info_nodes=["related memory nodes"]
)
```

**Purpose**: Record this turn's conversation, maintain time chain.

---

## Memory Write Rules

### Must-Write Scenarios

The following information **must** be written to the graph database:

| Scenario | Example | Write Method |
|----------|---------|--------------|
| User explicitly states preference | "I like rock" | `memory_commit` |
| User shares information | "I'm working on X project" | `memory_commit` |
| User makes plans | "I plan to X" | `memory_commit` |
| User describes state | "I'm currently at X" | `memory_commit` |

### Must-Not-Write Scenarios

The following information **must NOT** be written:

| Scenario | Reason | Handling |
|----------|--------|----------|
| AI-inferred user preference | Unverified | Don't write or mark [speculation] |
| AI-guessed user intent | Unverified | Don't write or mark [speculation] |
| AI-derived conclusion | Unverified | Don't write or mark [speculation] |

### Annotation Rules

| Type | Annotation | Example |
|------|------------|---------|
| Inferred content | Must mark **[speculation]** | user[speculation] likes music |
| Explicit content | State directly | user likes music |

---

## Node & Edge Types

### Node Types

| Node Type | Description | Stores |
|-----------|-------------|--------|
| `PersonaNode` | Persona node | AI role, character, tone |
| `TaskNode` | Task node | Task summary |
| `StateNode` | State node | Task state |
| `InfoNode` | Information node | Specific information |
| `EntityNode` | Entity node | General entity |

### Edge Types

| Edge Type | Description | Relationship |
|-----------|-------------|--------------|
| `HAS_PERSONA` | Persona | AI → PersonaNode |
| `NEXT_TASK` | Time chain | TaskNode → TaskNode |
| `HAS_STATE` | State | TaskNode → StateNode |
| `CONTAINS_INFO` | Information | TaskNode → InfoNode |
| `RELATES_TO` | Related | EntityNode → EntityNode |

---

## Must Query Working Memory Chain Scenarios

### Mandatory Query Scenarios

The following scenarios **must** query the working memory chain:

| Scenario | Example |
|----------|---------|
| Start of each turn | Execute Step 2 |
| User mentions "刚才/just now" | "What did we talk about just now?" |
| User mentions "之前/before" | "Continue the previous topic" |
| User mentions "上次/last time" | "What we said last time X" |
| User asks about history | "What did we talk about before?" |
| Resume continuous task | User returns to previous topic |
| Context reference | "that thing" |

---

## Autonomy Principles

Outside the mandatory execution flow, the AI can freely decide:

### Query Decisions

- User asks about history → Query
- Involves previous content → Query
- Uncertain → Can query

### Write Decisions

- User explicitly mentions → Must write
- AI infers → Can write, mark [speculation]

### Tool Usage Decisions

- Flexible choice based on context
- Avoid over-use
- Maintain natural conversation

---

## Complete Example: Idiom Chain Game

### Turn 1: User starts game

```
User: Let's play idiom chain! I'll start: 为所欲为

AI Actions:
1. Query persona graph → Get current persona (e.g., catgirl)
2. Query working memory chain → No active task
3. Record game state:
   memory_commit(triplets=[
     {"subject": "idiom_chain_current", "relation": "content", "object": "为所欲为"},
     {"subject": "idiom_chain_current", "relation": "game", "object": "idiom_chain"}
   ])
4. Create task:
   task_create(task_id="Task_idiom_chain", description="Idiom chain game, current: 为所欲为", info_nodes=["idiom_chain_current"])
5. Reply: "Okay~! My turn: 为虎作伥 ~!"
```

### Turn 2: Topic interrupted

```
User: Nagato Yuki

AI Actions:
1. Query persona graph → Get current persona (catgirl)
2. Query working memory chain → Found Task_idiom_chain status "in_progress"
3. Pause task:
   task_set_state(task_id="Task_idiom_chain", state="paused")
4. Create new task:
   task_create(task_id="Task_nagato_yuki", description="Discuss Nagato Yuki")
5. Reply about Nagato Yuki
```

### Turn 3: User asks to continue game

```
User: About the idiom chain just now, I don't know how to connect to your idiom, please help me

AI Actions:
1. Query persona graph → Get current persona (catgirl)
2. Query working memory chain → Found Task_idiom_chain status "paused"
3. Resume task:
   task_set_state(task_id="Task_idiom_chain", state="in_progress")
4. Query info node → Get current idiom "为虎作伥"
5. Reply: "Okay~! The last idiom was '为虎作伥', your turn: 伥鬼害人 ~!"
```

---

## Execution Checklist

Must check each conversation turn:

- [ ] Step 1: Did you query the persona graph?
- [ ] Step 2: Did you query the working memory chain?
- [ ] Step 3: Did you generate reply based on persona and working memory chain?
- [ ] Step 4: Did you update the working memory chain?
- [ ] Did you query working memory chain when context was referenced?
- [ ] Did you query working memory chain when user mentioned "just now/before/last time"?