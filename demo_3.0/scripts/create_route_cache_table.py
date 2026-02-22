"""Create route_cache table using Python"""
import pymysql
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config.settings import get_config

def create_table():
    """Create the route_cache table"""
    config = get_config()

    try:
        connection = pymysql.connect(
            host=config.get("database.host", "localhost"),
            user=config.get("database.user", "root"),
            password=config.get("database.password", ""),
            database=config.get("database.database", "vrp_project"),
            charset=config.get("database.charset", "utf8mb4"),
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Create table SQL - reduced VARCHAR size for unique key
            sql = """
            CREATE TABLE IF NOT EXISTS route_cache (
                id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary Key',

                -- Cache keys (reduced size for unique key)
                start_address VARCHAR(200) NOT NULL COMMENT 'Start address',
                end_address VARCHAR(200) NOT NULL COMMENT 'End address',
                start_lat DECIMAL(10, 7) NOT NULL COMMENT 'Start latitude',
                start_lng DECIMAL(10, 7) NOT NULL COMMENT 'Start longitude',
                end_lat DECIMAL(10, 7) NOT NULL COMMENT 'End latitude',
                end_lng DECIMAL(10, 7) NOT NULL COMMENT 'End longitude',

                -- Original route data from Amap API
                raw_polyline TEXT COMMENT 'Original polyline data',
                total_distance DECIMAL(10, 2) COMMENT 'Total distance (meters)',
                estimated_duration INT COMMENT 'Estimated duration (seconds)',

                -- Graph structure data (JSON serialized)
                graph_data LONGTEXT COMMENT 'Temporary graph structure (JSON)',
                node_mapping LONGTEXT COMMENT 'Node ID mapping (JSON)',

                -- Algorithm results (JSON serialized)
                dijkstra_result TEXT COMMENT 'Dijkstra algorithm result (JSON)',
                astar_result TEXT COMMENT 'A* algorithm result (JSON)',
                pso_result TEXT COMMENT 'PSO algorithm result (JSON)',

                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created at',
                last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last accessed at',
                access_count INT DEFAULT 1 COMMENT 'Access count',
                cache_hit_count INT DEFAULT 0 COMMENT 'Cache hit count',

                -- Indexes
                UNIQUE KEY uk_route (start_address(150), end_address(150)),
                INDEX idx_coords (start_lat, start_lng, end_lat, end_lng),
                INDEX idx_created (created_at),
                INDEX idx_access (access_count DESC)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Route cache table';
            """

            cursor.execute(sql)
            connection.commit()
            print("Successfully created route_cache table!")

            # Verify table exists
            cursor.execute("SHOW TABLES LIKE 'route_cache'")
            result = cursor.fetchone()
            if result:
                print("Verified: route_cache table exists.")
                cursor.execute("DESCRIBE route_cache")
                columns = cursor.fetchall()
                print(f"\nTable structure ({len(columns)} columns):")
                for col in columns:
                    print(f"  - {col['Field']}: {col['Type']}")
            else:
                print("Warning: Table creation may have failed.")

    except Exception as e:
        print(f"Error creating table: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    create_table()
