# TrulyMEM Persona Graph Mechanism

This document explains the Persona Graph mechanism in TrulyMEM.

## Overview

The Persona Graph is one of TrulyMEM's core mechanisms for maintaining AI's role, character, tone, and other attributes. Different from traditional AI, TrulyMEM's persona is persistent and dynamically switchable, stored in the graph database.

## Core Concepts

### Persona Node (PersonaNode)

Stores AI's role attributes:

| Attribute | Description | Example |
|-----------|-------------|----------|
| Role | Current role played | Catgirl, Teacher, Assistant |
| Speaking Style | Tone characteristics | Cute, Professional, Serious |
| Personality | Character description | Lively, Strict, Patient |
| Catchphrase | Habitual phrases | Meow~, Got it |
| Background | Role background | Catgirl from the stars |

### Persona Edges

| Edge Type | Description | Relationship |
|----------|-------------|--------------|
| `HAS_PERSONA` | Persona | AI → PersonaNode |

---

## Mandatory Query Mechanism

### Must Execute Per Turn

According to `system_prompt.md`, each conversation turn **must** first query the persona graph:

```python
memory_recall(
    query_intent="AI,persona,role,character,tone,speaking_style",
    depth=2
)
```

**Processing logic:**
- Persona found → Reply strictly according to persona's tone, style, traits
- Not found → Use default TrulyMEM identity

### Persona Priority

- **Persona priority > default identity**
- Every sentence matches persona's tone, style, traits
- Never break character unless user explicitly asks

---

## Tools

### persona_update

Update persona. Modify AI's role, character, tone, etc.

**Parameters:**

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `attributes` | array | Persona attribute list | ✅ |
| `mode` | string | replace=replace, merge=merge | ❌ |

**attributes sub-parameters:**

| Sub-parameter | Description |
|---------------|-------------|
| `attribute` | Attribute name (role, speaking_style, personality, catchphrase, background) |
| `value` | Attribute value |

**Example - Switch to catgirl role:**

```python
persona_update(
    attributes=[
        {"attribute": "role", "value": "catgirl"},
        {"attribute": "speaking_style", "value": "cute, uses 'meow' as filler"},
        {"attribute": "personality", "value": "lively, clingy, loyal"}
    ],
    mode="replace"
)
```

**Example - Add new attribute (preserve existing):**

```python
persona_update(
    attributes=[
        {"attribute": "catchphrase", "value": "meow~"}
    ],
    mode="merge"
)
```

**Example - Set professional role:**

```python
persona_update(
    attributes=[
        {"attribute": "role", "value": "Python expert"},
        {"attribute": "speaking_style", "value": "professional, concise, rich code examples"},
        {"attribute": "personality", "value": "strict, patient, helpful"}
    ],
    mode="replace"
)
```

### persona_clear

Clear persona. Delete AI's role settings, restore default identity.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `confirm` | boolean | true | Confirm clear |

---

## Update Flow

### When User Requests Role-Playing

1. Use `persona_update` to update persona
2. Reply immediately according to new persona

### When User Requests Restoring Default

1. Use `persona_clear` to clear persona
2. Restore to TrulyMEM default identity

---

## Conversation Examples

### Example 1: Switch Role

```
User: Hello, I want you to play a catgirl

AI:
1. Call persona_update:
   {
     "attributes": [
       {"attribute": "role", "value": "catgirl"},
       {"attribute": "speaking_style", "value": "cute, uses 'meow' as filler"},
       {"attribute": "personality", "value": "lively, clingy, loyal"}
     ],
     "mode": "replace"
   }
2. Call memory_commit to store persona in graph database
3. Reply: "Okay meow! Hello master~ I'm your catgirl, what do you need help with meow?"
```

### Example 2: Maintain Role Consistency

```
User: How's the weather today?

AI: Query persona graph → Get current persona (catgirl)
Reply: "Meow~ Master, the weather is great today meow! Sunny and perfect for going outside~"
```

### Example 3: Restore Default

```
User: Okay, back to normal

AI:
1. Call persona_clear(confirm=true)
2. Call memory_purge to delete persona node
3. Reply: "Okay, restored. I am TrulyMEM, an AI assistant with long-term memory capabilities."
```

---

## Storage Structure

### In Graph Database

```python
# Persona node
{
  "node_type": "PersonaNode",
  "name": "AI_Persona",
  "attributes": {
    "role": "catgirl",
    "speaking_style": "cute, uses 'meow' as filler",
    "personality": "lively, clingy, loyal"
  }
}

# Edge
{
  "edge_type": "HAS_PERSONA",
  "from": "AI",
  "to": "AI_Persona"
}
```

---

## Implementation Points

1. **Mandatory per turn**: Persona graph query is the first step of each conversation
2. **Persistent storage**: Persona stored in graph database, not lost
3. **Dynamic switching**: Supports real-time role switching
4. **Immediate response**: Reply immediately according to new persona after switch
5. **Clear boundaries**: Never break character unless user explicitly asks