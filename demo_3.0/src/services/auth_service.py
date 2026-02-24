"""认证服务模块"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session

from ..config.database import get_session
from ..models.user import User, PasswordReset
from ..utils.auth import PasswordManager, JWTManager, ValidationHelper


class AuthService:
    """认证服务类"""

    @staticmethod
    def register_user(
        username: str,
        password: str,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        注册新用户

        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
            phone: 手机号（可选）

        Returns:
            (成功状态, 消息, 用户数据/令牌)
        """
        # 验证用户名
        valid, msg = ValidationHelper.validate_username(username)
        if not valid:
            return False, msg, None

        # 验证密码
        valid, msg = ValidationHelper.validate_password(password)
        if not valid:
            return False, msg, None

        # 验证邮箱
        if email:
            if not ValidationHelper.validate_email(email):
                return False, "邮箱格式不正确", None

        # 验证手机号
        if phone:
            if not ValidationHelper.validate_phone(phone):
                return False, "手机号格式不正确", None

        # 至少需要邮箱或手机号之一
        if not email and not phone:
            return False, "请至少提供邮箱或手机号", None

        db: Session = get_session()
        try:
            # 检查用户名是否已存在
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                return False, "用户名已存在", None

            # 检查邮箱是否已存在
            if email:
                existing_email = db.query(User).filter(User.email == email).first()
                if existing_email:
                    return False, "邮箱已被注册", None

            # 检查手机号是否已存在
            if phone:
                existing_phone = db.query(User).filter(User.phone == phone).first()
                if existing_phone:
                    return False, "手机号已被注册", None

            # 加密密码
            hashed_password, salt = PasswordManager.hash_password(password)
            stored_password = f"{hashed_password}:{salt}"

            # 创建新用户
            new_user = User(
                username=username,
                password=stored_password,
                email=email,
                phone=phone,
                is_active=True,
                is_verified=False  # 需要验证
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            # 生成JWT令牌
            token_data = {
                'user_id': new_user.id,
                'username': new_user.username
            }
            access_token = JWTManager.create_access_token(token_data)

            return True, "注册成功", {
                'user': new_user.to_dict(),
                'access_token': access_token
            }

        except Exception as e:
            db.rollback()
            return False, f"注册失败: {str(e)}", None
        finally:
            db.close()

    @staticmethod
    def login_user(login_field: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        用户登录（支持用户名/邮箱/手机号登录）

        Args:
            login_field: 登录字段（用户名/邮箱/手机号）
            password: 密码

        Returns:
            (成功状态, 消息, 用户数据/令牌)
        """
        db: Session = get_session()
        try:
            # 查找用户（支持用户名、邮箱、手机号）
            user = db.query(User).filter(
                (User.username == login_field) |
                (User.email == login_field) |
                (User.phone == login_field)
            ).first()

            if not user:
                return False, "用户不存在", None

            if not user.is_active:
                return False, "账户已被禁用", None

            # 验证密码
            stored_password = user.password
            if ':' not in stored_password:
                return False, "密码格式错误", None

            hashed_password, salt = stored_password.split(':')

            if not PasswordManager.verify_password(password, hashed_password, salt):
                return False, "密码错误", None

            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            db.commit()

            # 生成JWT令牌
            token_data = {
                'user_id': user.id,
                'username': user.username
            }
            access_token = JWTManager.create_access_token(token_data)

            return True, "登录成功", {
                'user': user.to_dict(),
                'access_token': access_token
            }

        except Exception as e:
            return False, f"登录失败: {str(e)}", None
        finally:
            db.close()

    @staticmethod
    def verify_token(token: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        验证JWT令牌

        Args:
            token: JWT令牌

        Returns:
            (成功状态, 消息, 用户数据)
        """
        payload = JWTManager.verify_token(token)
        if not payload:
            return False, "令牌无效或已过期", None

        user_id = payload.get('user_id')
        if not user_id:
            return False, "令牌格式错误", None

        db: Session = get_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在", None

            if not user.is_active:
                return False, "账户已被禁用", None

            return True, "验证成功", user.to_dict()

        except Exception as e:
            return False, f"验证失败: {str(e)}", None
        finally:
            db.close()

    @staticmethod
    def request_password_reset(contact: str) -> Tuple[bool, str]:
        """
        请求密码重置

        Args:
            contact: 联系方式（邮箱或手机号）

        Returns:
            (成功状态, 消息)
        """
        db: Session = get_session()
        try:
            # 查找用户
            is_email = ValidationHelper.validate_email(contact)
            is_phone = ValidationHelper.validate_phone(contact)

            if not is_email and not is_phone:
                return False, "请输入有效的邮箱或手机号"

            user = db.query(User).filter(
                (User.email == contact) | (User.phone == contact)
            ).first()

            if not user:
                # 为了安全，不透露用户是否存在
                return True, "如果该账号存在，将收到重置链接"

            # 生成重置令牌
            reset_token = PasswordManager.generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)  # 1小时后过期

            # 保存重置记录
            reset_record = PasswordReset(
                email=user.email or contact if is_email else None,
                phone=user.phone or contact if is_phone else None,
                token=reset_token,
                expires_at=expires_at
            )

            db.add(reset_record)
            db.commit()

            # TODO: 发送邮件或短信
            # 这里应该集成邮件/短信服务
            print(f"重置令牌: {reset_token}")  # 开发环境打印到控制台

            return True, "重置链接已发送到您的邮箱/手机"

        except Exception as e:
            db.rollback()
            return False, f"请求失败: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def reset_password(token: str, new_password: str) -> Tuple[bool, str]:
        """
        重置密码

        Args:
            token: 重置令牌
            new_password: 新密码

        Returns:
            (成功状态, 消息)
        """
        # 验证密码
        valid, msg = ValidationHelper.validate_password(new_password)
        if not valid:
            return False, msg

        db: Session = get_session()
        try:
            # 查找重置记录
            reset_record = db.query(PasswordReset).filter(
                PasswordReset.token == token,
                PasswordReset.used == False
            ).first()

            if not reset_record:
                return False, "重置链接无效或已过期"

            # 检查是否过期
            if reset_record.expires_at < datetime.utcnow():
                return False, "重置链接已过期"

            # 查找用户
            user = db.query(User).filter(
                (User.email == reset_record.email) |
                (User.phone == reset_record.phone)
            ).first()

            if not user:
                return False, "用户不存在"

            # 更新密码
            hashed_password, salt = PasswordManager.hash_password(new_password)
            user.password = f"{hashed_password}:{salt}"

            # 标记令牌已使用
            reset_record.used = True

            db.commit()

            return True, "密码重置成功"

        except Exception as e:
            db.rollback()
            return False, f"重置失败: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def get_user_info(user_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            (成功状态, 消息, 用户数据)
        """
        db: Session = get_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在", None

            return True, "获取成功", user.to_dict()

        except Exception as e:
            return False, f"获取失败: {str(e)}", None
        finally:
            db.close()
