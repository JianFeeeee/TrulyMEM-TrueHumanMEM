"""
测试工作记忆链机制
"""
import sys
sys.path.insert(0, 'e:/program/graph_enable_ability')

from graph_memory_tui.core.optimized_operations import OPTIMIZED_SYSTEM_PROMPT

def test_working_memory_chain():
    """测试工作记忆链机制是否正确添加"""
    
    print("=" * 60)
    print("工作记忆链机制测试")
    print("=" * 60)
    
    # 测试1: 检查核心概念
    assert "工作记忆链机制" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到工作记忆链机制"
    print("[OK] 测试1通过: 工作记忆链机制已添加")
    
    # 测试2: 检查节点类型
    assert "TaskNode" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到TaskNode"
    assert "StateNode" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到StateNode"
    assert "普通记忆节点" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到普通记忆节点"
    assert "InfoNode" not in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] InfoNode应该被移除"
    print("[OK] 测试2通过: 所有节点类型已正确定义(使用普通记忆节点)")
    
    # 测试3: 检查边类型
    assert "NEXT_TASK" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到NEXT_TASK"
    assert "HAS_STATE" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到HAS_STATE"
    assert "CONTAINS_INFO" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到CONTAINS_INFO"
    assert "SUB_TASK" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到SUB_TASK"
    print("[OK] 测试3通过: 所有边类型已定义")
    
    # 测试4: 检查强制执行规则
    assert "强制执行规则" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到强制执行规则"
    assert "每轮对话开始时" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到每轮对话开始时"
    assert "每轮对话结束时" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到每轮对话结束时"
    print("[OK] 测试4通过: 强制执行规则已定义")
    
    # 测试5: 检查连续性任务处理
    assert "连续性任务处理" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到连续性任务处理"
    assert "成语接龙" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到成语接龙示例"
    print("[OK] 测试5通过: 连续性任务处理已定义")
    
    # 测试6: 检查任务状态转换
    assert "State_进行中" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到State_进行中"
    assert "State_已完成" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到State_已完成"
    assert "State_已暂停" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到State_已暂停"
    print("[OK] 测试6通过: 任务状态转换已定义")
    
    # 测试7: 检查核心职责更新
    assert "维护工作记忆链" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到维护工作记忆链"
    print("[OK] 测试7通过: 核心职责已更新")
    
    # 测试8: 检查示例说明
    assert "第一轮：用户发起游戏" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到第一轮示例"
    assert "第二轮：话题被打断" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到第二轮示例"
    assert "第三轮：用户要求继续游戏" in OPTIMIZED_SYSTEM_PROMPT, "[ERROR] 未找到第三轮示例"
    print("[OK] 测试8通过: 完整示例已添加")
    
    print("=" * 60)
    print("所有测试通过! 工作记忆链机制已成功添加到提示词中")
    print("=" * 60)
    
    # 统计信息
    total_length = len(OPTIMIZED_SYSTEM_PROMPT)
    working_memory_length = len("工作记忆链机制")
    
    print(f"\n提示词总长度: {total_length} 字符")
    print(f"工作记忆链机制部分约占: {working_memory_length / total_length * 100:.2f}%")
    
    return True

if __name__ == "__main__":
    try:
        test_working_memory_chain()
        print("\n[SUCCESS] 测试成功!")
    except AssertionError as e:
        print(f"\n[ERROR] 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        sys.exit(1)
