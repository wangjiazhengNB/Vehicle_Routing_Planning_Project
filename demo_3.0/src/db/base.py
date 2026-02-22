"""数据库基类模块"""

from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session

from ..config.database import get_session

ModelType = TypeVar("ModelType")


class BaseDAO(Generic[ModelType]):
    """数据访问对象基类"""

    def __init__(self, model: Type[ModelType]):
        """
        初始化DAO

        Args:
            model: SQLAlchemy模型类
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        根据ID获取单个记录

        Args:
            db: 数据库会话
            id: 记录ID

        Returns:
            模型实例或None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        获取所有记录（支持分页）

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            模型实例列表
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> ModelType:
        """
        创建新记录

        Args:
            db: 数据库会话
            obj_in: 创建数据的字典

        Returns:
            创建的模型实例
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        """
        更新记录

        Args:
            db: 数据库会话
            db_obj: 要更新的模型实例
            obj_in: 更新数据的字典

        Returns:
            更新后的模型实例
        """
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """
        删除记录

        Args:
            db: 数据库会话
            id: 记录ID

        Returns:
            是否删除成功
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def count(self, db: Session) -> int:
        """
        统计记录数

        Args:
            db: 数据库会话

        Returns:
            记录总数
        """
        return db.query(self.model).count()

    def filter_by(self, db: Session, **kwargs) -> List[ModelType]:
        """
        根据条件过滤记录

        Args:
            db: 数据库会话
            **kwargs: 过滤条件

        Returns:
            模型实例列表
        """
        return db.query(self.model).filter_by(**kwargs).all()

    def filter_one(self, db: Session, **kwargs) -> Optional[ModelType]:
        """
        根据条件获取单个记录

        Args:
            db: 数据库会话
            **kwargs: 过滤条件

        Returns:
            模型实例或None
        """
        return db.query(self.model).filter_by(**kwargs).first()
