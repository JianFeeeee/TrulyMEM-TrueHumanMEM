# API Key 配置指南

## ❌ 连接错误原因

**错误信息：** `Connection error`

**可能原因：**
1. ❌ API Key 未配置
2. ❌ API Key 无效
3. ❌ 网络无法访问 API
4. ❌ API 服务器暂时不可用

## ✅ 解决方法

### 方法1：在 TUI 中配置（推荐）

**步骤：**

1. **按 F2** - 展开右侧边栏
2. **点击"配置"** - 展开配置区域
3. **输入 API Key** - 在输入框输入你的密钥
4. **按 Tab** - 保存并应用

**详细操作：**

```
启动应用
    ↓
看到欢迎消息
    ↓
按 F2 键
    ↓
右侧出现侧边栏
    ↓
点击"配置"标题
    ↓
看到三个输入框：
┌─────────────────────┐
│ API Key:            │
│ [******************]│ ← 输入你的 Key
│                     │
│ 模型:               │
│ [deepseek-chat    ] │
│                     │
│ Base URL:           │
│ [https://api...    ]│
└─────────────────────┘
    ↓
输入 API Key: sk-xxxxxxxxxxxxx
    ↓
按 Tab 键
    ↓
看到通知："✅ 配置已更新并应用"
    ↓
配置完成！
```

### 方法2：环境变量配置

**Windows:**
```cmd
setx DEEPSEEK_API_KEY "sk-xxxxxxxxxxxxx"
```

**Linux/macOS:**
```bash
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxx"
```

**注意：** 设置环境变量后需要重启终端。

### 方法3：配置文件

**创建配置文件：**

**Windows:**
```
C:\Users\<你的用户名>\.graph_memory_tui\config.json
```

**Linux/macOS:**
```
~/.graph_memory_tui/config.json
```

**文件内容：**
```json
{
  "api_key": "sk-xxxxxxxxxxxxx",
  "model": "deepseek-chat",
  "base_url": "https://api.deepseek.com"
}
```

## 🔑 获取 API Key

### DeepSeek API Key

1. 访问：https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制密钥（以 `sk-` 开头）

### 其他兼容 API

如果使用其他 OpenAI 兼容 API：
- 修改 Base URL
- 使用对应的 API Key

## 🧪 验证配置

### 测试步骤

1. **配置 API Key** - 按上述方法配置
2. **发送测试消息** - 输入"你好"
3. **查看响应** - 应该收到 AI 回复

### 成功标志

```
✅ 配置已更新并应用

[你的消息] 你好
[AI回复] 你好！我是图数据库记忆助手...
```

### 失败标志

```
❌ 错误: Connection error

网络连接错误！可能的原因：
1. API Key 未配置或无效
2. 网络无法访问 API 服务器
...
```

## 🔧 故障排除

### 问题1：API Key 格式错误

**检查：**
- ✅ 以 `sk-` 开头
- ✅ 没有空格
- ✅ 完整复制

**示例：**
```
✅ sk-1234567890abcdef...
❌ 1234567890abcdef...  (缺少 sk- 前缀)
❌ sk-1234 5678...      (包含空格)
```

### 问题2：网络问题

**检查：**
- 网络连接是否正常
- 能否访问 https://api.deepseek.com
- 是否需要代理/VPN

**测试网络：**
```bash
curl https://api.deepseek.com/v1/models
```

### 问题3：API Key 无效

**检查：**
- API Key 是否过期
- 账号是否有余额
- 是否有权限访问 API

**解决：**
- 重新生成 API Key
- 检查账号状态
- 充值或升级套餐

### 问题4：配置未生效

**检查：**
- 是否按 Tab 保存
- 是否看到配置更新通知
- 重启应用测试

**解决：**
- 重新配置
- 检查配置文件
- 清除缓存重试

## 📊 配置优先级

1. **TUI 页面配置**（最高优先级）
   - 实时生效
   - 自动保存

2. **环境变量**
   - 全局生效
   - 需要重启终端

3. **配置文件**
   - 持久化保存
   - 自动加载

## 💡 最佳实践

### 安全建议

- ✅ 不要分享 API Key
- ✅ 定期更换密钥
- ✅ 使用环境变量或配置文件
- ❌ 不要在代码中硬编码
- ❌ 不要提交到版本控制

### 使用建议

- ✅ 使用 TUI 配置（最方便）
- ✅ 配置后立即测试
- ✅ 保存配置文件备份
- ✅ 记录 API Key 获取日期

## 🎯 快速配置清单

- [ ] 获取 API Key
- [ ] 启动应用
- [ ] 按 F2 展开侧边栏
- [ ] 点击"配置"
- [ ] 输入 API Key
- [ ] 按 Tab 保存
- [ ] 发送测试消息
- [ ] 验证响应正常

## 🎉 配置成功后

你就可以：
- ✅ 与 AI 对话
- ✅ 使用图数据库记忆
- ✅ 执行工具调用
- ✅ 管理长期记忆

开始你的图记忆对话之旅吧！

🎯
