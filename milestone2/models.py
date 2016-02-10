from math import cos, sin, hypot, pi, atan2
from milestone2.tasks import Task


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

        :param target_x:
        :param target_y:
        :return: angle: +clockwise, in degrees, to rotate
        """
        delta_x = target_x - self.x
        delta_y = target_y - self.y
        theta_ball = atan2(delta_x, delta_y)
        theta_ball = theta_ball * 180 / pi
        theta_robot = self.angle
        angle_to_rotate = theta_ball - theta_robot

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
    def __init__(self, x, y):
        self.x = x
        self.y = y


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
        self._task = Task(self)
        self._goal = Goal(0, 0)

    @property
    def ball(self):
        return self._ball

    @property
    def our_robot(self):
        return self._our_robot

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

        if pos_dict['ball']:
            self.ball.x = pos_dict['ball']['center'][0]
            self.ball.y = pos_dict['ball']['center'][1]
            # print(self.our_robot.x, self.our_robot.y, self.our_robot.angle)
            # print(self.ball.x, self.ball.y)
