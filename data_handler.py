import pandas as pd
from datetime import datetime
from pymunk import Body
#from simulator import PhysicsSimulator

class DataHandler:
    def __init__(self):
        self.buffer=[]
        self.last_save_time=datetime.now().timestamp()
        self.current_sim_time=0.0#总时间

    def update_sim_time(self,dt):
        self.current_sim_time+=dt

    def collect_data(self,bodies,current_time):
        """收集数据，在确认数据类型后再确定形式"""
        for index,body in enumerate(bodies):
            new_row={
                "index":index,
                "timestamp": current_time,
                "x": body.position.x,
                "y": body.position.y,
                "vx": body.velocity.x,
                "vy": body.velocity.y,
            }
            self.databuffer.append(new_row)


    def reset(self):
        '''清空数据重新开始'''
        self.buffer.clear()


        self.current_sim_time=0.0


class DataCalculator:
    @staticmethod
    def kinetic_energy(body:Body):
        return 0.5*body.mass*(body.velocity.x**2+body.velocity.y**2)

    @staticmethod
    def potential_energy(body:Body,ground_y=400,y_axis_direction:str="down"):
        height = (ground_y - body.position.y) if y_axis_direction == "down" else (body.position.y - ground_y)
        '''重力设定似乎很不完全，需要调整'''
        return body.mass*9.81*height
