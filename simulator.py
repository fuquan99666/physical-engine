import pymunk
from pymunk import Vec2d
from data_handler import DataHandler


class PhysicsSimulator:
    def __init__(self):
        # 基础参数
        self.space = pymunk.Space()
        self.space.gravity = (0, 981)  # 重力
   
        self.bodies = []  # 全部物体
        self.time_scale = 1.0  # 用于控制时间流速
        self.data_handler = DataHandler()  # 统计数据
        self.create_index = 0

    def get_gravity(self):
        return self.space.gravity

    def set_gravity(self, gx, gy):
        self.space.gravity = (gx, gy)

    def get_time_scale(self):
        return self.time_scale

    def set_time_scale(self,ratio):
        self.time_scale=ratio

    def init_datahandler(self):
        if self.data_handler.current_file == None:
            self.data_handler.create_initial_file()

    def add_circle(self, p_x, p_y, mass, out_radius, elasticity=0.5, inner_radius=0):

        # 添加圆形物体(x,y,质量，外半径，伸缩系数，内半径（缺省为零）)
        moment = pymunk.moment_for_circle(mass, inner_radius, out_radius)
        body = pymunk.Body(mass, moment)
        body.position = (p_x, p_y)
        shape = pymunk.Circle(body, out_radius)
        shape.elasticity = elasticity
        self.space.add(body, shape)
        self.bodies.append(body)
        self.create_index += 1
        self.init_datahandler()
        self.data_handler.register_object(self.create_index, "circle", mass=mass, radius=out_radius, color='00ff00')
        return body, shape

    def add_box(self, p_x, p_y, height, width, mass, elasticity=0.5):

        # 添加矩形物体(x,y,高度，宽度，质量，伸缩系数)
        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = (p_x, p_y)
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.elasticity = elasticity
        self.space.add(body, shape)
        self.bodies.append(body)
        self.create_index += 1
        self.init_datahandler()
        self.data_handler.register_object(self.create_index, 'polygon', mass=mass, width=width, height=height,
                                          color='00ff00')
        return body, shape

    def add_segment(self, start, destination, mass, radius=0.1, elasticity=0.5, static=False):
        if static:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:

            # 添加线段（类似于杆）(起点，终点，质量，半径（就是碰撞的宽度，缺省0.1），伸缩系数）
            moment = 0.01 * pymunk.moment_for_segment(mass,
                                                      start,
                                                      destination,
                                                      radius)
            body = pymunk.Body(mass,
                               moment)
        body.position = (start + destination) / 2

        shape = pymunk.Segment(body, start - body.position, destination - body.position, radius)
        shape.elasticity = elasticity
        self.space.add(body, shape)
        self.bodies.append(body)
        self.create_index += 1
        self.init_datahandler()
        self.data_handler.register_object(self.create_index, 'segment', start=start, destination=destination,
                                          radius=radius, color='00ff00')
        return body, shape

    def add_spring(self, body1, body2, stiffness, damping, anchor1=(0, 0), anchor2=(0, 0), rest_length=100):

        # 添加指定地点的弹簧(连接的物体一，物体二，劲度系数，阻尼，弹簧两端在物体上连接的具体位置（相对于物体中心坐标一，二，自然长度)
        spring = pymunk.DampedSpring(
            body1,
            body2,
            anchor1,
            anchor2,
            rest_length,
            stiffness,
            damping)
        self.space.add(spring)
        self.create_index += 1
        self.init_datahandler()
        return spring

    def add_polygon(self, p_x, p_y, vertices, mass, elasticity=0.5):

        # 添加多边形物体(x,y,高度，宽度，质量，伸缩系数)
        moment = pymunk.moment_for_poly(mass,
                                        vertices)
        body = pymunk.Body(mass,
                           moment)
        body.position = (p_x,
                         p_y)
        try:
            shape = pymunk.Poly(body, vertices)
        except Exception as e:
            raise ValueError(f"无效多边形顶点: {str(e)}") from e
        shape.elasticity = elasticity
        self.space.add(body, shape)
        self.bodies.append(body)
        self.create_index += 1
        self.init_datahandler()
        return body, shape

    def add_pivot_joint(self, body_a, body_b, anchor_a, anchor_b):
        """
        创建两个物体间的旋转关节
        :param body_a: 第一个物体
        :param body_b: 第二个物体
        :param anchor_a: 在body_a上的连接点（局部坐标）
        :param anchor_b: 在body_b上的连接点（局部坐标）
        :return: 关节对象
        """
        joint = pymunk.PinJoint(
            body_a,
            body_b,
            anchor_a,
            anchor_b
        )
        self.space.add(joint)
        self.create_index += 1
        self.init_datahandler()
        return joint

    def add_slide_joint(self, body_a, body_b, anchor_a, anchor_b, min_length, max_length):
        """
        创建可限制移动距离的关节
        :param min_length: 最小允许距离
        :param max_length: 最大允许距离
        """
        joint = pymunk.SlideJoint(
            body_a,
            body_b,
            anchor_a,
            anchor_b,
            min_length,
            max_length
        )
        self.space.add(joint)
        self.create_index += 1
        self.init_datahandler()
        return joint

    def add_gear_joint(self, body_a, body_b, phase, ratio):
        """
        创建同步旋转的齿轮约束
        :param phase: 初始角度差（弧度）
        :param ratio: 转速比（2.0表示body_a转1圈body_b转2圈）
        """
        joint = pymunk.GearJoint(body_a, body_b, phase, ratio)
        self.space.add(joint)
        self.create_index += 1
        self.init_datahandler()
        return joint

    def update_gravity(self, g_x, g_y):

        # 更新实时均匀力场
        self.space.gravity = (g_x * self.time_scale,
                              g_y * self.time_scale)

    def update_object_property(self, body, mass=None, elasticity=None, velocity=None):

        # 更新物理性质
        if mass is not None:
            body.mass = mass
        if elasticity is not None:
            for shape in body.shapes:
                shape.elasticity = elasticity
        if velocity is not None:
            body.velocity = velocity

    def step(self, dt):

        scaled_dt = dt * self.time_scale

        # 推进物理引擎一步
        self.space.step(scaled_dt)
        # 同步记录数据
        self.data_handler.update_sim_time(scaled_dt)
        self.data_handler.collect_data(self.bodies,
                                       self.data_handler.current_sim_time)

    def clear(self):

        # 清空物理空间
        self.space.remove(self.space.bodies)
        self.bodies = []
