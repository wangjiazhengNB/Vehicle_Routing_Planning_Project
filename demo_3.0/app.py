"""应用入口文件"""

from flask import Flask
from flask_cors import CORS
from functools import wraps

from src.api.routes import api_bp
from src.api.auth_routes import auth_bp
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
app.register_blueprint(auth_bp)


# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, redirect

        # 检查 cookie 中的 token
        token = request.cookies.get('auth_token')

        if not token:
            # 没有 token，重定向到登录页
            return redirect('/auth?next=' + request.path)

        # 验证 token
        from src.services.auth_service import AuthService
        success, message, user_data = AuthService.verify_token(token)

        if not success:
            # token 无效，重定向到登录页
            return redirect('/auth?next=' + request.path)

        # token 有效，将用户信息添加到请求上下文
        request.current_user = user_data
        return f(*args, **kwargs)

    return decorated_function


# 首页路由（展示页面）
@app.route('/')
def index():
    from flask import render_template
    return render_template('landing.html')


# 路径规划应用路由（需要登录）
@app.route('/app')
@login_required
def app_page():
    from flask import render_template
    return render_template('index.html')


# 登录/注册页面路由
@app.route('/auth')
def auth():
    from flask import render_template, request
    next_page = request.args.get('next', '/app')
    return render_template('auth.html', next_page=next_page)


# 规划结果页面路由
@app.route('/result')
@login_required
def result_page():
    from flask import render_template
    return render_template('result.html')


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