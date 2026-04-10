"""
Web接口 - 提供浏览器访问
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
from typing import Optional

from ..core.embedded_db import EmbeddedGraphDB
from ..models.config import AppConfig


class WebInterface:
    """Web接口服务"""
    
    def __init__(self, config: AppConfig, db: EmbeddedGraphDB, port: int = 5000):
        self.config = config
        self.db = db
        self.port = port
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        CORS(self.app)
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            data = request.json
            message = data.get('message', '')
            # 简单响应，实际应集成完整的聊天逻辑
            return jsonify({
                'response': f'收到消息: {message}\n\n请使用TUI界面获得完整功能。',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/memory/recall', methods=['POST'])
        def recall():
            data = request.json
            result = self.db.recall(
                query_intent=data.get('query_intent', ''),
                seed_entities=data.get('seed_entities'),
                depth=data.get('depth', 2)
            )
            return jsonify(result)
        
        @self.app.route('/api/memory/commit', methods=['POST'])
        def commit():
            data = request.json
            result = self.db.commit(
                triplets=data.get('triplets', []),
                entity_types=data.get('entity_types'),
                session_id=data.get('session_id'),
                turn_id=data.get('turn_id')
            )
            return jsonify(result)
        
        @self.app.route('/api/memory/introspect', methods=['GET'])
        def introspect():
            result = self.db.introspect()
            return jsonify(result)
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            return jsonify({
                'api_key': self.config.api_key[:10] + '...' if self.config.api_key else '',
                'model': self.config.model,
                'base_url': self.config.base_url
            })
        
        @self.app.route('/api/config', methods=['POST'])
        def save_config():
            data = request.json
            self.config.api_key = data.get('api_key', '')
            self.config.model = data.get('model', 'deepseek-chat')
            self.config.base_url = data.get('base_url', 'https://api.deepseek.com')
            return jsonify({'status': 'ok', 'message': 'Configuration saved'})
    
    def run(self):
        """启动Web服务"""
        print(f"Web interface running at http://localhost:{self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
    
    def run_async(self):
        """异步启动Web服务"""
        import threading
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
