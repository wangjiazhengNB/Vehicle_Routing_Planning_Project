"""应用入口文件"""

from flask import Flask
from flask_cors import CORS

from src.api.routes import api_bp
from src.config.settings import get_config

# 获取配置
config = get_config()

# 创建Flask应用
app = Flask(__name__, template_folder='templates', static_folder='static')

# UTF-8编码配置（修复中文地址编码问题）
app.config['JSON_AS_ASCII'] = False
app.config['JSON_ENSURE_ASCII'] = False

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
    版本: {config.app_version}
    访问地址: http://{config.host}:{config.port}
    ================================================
    """)

    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug
    )