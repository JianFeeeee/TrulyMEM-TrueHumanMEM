"""
Web API 服务 - 将 Packet 协议映射为 RESTful API
"""
import sys
import os
import argparse
import threading
import time
import hashlib
from datetime import timedelta
from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_cors import CORS

# 添加项目路径以便导入 core 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.server import BackendServer, Packet, PacketType
from core.client import BackendClient
from core.activity_recorder import get_recorder
from core.embedded_db import EmbeddedGraphDB


LOGIN_MAX_ATTEMPTS = 5          # 最大尝试次数
LOGIN_WAIT_MINUTES = 5           # 超过次数后等待分钟数
LOGIN_BAN_THRESHOLD = 3          # 超过此轮次后 ban IP
LOGIN_BAN_HOURS = 24            # IP ban 时长（小时）

# 内存记录：{ip: {"attempts": 0, "first_fail": 0, "ban_until": 0, "rounds": 0}}
_login_attempts: dict = {}

def _check_login_limit(ip: str) -> dict:
    """检查 IP 的登录限制。返回 {"blocked": bool, "reason": str, "wait_seconds": int}"""
    now = time.time()
    record = _login_attempts.get(ip)

    if record:
        # 检查是否在 ban 中
        if record["ban_until"] > now:
            remaining = int(record["ban_until"] - now)
            return {"blocked": True, "reason": f"IP 已被临时封禁，剩余 {remaining//60} 分钟", "wait_seconds": remaining}

        # 检查是否需要等待（连续失败超过阈值）
        if record["attempts"] >= LOGIN_MAX_ATTEMPTS:
            wait_end = record["first_fail"] + LOGIN_WAIT_MINUTES * 60
            if wait_end > now:
                remaining = int(wait_end - now)
                return {"blocked": True, "reason": f"登录尝试过多，请等待 {remaining} 秒后再试", "wait_seconds": remaining}
            else:
                # 等待时间已过，重置计数但记录轮次
                record["rounds"] += 1
                record["attempts"] = 0
                record["first_fail"] = 0

                # 如果轮次超过阈值则 ban IP
                if record["rounds"] >= LOGIN_BAN_THRESHOLD:
                    record["ban_until"] = now + LOGIN_BAN_HOURS * 3600
                    record["rounds"] = 0
                    return {"blocked": True, "reason": f"多次登录失败，IP 已被封禁 {LOGIN_BAN_HOURS} 小时", "wait_seconds": LOGIN_BAN_HOURS * 3600}

    return {"blocked": False, "reason": "", "wait_seconds": 0}

def _record_login_fail(ip: str):
    """记录一次登录失败"""
    now = time.time()
    record = _login_attempts.get(ip)
    if not record:
        _login_attempts[ip] = {"attempts": 1, "first_fail": now, "ban_until": 0, "rounds": 0}
    else:
        if record["first_fail"] == 0:
            record["first_fail"] = now
        record["attempts"] += 1

def _record_login_success(ip: str):
    """登录成功后清除该 IP 的记录"""
    _login_attempts.pop(ip, None)

# 定期清理过期记录（防止内存泄漏）
_cleanup_interval = 3600  # 1小时
_last_cleanup = time.time()
def load_secret_key():
    import json
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_config.json')
    defaults = {"SECRET_KEY": "trulymem-secret-key-2026"}
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            file_config = json.load(f)
            if "SECRET_KEY" in file_config:
                defaults["SECRET_KEY"] = file_config["SECRET_KEY"]
    return defaults

WEB_CONFIG = load_secret_key()

_ui_dir = os.path.join(os.path.dirname(__file__), '..', 'ui')
app = Flask(__name__, static_folder=os.path.join(_ui_dir, 'static'), static_url_path='', template_folder=os.path.join(_ui_dir, 'templates'))
app.secret_key = WEB_CONFIG["SECRET_KEY"]
app.permanent_session_lifetime = timedelta(days=7)
CORS(app, supports_credentials=True)  # 启用跨域支持，支持 session cookies


def login_required(f):
    """登录验证装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """API 登录验证装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({"success": False, "error": "未登录"}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员权限验证装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username', '')
        g_db = get_global_db()
        if not g_db or not g_db.is_admin(username):
            return jsonify({"success": False, "error": "权限不足，需要管理员权限"}), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@login_required
def index():
    """返回星图页面（默认首页）"""
    return app.send_static_file('graph.html')


@app.route('/graph.html')
@login_required
def graph_html():
    """返回星图页面"""
    return app.send_static_file('graph.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """提供静态文件访问"""
    return app.send_static_file(filename)


@app.route('/chat')
@login_required
def chat():
    """返回聊天页面"""
    return app.send_static_file('index.html')

# 全局服务器和客户端实例
backend_server: BackendServer = None
backend_client: BackendClient = None
server_thread: threading.Thread = None
graph_db: EmbeddedGraphDB = None
global_db: EmbeddedGraphDB = None  # 全局数据库（用于用户管理）


def get_global_db():
    """获取全局数据库实例"""
    global global_db
    if global_db is None:
        global_db_path = os.path.join(os.path.expanduser("~"), ".trulymem", "trulymem.db")
        if os.path.exists(global_db_path):
            global_db = EmbeddedGraphDB(db_path=global_db_path)
    return global_db


def create_server(username: str = ""):
    """创建并启动 BackendServer 后台线程"""
    global backend_server, backend_client, server_thread, graph_db
    
    backend_server = BackendServer(username=username)
    backend_server.start()
    
    backend_client = BackendClient(backend_server)
    
    # 创建图数据库实例（连接用户的数据库文件）
    graph_db = EmbeddedGraphDB(db_path=backend_server._db_path)
    
    # 等待服务器初始化完成
    time.sleep(0.5)


def reload_server_for_user(username: str):
    """为指定用户重新加载服务器"""
    global backend_server, backend_client, graph_db
    
    # 关闭旧的服务器
    if backend_server:
        backend_server.shutdown()
    
    # 创建新的服务器（使用用户的数据库）
    create_server(username=username)


@app.route('/login')
def login_page():
    """登录页面 - 如果没有用户则重定向到设置页"""
    # 如果没有用户，重定向到首次设置页
    users_count = 0
    g_db = get_global_db()
    if g_db:
        users_count = g_db.get_web_users_count()
    elif graph_db:
        users_count = graph_db.get_web_users_count()
    if users_count == 0:
        return redirect('/setup')
    return render_template('login.html')


@app.route('/setup')
def setup_page():
    """首次设置页面 - 如果已有用户则跳转到登录页"""
    has_users = False
    g_db = get_global_db()
    if g_db:
        has_users = g_db.get_web_users_count() > 0
    elif graph_db:
        has_users = graph_db.get_web_users_count() > 0
    if has_users:
        return redirect('/login')
    return render_template('setup.html')


@app.route('/settings')
@api_login_required
def settings_page():
    """Web 设置页面"""
    return render_template('settings.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    """登录接口"""
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    # 登录限流检查
    ip = request.remote_addr
    limit_check = _check_login_limit(ip)
    if limit_check["blocked"]:
        return jsonify({"success": False, "error": limit_check["reason"]})
    
    # 从全局数据库验证
    g_db = get_global_db()
    if g_db and g_db.verify_web_user(username, password):
        session['authenticated'] = True
        session['username'] = username  # 存储用户名
        session.permanent = True
        
        # 重新加载服务器使用该用户的数据库
        reload_server_for_user(username)
        
        return jsonify({"success": True})
    
@app.route('/api/logout', methods=['POST'])
def api_logout():
    """登出接口"""
    session.clear()
    return jsonify({"success": True})


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """检查登录状态"""
    return jsonify({"authenticated": bool(session.get('authenticated'))})


@app.route('/api/userinfo', methods=['GET'])
def userinfo():
    """获取当前登录用户信息（含角色）"""
    if not session.get('authenticated'):
        return jsonify({"success": False, "error": "未登录"}), 401
    username = session.get('username', '')
    g_db = get_global_db()
    if not g_db:
        return jsonify({"success": False, "error": "数据库未初始化"}), 500
    user = g_db.get_web_user(username)
    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404
    return jsonify({
        "success": True,
        "username": user['username'],
        "role": user.get('role', 'user'),
        "is_admin": user.get('role') == 'admin',
        "created_at": user.get('created_at')
    })


@app.route('/api/web-check', methods=['GET'])
def web_check():
    """检查是否需要首次设置，返回是否配置完成"""
    users_count = 0
    if graph_db:
        users_count = graph_db.get_web_users_count()

    return jsonify({
        "needs_setup": users_count == 0,
        "users_count": users_count
    })


@app.route('/api/web-users', methods=['GET'])
@api_login_required
def web_users():
    """获取 web_users 列表"""
    if graph_db:
        users = graph_db.get_web_users()
        return jsonify({
            "success": True,
            "users": [
                {
                    "username": u['username'],
                    "role": u.get('role', 'user'),
                    "is_admin": u.get('role') == 'admin',
                    "created_at": u.get('created_at')
                }
                for u in users
            ]
        })
    return jsonify({"success": False, "error": "数据库未初始化"}), 500


@app.route('/api/web-user/<username>', methods=['GET'])
@api_login_required
def web_user_detail(username):
    """获取单个 web_user 详情"""
    if not graph_db:
        return jsonify({"success": False, "error": "数据库未初始化"}), 500
    user = graph_db.get_web_user(username)
    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404
    return jsonify({
        "success": True,
        "username": user['username'],
        "role": user.get('role', 'user'),
        "is_admin": user.get('role') == 'admin',
        "created_at": user.get('created_at')
    })


@app.route('/api/setup', methods=['POST'])
def api_setup():
    """首次设置 - 创建初始管理员用户"""
    # 只有没有任何用户时才允许设置
    g_db = get_global_db()
    if g_db and g_db.get_web_users_count() > 0:
        return jsonify({"success": False, "error": "用户已存在，不允许重复设置"}), 400

    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    confirm = data.get('confirm_password', '')

    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400

    if password != confirm:
        return jsonify({"success": False, "error": "两次密码输入不一致"}), 400

    if len(password) < 6:
        return jsonify({"success": False, "error": "密码长度至少 6 位"}), 400

    # 使用全局数据库创建用户
    if g_db is None:
        # 如果全局数据库不存在，创建它
        global_db_path = os.path.join(os.path.expanduser("~"), ".trulymem", "trulymem.db")
        g_db = EmbeddedGraphDB(db_path=global_db_path)
        global global_db
        global_db = g_db
    
    result = g_db.set_web_user(username, password)
    if result.get("success"):
        # 设置完成后自动登录
        session['authenticated'] = True
        session['username'] = username
        session.permanent = True
        return jsonify({"success": True, "message": "用户创建成功"})

    return jsonify({"success": False, "error": "创建用户失败"}), 500


@app.route('/api/change-password', methods=['POST'])
@api_login_required
def api_change_password():
    """修改 Web 登录密码"""
    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not new_password:
        return jsonify({"success": False, "error": "新密码不能为空"}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "error": "两次密码输入不一致"}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "error": "密码长度至少 6 位"}), 400

    # 获取当前登录用户
    current_username = session.get('username', '')
    if not current_username:
        return jsonify({"success": False, "error": "无法识别当前用户"}), 400

    # 验证当前密码（使用全局数据库）
    g_db = get_global_db()
    if not g_db or not g_db.verify_web_user(current_username, current_password):
        return jsonify({"success": False, "error": "当前密码错误"}), 400

    result = g_db.set_web_user(current_username, new_password)
    if result.get("success"):
        return jsonify({"success": True, "message": "密码已更新"})

    return jsonify({"success": False, "error": "修改密码失败"}), 500


# ========== 管理员 API ==========

@app.route('/api/admin/users', endpoint='api_admin_get_users', methods=['GET'])
@api_login_required
@admin_required
def api_admin_get_users():
    """获取用户列表"""
    g_db = get_global_db()
    if not g_db:
        return jsonify({"success": False, "error": "全局数据库未初始化"}), 500
    
    users = g_db.get_web_users()
    return jsonify({"success": True, "users": users})


@app.route('/api/admin/users', endpoint='api_admin_add_user', methods=['POST'])
@api_login_required
@admin_required
def api_admin_add_user():
    """管理员添加用户"""
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "error": "密码长度至少 6 位"}), 400
    
    g_db = get_global_db()
    if not g_db:
        return jsonify({"success": False, "error": "全局数据库未初始化"}), 500
    
    result = g_db.set_web_user(username, password)
    if result.get("success"):
        return jsonify({"success": True, "message": "用户添加成功", "user": result})
    
    return jsonify({"success": False, "error": "添加用户失败"}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@api_login_required
@admin_required
def api_admin_delete_user(user_id):
    """管理员删除用户"""
    g_db = get_global_db()
    if not g_db:
        return jsonify({"success": False, "error": "全局数据库未初始化"}), 500
    
    # 获取所有用户
    users = g_db.get_web_users()
    
    # 查找要删除的用户
    target_user = None
    for u in users:
        if u['id'] == user_id:
            target_user = u
            break
    
    if not target_user:
        return jsonify({"success": False, "error": "用户不存在"}), 404
    
    # 不能删除自己
    current_username = session.get('username', '')
    if target_user['username'] == current_username:
        return jsonify({"success": False, "error": "不能删除当前登录的用户"}), 400
    
    # 不能删除最后一个 admin
    admin_count = sum(1 for u in users if u.get('role') == 'admin')
    if target_user.get('role') == 'admin' and admin_count <= 1:
        return jsonify({"success": False, "error": "不能删除最后一个管理员"}), 400
    
    # 删除用户（保留文件目录）
    result = g_db.delete_web_user(target_user['username'])
    if not result.get('success'):
        return jsonify({"success": False, "error": result.get('error', '删除失败')}), 500
    
    return jsonify({"success": True, "message": "用户已删除"})


@app.route('/api/admin/migrate-check', methods=['GET'])
def api_admin_migrate_check():
    """检测系统是否需要迁移"""
    from core.migrate import need_migration, is_migrated
    
    return jsonify({
        "success": True,
        "need_migration": need_migration(),
        "is_migrated": is_migrated()
    })


@app.route('/api/admin/migrate', methods=['POST'])
def api_admin_migrate():
    """执行迁移+创建首个用户"""
    from core.migrate import need_migration, run_migration
    
    if not need_migration():
        return jsonify({"success": False, "error": "不需要迁移"}), 400
    
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "error": "密码长度至少 6 位"}), 400
    
    result = run_migration(username, password)
    
    if result.get("success"):
        # 自动登录
        session['authenticated'] = True
        session['username'] = username
        session.permanent = True
        
        # 重新加载服务器
        reload_server_for_user(username)
        
        return jsonify({"success": True, "message": "迁移完成", "data": result})
    
    return jsonify({"success": False, "error": result.get("error", "迁移失败")}), 500


@app.route('/api/settings/config', methods=['GET', 'POST', 'PUT'])
@api_login_required
def web_settings_config():
    """获取/更新当前登录用户的配置"""
    if request.method == 'GET':
        settings = {}
        if backend_client:
            result = backend_client.get_settings()
            settings = result.get("data", {}) if isinstance(result, dict) else result
            if isinstance(settings, dict):
                settings = settings.get("api_config", {}) if "api_config" in settings else settings
        # 从 settings 中提取相关字段
        return jsonify({
            "success": True,
            "enable_web": settings.get("enable_web", False),
            "web_port": settings.get("web_port", 4096),
            "enable_tui": settings.get("enable_tui", True),
        })

    # PUT/POST 更新
    data = request.get_json() or {}
    enable_tui = data.get('enable_tui')

    if enable_tui is not None and backend_client:
        # 获取当前配置，合并更新
        current = backend_client.get_settings()
        current_data = current.get("data", {}) if isinstance(current, dict) else {}

        tool_limits = current_data.get("tool_limits", {})
        api_config = current_data.get("api_config", {})
        api_config["enable_tui"] = bool(enable_tui)

        result = backend_client.update_settings(api_config, tool_limits)
        return jsonify({"success": True, "enable_tui": bool(enable_tui)})

    return jsonify({"success": False, "error": "没有需要更新的配置"}), 400


@app.errorhandler(404)
def not_found(e):
    """404 处理"""
    return jsonify({
        "success": False,
        "error": "404 Not Found"
    }), 404


@app.errorhandler(500)
def server_error(e):
    """500 处理"""
    return jsonify({
        "success": False,
        "error": str(e.original_exception if hasattr(e, 'original_exception') else e)
    }), 500


@app.route('/api/message', methods=['POST'])
@api_login_required
def process_message():
    """发送消息给 AI - PROCESS_MESSAGE"""
    data = request.get_json() or {}
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({
            "success": False,
            "error": "message 参数不能为空"
        }), 400
    
    result = backend_client.process_message(user_input)
    return jsonify(result)


@app.route('/api/tools/execute', methods=['POST'])
@api_login_required
def execute_tool():
    """直接执行工具 - EXECUTE_TOOL"""
    data = request.get_json() or {}
    tool_name = data.get('tool_name', '')
    arguments = data.get('arguments', {})
    
    if not tool_name:
        return jsonify({
            "success": False,
            "error": "tool_name 参数不能为空"
        }), 400
    
    result = backend_client.execute_tool(tool_name, arguments)
    return jsonify(result)


@app.route('/api/status', methods=['GET'])
@api_login_required
def get_status():
    """获取状态 - GET_STATUS"""
    result = backend_client.get_status()
    return jsonify(result)


@app.route('/api/settings', methods=['GET'])
@api_login_required
def get_settings():
    """获取配置 - GET_SETTINGS"""
    result = backend_client.get_settings()
    return jsonify(result)


@app.route('/api/settings', methods=['PUT'])
@api_login_required
def set_settings():
    """更新配置 - SET_SETTINGS"""
    data = request.get_json() or {}
    
    api_config = data.get('api_config', {})
    tool_limits = data.get('tool_limits', {})
    
    result = backend_client.update_settings(api_config, tool_limits)
    return jsonify(result)


@app.route('/api/history', methods=['GET'])
@api_login_required
def get_history():
    """获取历史 - GET_HISTORY"""
    result = backend_client.get_history()
    return jsonify({"success": True, "history": result})


@app.route('/api/history', methods=['DELETE'])
@api_login_required
def clear_history():
    """清空历史 - SAVE_HISTORY(空)"""
    result = backend_client.clear_history()
    return jsonify(result)


@app.route('/api/shutdown', methods=['POST'])
@api_login_required
def shutdown():
    """关闭服务器 - SHUTDOWN"""
    backend_client.shutdown()
    return jsonify({"success": True, "status": "shutdown"})


@app.route('/api/activity', methods=['GET'])
@api_login_required
def get_activity():
    """获取当前轮的数据库操作记录"""
    recorder = get_recorder()
    records = recorder.get_all()
    summary = recorder.get_summary()
    return jsonify({
        "success": True,
        "data": {
            "records": records,
            "summary": summary
        }
    })


@app.route('/api/graph', methods=['GET'])
@api_login_required
def get_graph():
    """返回全量图数据"""
    global graph_db
    
    if graph_db is None:
        return jsonify({
            "success": False,
            "error": "图数据库未初始化"
        }), 500

    cursor = graph_db.conn.cursor()
    
    # 查询实体（节点）
    cursor.execute("""
        SELECT id, name, type, mention_count
        FROM entities
        ORDER BY mention_count DESC
    """)
    
    nodes = []
    for row in cursor.fetchall():
        nodes.append({
            "id": row['id'],
            "name": row['name'],
            "type": str(row['type'] or 'unknown'),
            "mention_count": row['mention_count']
        })
    
    # 查询关系（边）
    cursor.execute("""
        SELECT r.id, r.source_id, r.target_id, r.relation_type, r.confidence, r.status
        FROM relations r
        WHERE r.status = 'active'
    """)
    
    edges = []
    for row in cursor.fetchall():
        edges.append({
            "id": row['id'],
            "source": row['source_id'],
            "target": row['target_id'],
            "relation_type": row['relation_type'],
            "confidence": row['confidence'],
            "status": row['status']
        })
    
    return jsonify({
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
    })


@app.route('/api/graph/highlight', methods=['GET'])
@api_login_required
def get_graph_highlight():
    """返回需要高亮的节点ID列表"""
    recorder = get_recorder()
    records = recorder.get_all()
    
    highlight_ids = []
    new_node_id = None
    new_edge = None
    
    if graph_db is None:
        return jsonify({
            "success": False,
            "data": {
                "highlight_ids": [],
                "new_node_id": None,
                "new_edge": None
            }
        })

    # 从最近的记录中提取实体ID
    for record in records[-10:]:  # 只看最近10条记录
        entity_name = record.get('entity', '')
        if entity_name:
            cursor = graph_db.conn.cursor()
            cursor.execute("SELECT id FROM entities WHERE name = ?", (entity_name,))
            row = cursor.fetchone()
            if row:
                highlight_ids.append(row['id'])
        
        # 除删除外，所有操作都拉镜头（create/recall/query/update/archive 等）
        if record.get('action') != 'delete' and entity_name:
            cursor = graph_db.conn.cursor()
            cursor.execute("SELECT id FROM entities WHERE name = ?", (entity_name,))
            row = cursor.fetchone()
            if row:
                new_node_id = row['id']
    
    # 检查是否有删除的节点
    deleted_node_ids = []
    for record in records[-10:]:
        if record.get('action') == 'delete':
            entity_name = record.get('entity', '')
            if entity_name:
                try:
                    cursor = graph_db.conn.cursor()
                    cursor.execute("SELECT id FROM entities WHERE name = ?", (entity_name,))
                    row = cursor.fetchone()
                    if row:
                        deleted_node_ids.append(row['id'])
                except Exception:
                    pass  # 实体可能已被删除，忽略错误
    
    # 去重
    highlight_ids = list(set(highlight_ids))
    deleted_node_ids = list(set(deleted_node_ids))
    
    return jsonify({
        "success": True,
        "highlight_ids": highlight_ids,
        "new_node_id": new_node_id,
        "new_edge": new_edge,
        "deleted_node_ids": deleted_node_ids
    })


# ── 可被 TUI 作为线程启动 ──────────────────────────────────────────────────

_web_thread: threading.Thread | None = None
_http_server = None  # werkzeug.serving.BaseWSGIServer 引用，用于优雅停止


def run_web_server(port: int = 4096, host: str = '0.0.0.0') -> None:
    """在后台线程启动 Flask，供 TUI 或入口脚本在进程中直接调用"""
    global backend_server, backend_client, _web_thread, _http_server

    if _http_server is not None:
        return  # 已在运行

    # 自动初始化后端（如果还没初始化的话）
    if backend_server is None:
        create_server()

    def _start():
        global _http_server
        try:
            from werkzeug.serving import make_server
            _http_server = make_server(host, port, app, threaded=True)
            print(f"Web API 服务启动在 http://{host}:{port}")
            _http_server.serve_forever()
        except Exception as e:
            print(f"Web 服务启动失败: {e}")
            _http_server = None
        finally:
            _http_server = None

    _web_thread = threading.Thread(target=_start, daemon=True)
    _web_thread.start()


def stop_web_server() -> None:
    """停止 Web 服务线程"""
    global _http_server, _web_thread
    if _http_server:
        try:
            _http_server.shutdown()
        except Exception:
            pass
        _http_server = None
    _web_thread = None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TrulyMEM Web API 服务')
    parser.add_argument('--port', type=int, default=5000, help='服务端口 (默认: 5000)')
    
    args = parser.parse_args()
    
    # 启动后端服务器
    print("正在启动 BackendServer...")
    create_server()
    print("BackendServer 已启动")
    
    # 启动 Flask 应用
    print(f"Web API 服务启动在 http://0.0.0.0:{args.port}")
    app.run(host='0.0.0.0', port=args.port, debug=False)
