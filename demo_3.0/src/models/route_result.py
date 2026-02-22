"""路径结果模型"""

import json
from sqlalchemy import Column, Integer, String, Numeric, Text
from sqlalchemy.dialects.mysql import TIMESTAMP
from datetime import datetime
from src.config.database import Base


class RouteResult(Base):
    """路径结果表模型"""

    __tablename__ = 'route_result'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    start_address = Column(String(200), nullable=False, comment='起点地址')
    end_address = Column(String(200), nullable=False, comment='终点地址')
    algorithm = Column(String(50), nullable=False, comment='算法类型')
    route_json = Column(Text, nullable=False, comment='路径节点JSON')
    total_distance = Column(Numeric(10, 2), comment='总距离(米)')
    total_cost = Column(Numeric(10, 2), comment='总成本')
    execution_time = Column(Numeric(10, 2), comment='执行时间(毫秒)')
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment='创建时间')

    @property
    def route_nodes(self):
        """获取路径节点列表"""
        return json.loads(self.route_json) if self.route_json else []

    @route_nodes.setter
    def route_nodes(self, value):
        """设置路径节点列表"""
        self.route_json = json.dumps(value, ensure_ascii=False)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'start_address': self.start_address,
            'end_address': self.end_address,
            'algorithm': self.algorithm,
            'route_nodes': self.route_nodes,
            'total_distance': float(self.total_distance) if self.total_distance else None,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'execution_time': float(self.execution_time) if self.execution_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return (f"<RouteResult(id={self.id}, "
                f"algorithm={self.algorithm}, "
                f"start={self.start_address}, "
                f"end={self.end_address})>")
