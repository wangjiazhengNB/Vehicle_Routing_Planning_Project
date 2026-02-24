"""认证工具模块"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional


class PasswordManager:
    """密码管理工具"""

    # 使用 SHA-256 + salt 的方式加密密码
    SALT_LENGTH = 32

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        对密码进行哈希加密

        Args:
            password: 原始密码
            salt: 盐值（可选，不提供则生成新的）

        Returns:
            (hashed_password, salt): 加密后的密码和盐值
        """
        if salt is None:
            salt = secrets.token_hex(PasswordManager.SALT_LENGTH)

        # 使用 SHA-256 + salt 进行加密
        password_salt = (password + salt).encode('utf-8')
        hashed = hashlib.sha256(password_salt).hexdigest()

        return hashed, salt

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        验证密码是否正确

        Args:
            password: 原始密码
            hashed_password: 加密后的密码
            salt: 盐值

        Returns:
            密码是否正确
        """
        new_hash, _ = PasswordManager.hash_password(password, salt)
        return new_hash == hashed_password

    @staticmethod
    def generate_reset_token() -> str:
        """
        生成密码重置令牌

        Returns:
            重置令牌
        """
        return secrets.token_urlsafe(32)


class JWTManager:
    """JWT令牌管理工具"""

    # JWT 配置
    SECRET_KEY = "your-secret-key-change-this-in-production"  # 生产环境需要更改
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌

        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量

        Returns:
            JWT令牌
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWTManager.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            'exp': expire,
            'iat': datetime.utcnow()
        })

        encoded_jwt = jwt.encode(to_encode, JWTManager.SECRET_KEY, algorithm=JWTManager.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        解码JWT令牌

        Args:
            token: JWT令牌

        Returns:
            解码后的数据，如果令牌无效则返回None
        """
        try:
            payload = jwt.decode(token, JWTManager.SECRET_KEY, algorithms=[JWTManager.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """
        验证JWT令牌

        Args:
            token: JWT令牌

        Returns:
            用户信息，如果令牌无效则返回None
        """
        payload = JWTManager.decode_token(token)
        if payload and 'user_id' in payload:
            return payload
        return None


class ValidationHelper:
    """输入验证工具"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        验证邮箱格式

        Args:
            email: 邮箱地址

        Returns:
            是否有效
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        验证手机号格式（中国大陆）

        Args:
            phone: 手机号

        Returns:
            是否有效
        """
        import re
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        验证密码强度

        Args:
            password: 密码

        Returns:
            (是否有效, 错误信息)
        """
        if len(password) < 6:
            return False, "密码长度不能少于6位"

        if len(password) > 50:
            return False, "密码长度不能超过50位"

        return True, ""

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        验证用户名

        Args:
            username: 用户名

        Returns:
            (是否有效, 错误信息)
        """
        # 长度按字符数计算（中文算1个字符）
        if len(username) < 2:
            return False, "用户名长度不能少于2个字符"

        if len(username) > 20:
            return False, "用户名长度不能超过20个字符"

        import re
        # 允许中文、字母、数字、下划线、连字符
        pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_-]+$'
        if not re.match(pattern, username):
            return False, "用户名只能包含中文、字母、数字、下划线和连字符"

        # 检查是否全是特殊字符（至少需要一个字母或数字或中文）
        has_valid_char = re.search(r'[\u4e00-\u9fa5a-zA-Z0-9]', username)
        if not has_valid_char:
            return False, "用户名至少需要一个中文、字母或数字"

        return True, ""
