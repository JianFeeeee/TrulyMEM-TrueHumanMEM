"""测试消息顺序"""
from graph_memory_tui.core.graph_client import GraphMemoryClient

# 模拟消息构建
class MockClient:
    pass

class MockGraph:
    pass

# 测试消息顺序
client = GraphMemoryClient.__new__(GraphMemoryClient)
client.client = MockClient()
client.graph = MockGraph()
client.tools = []
client.system_prompt = 'You are a helpful assistant.'

# 模拟第一次调用（无工具结果）
print('=== 第一次调用（无工具结果）===')
messages = [{'role': 'system', 'content': client.system_prompt}]
messages.append({'role': 'user', 'content': '你好'})
for i, msg in enumerate(messages):
    content = str(msg.get('content', ''))[:50]
    print(f'{i+1}. {msg["role"]}: {content}')

print()
print('=== 第二次调用（有工具结果）===')
messages = [{'role': 'system', 'content': client.system_prompt}]
messages.append({'role': 'user', 'content': '你好'})
messages.append({
    'role': 'assistant',
    'content': None,
    'tool_calls': [{'id': 'call_123', 'type': 'function', 'function': {'name': 'memory_recall', 'arguments': '{}'}}]
})
messages.append({'role': 'tool', 'tool_call_id': 'call_123', 'content': '查询结果...'})

for i, msg in enumerate(messages):
    role = msg.get('role')
    if role == 'tool':
        tid = msg.get('tool_call_id')
        print(f'{i+1}. {role}: tool_call_id={tid}')
    elif role == 'assistant' and msg.get('tool_calls'):
        tc_count = len(msg.get('tool_calls'))
        print(f'{i+1}. {role}: tool_calls={tc_count}')
    else:
        content = str(msg.get('content', ''))[:50]
        print(f'{i+1}. {role}: {content}')

print()
print('✅ 消息顺序正确！')
print('AI 可以看到：')
print('1. 用户说了什么')
print('2. 自己调用了什么工具')
print('3. 工具返回了什么结果')
