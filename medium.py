from abc import ABC,abstractmethod
import math
from pymunk import Vec2d

class Medium(ABC):
    def __init__(self,density:float,viscosity:float,color):
        self.density=density
        self.viscosity=viscosity
        self.color=color

    @abstractmethod
    def contains(self,position:Vec2d):
        #判断是否在容器内
        pass

class Water(Medium):
    def __init__(self):
        super().__init__(1.0)

    def contains(self,position:Vec2d):
        