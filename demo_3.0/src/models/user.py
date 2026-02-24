"""用户模型"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from src.config.database import Base


class User(Base):
    """用户表模型"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    password = Column(String(255), nullable=False, comment='密码（哈希后）')
    email = Column(String(100), unique=True, nullable=True, comment='邮箱')
    phone = Column(String(20), unique=True, nullable=True, comment='手机号')
    is_active = Column(Boolean, default=True, comment='是否激活')
    is_verified = Column(Boolean, default=False, comment='是否已验证')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    last_login = Column(DateTime, nullable=True, comment='最后登录时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return (f"<User(id={self.id}, "
                f"username={self.username}, "
                f"email={self.email}, "
                f"phone={self.phone})>")


class PasswordReset(Base):
    """密码重置令牌表"""

    __tablename__ = 'password_resets'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    email = Column(String(100), nullable=False, comment='邮箱')
    phone = Column(String(20), nullable=True, comment='手机号')
    token = Column(String(255), unique=True, nullable=False, comment='重置令牌')
    expires_at = Column(DateTime, nullable=False, comment='过期时间')
    used = Column(Boolean, default=False, comment='是否已使用')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'email': self.email,
            'phone': self.phone,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used': self.used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return (f"<PasswordReset(id={self.id}, "
                f"email={self.email}, "
                f"used={self.used})>")
