import sqlite3
import json
class DataReplayer:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(f"{db_path}.db")
        self.current_time = 0.0
        
    def get_full_timeline(self):
        """获取完整时间线"""
        return self.conn.execute(
            "SELECT DISTINCT timestamp FROM body_data ORDER BY timestamp"
        ).fetchall()

    def get_frame_data(self, target_time):
        """获取带属性的帧数据"""
        cur = self.conn.execute('''
            SELECT b.idx, b.x, b.y, b.vx, b.vy,
                   p.shape_type, p.radius, p.width, p.height, 
                   p.vertices, p.metadata
            FROM body_data b
            LEFT JOIN object_properties p 
            ON b.idx = p.obj_id
            WHERE b.timestamp BETWEEN ? AND ? + 0.001
        ''', [target_time, target_time])
        
        frame_data = {}
        for row in cur:
            obj_id, x, y, vx, vy, shape_type, radius, width, height,start,destination,vertices, metadata = row
            frame_data[obj_id] = {
                'position': (x, y),
                'velocity': (vx, vy),
                'properties': {
                    'shape_type': shape_type,
                    'radius': radius,
                    'width': width,
                    'height': height,
                    'start':start,
                    'destination':destination,
                    'vertices': json.loads(vertices) if vertices else None,
                    'metadata': json.loads(metadata) if metadata else {}
                }
            }
        return frame_data
    
    def _get_object_properties(self, obj_id):
        """获取物体属性"""
        prop = self.conn.execute(
            "SELECT * FROM object_properties WHERE obj_id = ?",
            (obj_id,)
        ).fetchone()
        
        if prop:
            return {
                'shape_type': prop[1],
                'radius': prop[2],
                'width': prop[3],
                'height': prop[4],
                'vertices': json.loads(prop[5]) if prop[5] else None,
                'metadata': json.loads(prop[6]) if prop[6] else {}
            }
        return None