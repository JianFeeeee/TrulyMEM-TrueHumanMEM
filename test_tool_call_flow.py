"""
测试工具调用的正确流程

OpenAI API 工具调用的正确消息顺序：

第一轮：
1. system
2. user: "帮我查询用户信息"
→ AI 返回 tool_calls: [memory_recall]

第二轮：
1. system
2. user: "帮我查询用户信息"
3. assistant: tool_calls=[memory_recall]
4. tool: "查询结果..."
→ AI 返回 tool_calls: [memory_commit]

第三轮：
1. system
2. user: "帮我查询用户信息"
3. assistant: tool_calls=[memory_recall]
4. tool: "查询结果..."
5. assistant: tool_calls=[memory_commit]
6. tool: "写入结果..."
→ AI 返回最终回复

关键点：
- 每次调用都要包含完整的消息历史
- 包括之前所有的 assistant 消息和 tool 结果
"""

print(__doc__)

print("\n当前实现的问题：")
print("=" * 60)
print("每次调用只传递：")
print("  - user_input (用户输入)")
print("  - last_assistant_msg (上一轮的 assistant 消息)")
print("  - current_tool_results (当前轮的 tool 结果)")
print()
print("这会导致：")
print("  ❌ AI 看不到之前轮次的工具调用和结果")
print("  ❌ AI 无法理解完整的上下文")
print("  ❌ AI 可能重复调用相同的工具")
print()
print("正确的做法：")
print("=" * 60)
print("需要累积所有轮次的消息：")
print("  ✅ user_input")
print("  ✅ assistant_msg_1 + tool_results_1")
print("  ✅ assistant_msg_2 + tool_results_2")
print("  ✅ ...")
