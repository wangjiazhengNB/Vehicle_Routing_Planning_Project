"""地址缓存模型"""

from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.dialects.mysql import TIMESTAMP
from datetime import datetime
from src.config.database import Base


class AddressCache(Base):
    """地址缓存表模型"""

    __tablename__ = 'address_cache'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    address = Column(String(200), unique=True, nullable=False, comment='地址')
    lng = Column(Numeric(10, 7), nullable=False, comment='经度')
    lat = Column(Numeric(10, 7), nullable=False, comment='纬度')
    poi_name = Column(String(200), comment='POI名称')
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'address': self.address,
            'lng': float(self.lng),
            'lat': float(self.lat),
            'poi_name': self.poi_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_tuple(self):
        """转换为元组 (lng, lat, poi_name)"""
        return (float(self.lng), float(self.lat), self.poi_name or self.address)

    def __repr__(self):
        return (f"<AddressCache(id={self.id}, "
                f"address={self.address}, "
                f"coords={self.lng},{self.lat})>")
