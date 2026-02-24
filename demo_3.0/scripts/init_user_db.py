"""初始化用户数据库表"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.database import init_db, engine
from sqlalchemy import text

def init_user_tables():
    """初始化用户相关的数据库表"""

    print("正在初始化用户数据库...")

    # 初始化所有表
    init_db()

    print("✓ 数据库表创建成功！")

    # 检查表是否存在
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"\n当前数据库表：{tables}")

        if 'users' in tables:
            print("\n✓ users 表已创建")
        else:
            print("\n✗ users 表创建失败")

        if 'password_resets' in tables:
            print("✓ password_resets 表已创建")
        else:
            print("✗ password_resets 表创建失败")

if __name__ == '__main__':
    init_user_tables()
