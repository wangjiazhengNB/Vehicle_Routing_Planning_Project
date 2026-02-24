"""认证API路由模块"""

from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Callable

from ..services.auth_service import AuthService
from ..utils.auth import JWTManager


# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def token_required(f: Callable) -> Callable:
    """
    JWT令牌验证装饰器

    保护需要登录才能访问的API端点
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取令牌
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'success': False,
                'error': '缺少认证令牌'
            }), 401

        # 支持 Bearer token 格式
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header

        # 验证令牌
        success, message, user_data = AuthService.verify_token(token)
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 401

        # 将用户信息添加到请求上下文
        request.current_user = user_data
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册

    请求体:
    {
        "username": "用户名",
        "password": "密码",
        "email": "邮箱（可选）",
        "phone": "手机号（可选）"
    }

    返回:
    {
        "success": true,
        "message": "注册成功",
        "data": {
            "user": {...},
            "access_token": "..."
        }
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')

        # 验证必需参数
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400

        # 调用注册服务
        success, message, result = AuthService.register_user(username, password, email, phone)

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录

    请求体:
    {
        "login_field": "用户名/邮箱/手机号",
        "password": "密码"
    }

    返回:
    {
        "success": true,
        "message": "登录成功",
        "data": {
            "user": {...},
            "access_token": "..."
        }
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        login_field = data.get('login_field')
        password = data.get('password')

        # 验证必需参数
        if not login_field or not password:
            return jsonify({
                'success': False,
                'error': '账号和密码不能为空'
            }), 400

        # 调用登录服务
        success, message, result = AuthService.login_user(login_field, password)

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    用户登出

    返回:
    {
        "success": true,
        "message": "登出成功"
    }

    注意: JWT是无状态的，登出主要在前端处理（删除令牌）
    """
    return jsonify({
        'success': True,
        'message': '登出成功'
    })


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    获取当前登录用户信息

    请求头:
    Authorization: Bearer <token>

    返回:
    {
        "success": true,
        "data": {...}
    }
    """
    return jsonify({
        'success': True,
        'data': request.current_user
    })


@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """
    验证令牌

    请求体:
    {
        "token": "JWT令牌"
    }

    返回:
    {
        "success": true,
        "data": {...}
    }
    """
    try:
        data = request.get_json()

        if not data or not data.get('token'):
            return jsonify({
                'success': False,
                'error': '令牌不能为空'
            }), 400

        token = data.get('token')
        success, message, user_data = AuthService.verify_token(token)

        if success:
            return jsonify({
                'success': True,
                'data': user_data
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@auth_bp.route('/password/reset/request', methods=['POST'])
def request_password_reset():
    """
    请求密码重置

    请求体:
    {
        "contact": "邮箱或手机号"
    }

    返回:
    {
        "success": true,
        "message": "重置链接已发送"
    }
    """
    try:
        data = request.get_json()

        if not data or not data.get('contact'):
            return jsonify({
                'success': False,
                'error': '请提供邮箱或手机号'
            }), 400

        contact = data.get('contact')
        success, message = AuthService.request_password_reset(contact)

        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@auth_bp.route('/password/reset', methods=['POST'])
def reset_password():
    """
    重置密码

    请求体:
    {
        "token": "重置令牌",
        "new_password": "新密码"
    }

    返回:
    {
        "success": true,
        "message": "密码重置成功"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        token = data.get('token')
        new_password = data.get('new_password')

        if not token or not new_password:
            return jsonify({
                'success': False,
                'error': '令牌和新密码不能为空'
            }), 400

        success, message = AuthService.reset_password(token, new_password)

        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500
