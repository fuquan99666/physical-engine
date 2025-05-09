from abc import ABC,abstractmethod

import pymunk
from pymunk import Vec2d


class Field(ABC):
    """力场基类"""
    def __init__(self,strength=1.0,falloff=1.0):
        self.strength=strength
        self.falloff=falloff

    @abstractmethod
    def calculate_field_force(self,body:pymunk.Body):
        pass


    def add_force(self,body:pymunk.Body):
        force=self.calculate_field_force(body)
        body.apply_force_at_local_point(force,(0,0))

class MagneticField(Field):
    def __init__(self,direction,strength=0.0):
        super().__init__(strength)
        self.direction=direction

    def calculate_field_force(self,body:pymunk.Body):
        velocity=body.velocity
        directional_strength=self.strength*self.direction
        return Vec2d(-velocity.y,velocity.x)*directional_strength

class ElectricField(Field):
    def __init__(self,strength=1.0,charge_density=1.0):
        super().__init__(strength)
        self.charge_density=charge_density

    def calculate_field_force(self,body:pymunk.Body):
        pass


class GravitationalField(Field):
    def __init__(self,origin:Vec2d,source_mass=1000,strength=6.674e-11):
        super().__init__(strength)
        self.source_mass=source_mass
        self.origin=origin

    def calculate_field_force(self,body:pymunk.Body):
        r_vector=body.position-self.origin
        distance=r_vector.length
        '''可能要根据场源体形状（厚度）优化'''
        force=self.strength*self.source_mass*body.mass/(distance**2)
        return -r_vector.normalized()*force


