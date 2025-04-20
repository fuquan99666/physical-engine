
import pymunk
from pymunk import Vec2d
from data_handler import DataHandler


class PhysicsSimulator:
    def __init__(self):
        #基础参数
        self.space=pymunk.Space()
        self.space.gravity=(0,981)
        self.bodies=[]
        self.time_scale=1.0
        self.data_handler=DataHandler()

    def get_gravity(self):
        return self.space.gravity

    def set_gravity(self,gx,gy):
        self.space.gravity=(gx,gy)

    def add_circle(self,p_x,p_y,mass,out_radius,elasticity=0.5,inner_radius=0):

        #添加圆形物体
        moment=pymunk.moment_for_circle(mass,inner_radius,out_radius)
        body=pymunk.Body(mass,moment)
        body.position=(p_x,p_y)
        shape=pymunk.Circle(body,out_radius)
        shape.elasticity=elasticity
        self.space.add(body,shape)
        self.bodies.append(body)
        return body

    def add_box(self,p_x,p_y,height,width,mass,elasticity=0.5):

        #添加矩形物体
        moment=pymunk.moment_for_box(mass,(width,height))
        body=pymunk.Body(mass,moment)
        body.position=(p_x,p_y)
        shape=pymunk.Poly.create_box(body,(width,height))
        shape.elasticity=elasticity
        self.space.add(body,shape)
        self.bodies.append(body)
        return body

    def add_segment(self,start,destination,mass,radius=0.1,elasticity=0.5):

        #添加线段（类似于杆）
        moment=pymunk.moment_for_segment(mass,start,destination,radius)
        body=pymunk.Body(mass,moment)
        body.position=(start+destination)/2
        shape=pymunk.Segment(body,start,destination,radius)
        shape.elasticity=elasticity
        self.space.add(body,shape)
        self.bodies.append(body)
        return body

    def add_spring(self,body1,body2,stiffness,damping,anchor1=(0,0),anchor2=(0,0),rest_length=100):

        #添加指定地点的弹簧
        spring=pymunk.DampedSpring(
            body1,body2,anchor1,anchor2,rest_length,stiffness,damping
        )
        self.space.add(spring)
        return spring

    def update_gravity(self,g_x,g_y):

        #更新实时均匀力场
        self.space.gravity=(g_x*self.time_scale,g_y*self.time_scale)

    def update_object_property(self,body,mass=None,elasticity=None,velocity=None):

        #更新物理性质
        if mass is not None:
            body.mass=mass
        if elasticity is not None:
            for shape in body.shapes:
                shape.elasticity=elasticity
        if velocity is not None:
            body.velocity=velocity

    def step(self,dt):

        #推进物理引擎一步
        self.space.step(dt)
        #同步记录数据
        self.data_handler.update_sim_time(dt)
        self.data_handler.collect_data(self.bodies,self.data_handler.current_sim_time)


    def clear(self):

        #清空物理空间
        self.space.remove(self.space.bodies)
        self.bodies=[]

