#!/usr/bin/env python3
"""
跨平台一键启动脚本 - 支持多语言
自动启动 Docker (WSL/Desktop)、Neo4j、安装依赖、启动应用
"""

import subprocess
import sys
import time
import platform
import os
import locale
from pathlib import Path


# 多语言支持
LANGUAGES = {
    'zh_CN': {
        'title': 'Graph Memory TUI - 一键启动',
        'step': '步骤',
        'checking_docker': '检查 Docker...',
        'docker_not_found': 'Docker 未找到，尝试启动...',
        'starting_docker_wsl': '通过 WSL 启动 Docker...',
        'starting_docker_desktop': '启动 Docker Desktop...',
        'waiting_docker': '等待 Docker 启动...',
        'still_waiting': '仍在等待... ({current}/{timeout})',
        'docker_started': 'Docker 启动成功',
        'docker_is_running': 'Docker 正在运行',
        'docker_failed': 'Docker 启动失败！',
        'install_docker': '请安装 Docker: https://docs.docker.com/get-docker/',
        'starting_neo4j': '启动 Neo4j 数据库...',
        'creating_neo4j': '创建 Neo4j 容器...',
        'neo4j_created': 'Neo4j 容器已创建',
        'neo4j_started': 'Neo4j 容器已启动',
        'neo4j_running': 'Neo4j 容器已在运行',
        'waiting_neo4j': '等待 Neo4j 就绪...',
        'neo4j_failed': 'Neo4j 启动失败！',
        'checking_python': '检查 Python...',
        'python_found': 'Python 已找到',
        'setting_venv': '设置虚拟环境...',
        'creating_venv': '创建虚拟环境...',
        'venv_created': '虚拟环境已创建',
        'venv_exists': '虚拟环境已存在',
        'installing_deps': '安装依赖包...',
        'deps_installed': '依赖包已安装',
        'deps_exist': '依赖包已安装',
        'deps_failed': '依赖包安装失败！',
        'starting_app': '启动应用...',
        'all_ready': '所有系统就绪！',
        'neo4j_connection': 'Neo4j 连接信息:',
        'browser': '浏览器',
        'user': '用户名',
        'pass': '密码',
        'app_closed': '应用已关闭',
        'error': '错误',
        'interrupted': '用户中断',
    },
    'en_US': {
        'title': 'Graph Memory TUI - One-Click Start',
        'step': 'Step',
        'checking_docker': 'Checking Docker...',
        'docker_not_found': 'Docker not found, trying to start...',
        'starting_docker_wsl': 'Starting Docker via WSL...',
        'starting_docker_desktop': 'Starting Docker Desktop...',
        'waiting_docker': 'Waiting for Docker to start...',
        'still_waiting': 'Still waiting... ({current}/{timeout})',
        'docker_started': 'Docker started successfully',
        'docker_is_running': 'Docker is running',
        'docker_failed': 'Docker failed to start!',
        'install_docker': 'Please install Docker: https://docs.docker.com/get-docker/',
        'starting_neo4j': 'Starting Neo4j database...',
        'creating_neo4j': 'Creating Neo4j container...',
        'neo4j_created': 'Neo4j container created',
        'neo4j_started': 'Neo4j container started',
        'neo4j_running': 'Neo4j container already running',
        'waiting_neo4j': 'Waiting for Neo4j to be ready...',
        'neo4j_failed': 'Neo4j failed to start!',
        'checking_python': 'Checking Python...',
        'python_found': 'Python found',
        'setting_venv': 'Setting up virtual environment...',
        'creating_venv': 'Creating virtual environment...',
        'venv_created': 'Virtual environment created',
        'venv_exists': 'Virtual environment exists',
        'installing_deps': 'Installing dependencies...',
        'deps_installed': 'Dependencies installed',
        'deps_exist': 'Dependencies already installed',
        'deps_failed': 'Failed to install dependencies!',
        'starting_app': 'Starting application...',
        'all_ready': 'All systems ready!',
        'neo4j_connection': 'Neo4j Connection:',
        'browser': 'Browser',
        'user': 'User',
        'pass': 'Password',
        'app_closed': 'Application closed',
        'error': 'Error',
        'interrupted': 'Interrupted by user',
    }
}


def get_language():
    """获取系统语言"""
    try:
        # 尝试获取系统语言
        lang = locale.getdefaultlocale()[0]
        
        if lang and lang.startswith('zh'):
            return 'zh_CN'
        else:
            return 'en_US'
    except:
        return 'en_US'


# 全局语言设置
LANG = get_language()
TEXT = LANGUAGES[LANG]


def run_command(cmd, check=True, capture_output=True):
    """运行命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def print_step(step, total, message):
    """打印步骤信息"""
    print(f"\n[{TEXT['step']} {step}/{total}] {message}")


def print_ok(message):
    """打印成功信息"""
    print(f"[OK] {message}")


def print_error(message):
    """打印错误信息"""
    print(f"[ERROR] {message}")


def print_info(message):
    """打印信息"""
    print(f"[INFO] {message}")


def check_docker():
    """检查Docker"""
    success, _, _ = run_command("docker --version", check=False)
    return success


def start_docker_wsl():
    """通过WSL启动Docker"""
    print_info(TEXT['starting_docker_wsl'])
    
    # 检查WSL是否安装
    success, _, _ = run_command("wsl --list", check=False)
    if not success:
        return False
    
    # 启动WSL中的Docker
    success, _, _ = run_command("wsl -d docker-desktop", check=False)
    if success:
        return True
    
    # 尝试启动docker服务
    success, _, _ = run_command("wsl sudo service docker start", check=False)
    return success


def start_docker_desktop():
    """启动Docker Desktop"""
    print_info(TEXT['starting_docker_desktop'])
    
    docker_paths = [
        r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
        r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe",
    ]
    
    for path in docker_paths:
        if os.path.exists(path):
            subprocess.Popen([path], shell=True)
            return True
    
    return False


def start_docker():
    """启动Docker"""
    system = platform.system()
    
    if system == "Windows":
        # Windows: 优先尝试WSL
        print_info(TEXT['docker_not_found'])
        
        # 检查WSL是否可用
        success, _, _ = run_command("wsl --list", check=False)
        
        if success:
            # 使用WSL启动Docker
            if start_docker_wsl():
                return True
        
        # WSL不可用，尝试Docker Desktop
        if start_docker_desktop():
            return True
        
        return False
    
    elif system == "Darwin":
        # macOS: 启动 Docker
        print_info(TEXT['starting_docker_desktop'])
        subprocess.Popen(["open", "-a", "Docker"])
        return True
    
    else:
        # Linux: 启动 Docker daemon
        print_info(TEXT['starting_docker_desktop'])
        success, _, _ = run_command("sudo systemctl start docker", check=False)
        return success


def wait_for_docker(timeout=60):
    """等待Docker启动"""
    print_info(TEXT['waiting_docker'])
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        success, _, _ = run_command("docker info", check=False)
        if success:
            return True
        time.sleep(2)
        elapsed = int(time.time() - start_time)
        print(f"  {TEXT['still_waiting'].format(current=elapsed, timeout=timeout)}")
    
    return False


def start_neo4j():
    """启动Neo4j"""
    # 检查容器是否存在
    success, output, _ = run_command("docker ps -a | grep neo4j", check=False)
    
    if not success:
        # 创建新容器
        print_info(TEXT['creating_neo4j'])
        cmd = """docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
                 -e NEO4J_AUTH=neo4j/graphmemory123 \
                 -e NEO4J_PLUGINS='["apoc"]' neo4j:latest"""
        success, _, _ = run_command(cmd, check=False)
        
        if not success:
            return False
        print_ok(TEXT['neo4j_created'])
    else:
        # 检查是否运行
        success, _, _ = run_command("docker ps | grep neo4j", check=False)
        
        if not success:
            # 启动容器
            print_info(TEXT['starting_neo4j'])
            success, _, _ = run_command("docker start neo4j", check=False)
            
            if not success:
                return False
            print_ok(TEXT['neo4j_started'])
        else:
            print_ok(TEXT['neo4j_running'])
    
    # 等待Neo4j就绪
    print_info(TEXT['waiting_neo4j'])
    time.sleep(5)
    
    return True


def setup_venv():
    """设置虚拟环境"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print_info(TEXT['creating_venv'])
        success, _, _ = run_command(f"{sys.executable} -m venv venv", check=False)
        
        if not success:
            return False
        print_ok(TEXT['venv_created'])
    else:
        print_ok(TEXT['venv_exists'])
    
    # 激活虚拟环境
    system = platform.system()
    
    if system == "Windows":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # 检查依赖
    success, _, _ = run_command(f"{pip_path} show textual", check=False)
    
    if not success:
        print_info(TEXT['installing_deps'])
        success, _, _ = run_command(f"{pip_path} install -r requirements.txt", check=False)
        
        if not success:
            return False
        print_ok(TEXT['deps_installed'])
    else:
        print_ok(TEXT['deps_exist'])
    
    return True


def start_app():
    """启动应用"""
    system = platform.system()
    
    if system == "Windows":
        python_path = Path("venv/Scripts/python")
    else:
        python_path = Path("venv/bin/python")
    
    print_info(TEXT['starting_app'])
    
    # 直接运行，不捕获输出
    subprocess.run([str(python_path), "-m", "graph_memory_tui.main"])


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print(f"  {TEXT['title']}")
    print("=" * 50 + "\n")
    
    total_steps = 5
    
    # Step 1: Docker
    print_step(1, total_steps, TEXT['checking_docker'])
    
    if not check_docker():
        if not start_docker():
            print_error(TEXT['docker_failed'])
            print(TEXT['install_docker'])
            sys.exit(1)
        
        if not wait_for_docker():
            print_error(TEXT['docker_failed'])
            sys.exit(1)
        
        print_ok(TEXT['docker_started'])
    else:
        # 检查Docker daemon是否运行
        success, _, _ = run_command("docker info", check=False)
        
        if not success:
            if not start_docker():
                print_error(TEXT['docker_failed'])
                sys.exit(1)
            
            if not wait_for_docker():
                print_error(TEXT['docker_failed'])
                sys.exit(1)
        
        print_ok(TEXT['docker_is_running'])
    
    # Step 2: Neo4j
    print_step(2, total_steps, TEXT['starting_neo4j'])
    
    if not start_neo4j():
        print_error(TEXT['neo4j_failed'])
        sys.exit(1)
    
    # Step 3: Python
    print_step(3, total_steps, TEXT['checking_python'])
    print_ok(f"{TEXT['python_found']} {sys.version.split()[0]}")
    
    # Step 4: Virtual Environment
    print_step(4, total_steps, TEXT['setting_venv'])
    
    if not setup_venv():
        print_error(TEXT['deps_failed'])
        sys.exit(1)
    
    # Step 5: Start Application
    print_step(5, total_steps, TEXT['starting_app'])
    
    print("\n" + "=" * 50)
    print(f"  {TEXT['all_ready']}")
    print("=" * 50)
    print(f"\n{TEXT['neo4j_connection']}")
    print(f"  - {TEXT['browser']}: http://localhost:7474")
    print("  - Bolt:    bolt://localhost:7687")
    print(f"  - {TEXT['user']}:    neo4j")
    print(f"  - {TEXT['pass']}: graphmemory123")
    print(f"\n{TEXT['starting_app']}\n")
    
    start_app()
    
    print(f"\n{TEXT['app_closed']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{TEXT['interrupted']}")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {TEXT['error']}: {e}")
        sys.exit(1)
