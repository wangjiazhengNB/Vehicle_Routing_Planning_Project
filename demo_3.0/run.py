"""应用入口文件"""

import os
import sys
from flask import Flask
from flask_cors import CORS

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 添加 src 目录到路径
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.api.routes import api_bp
from src.config.settings import get_config

# 获取配置
config = get_config()

# 创建Flask应用
app = Flask(__name__,
           template_folder=os.path.join(project_root, 'templates'),
           static_folder=os.path.join(project_root, 'static'))

# CORS配置
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

# 注册蓝图
app.register_blueprint(api_bp)

# 主页面路由
@app.route('/')
def index():
    from flask import render_template
    return render_template('index.html')


if __name__ == '__main__':
    print(f"""
    ================================================
    车辆路径规划系统 - Demo 3.0
    ================================================
    应用名称: {config.app_name}
    版本: {config.app_version} - Demo 3.0
    访问地址: http://{config.host}:{config.port}
    ================================================
    """)

    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug
    )
