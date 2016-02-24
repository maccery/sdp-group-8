from math import cos, sin, hypot, pi, atan2
from planning.tasks import Task
from helper import *
import time

class Robot(object):
    def __init__(self, x, y, angle):
        self.is_busy = False
        self.x = x
        self.y = y
        self.angle = angle  # degrees from the north. 0 being north, +clockwise, -anticlockwise

    def get_rotation_to_point(self, target_x, target_y):
        """
        Calculates the rotation required to achieve alignment with given co-ordinates.
        This presumes the robot's angle given is the degrees from north, +clockwise.
        So "10 degrees", is 10 degrees clockwise from North

        The co-ordinate system from the vision system goes 0->+ from left to right, and  0->+ as you go down, therefore
        the maths is different

        :param target_x:
        :param target_y:
        :return: angle: +clockwise, in degrees, to rotate
        """
        delta_x = target_x - self.x
        delta_y = target_y - self.y

        theta_ball = atan2(delta_y, delta_x) + pi / 2
        if theta_ball > pi:
            theta_ball -= 2 * pi
        theta_ball = theta_ball / 2 / pi * 360

        theta_robot = self.angle
        angle_to_rotate = theta_ball - theta_robot
        print('angles:', theta_ball, theta_robot)
        if angle_to_rotate > 180:
            angle_to_rotate -= 360
        if angle_to_rotate < -180:
            angle_to_rotate += 360

        return angle_to_rotate

    def get_displacement_to_point(self, target_x, target_y):
        """
        Uses the euclidean distance to calculate the displacement between this robot and a target co-ordinates

        :param x:
        :param y:
        :return: displacement
        """
        delta_x = target_x - self.x
        delta_y = target_y - self.y
        displacement = hypot(delta_x, delta_y)

        return displacement


class Ball(object):
    def __init__(self, x, y, speed=0):
        self.x = x
        self.y = y
        self.speed = speed
        self.last_update_time = now()


    def update_speed(self, x, y):
        # calculate the speed the ball is moving at, based on the last time we updated the speed and the distnance moved

        time_since_last_updated = now() - self.last_update_time
        self.speed = calculate_speed(self.x, self.y, x, y, time_since_last_updated)

        # time in seconds
        self.x = x
        self.y = y
        self.last_update_time = now()

class Goal(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class World(object):
    """
    This class describes the environment; the pitch, the ball, the robots...
    """

    def __init__(self, pitch_num):
        self._ball = Ball(0, 0)
        self._our_robot = Robot(0, 0, 0)
        self._teammate = Robot(0, 0, 0)
        self._task = Task(self)
        self._goal = Goal(0, 0)

    @property
    def ball(self):
        return self._ball

    @property
    def our_robot(self):
        return self._our_robot

    @property
    def teammate(self):
        return self._teammate

    @property
    def task(self):
        return self._task

    def update_positions(self, pos_dict):
        """
        This method will update the positions of the pitch objects
            that it gets passed by the vision system
        :param pos_dict:
        :return:
        """
        for robot in pos_dict['robots']:
            if robot['team'] == 'yellow' and robot['group'] == 'green':
                self.our_robot.x = robot['center'][0]
                self.our_robot.y = robot['center'][1]
                self.our_robot.angle = robot['angle']

            if robot['team'] == 'blue' and robot['group'] == 'blue':
                self.teammate.x = robot['center'][0]
                self.teammate.y = robot['center'][1]
                self.teammate.angle = robot['angle']

        if pos_dict['ball']:
            # Before we update the positions, we can calculate the velocity of the ball by comparing it with its
            # previous position
            new_x = pos_dict['ball']['center'][0]
            new_y = pos_dict['ball']['center'][1]
            self.ball.update_speed(new_x, new_y) # this also updates positions
            # print(self.our_robot.x, self.our_robot.y, self.our_robot.angle)
            # print(self.ball.x, self.ball.y)