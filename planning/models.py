from math import hypot, pi, atan2

from helper import *
from planning.tasks import Task


class Robot(object):
    def __init__(self, x, y, angle, speed=0):
        self.is_busy = False
        self.x = x
        self.y = y
        self.angle = angle  # degrees from the north. 0 being north, +clockwise, -anticlockwise
        self.speed = speed
        self.last_update_time = now()
        self.team_color = None
        self.group_color = None
        self.grabbers_open = True

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

    def update_speed(self, x, y):
        # calculate the speed the ball is moving at, based on the last time we updated the speed and the distnance moved

        time_since_last_updated = now() - self.last_update_time
        self.speed = calculate_speed(self.x, self.y, x, y, time_since_last_updated)

        # time in seconds
        self.x = x
        self.y = y
        self.last_update_time = now()

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
        self.velocity = (0,0)
        self.acceleration = (0,0)
        self.last_update_time = now()
        self.predicted_stopping_coordinates_x = x
        self.predicted_stopping_coordinates_y = y

    def update_speed(self, x, y):
        # calculate the speed the ball is moving at, based on the last time we updated the speed and the distnance moved

        time_since_last_updated = now() - self.last_update_time
        initial_velocity = self.velocity
        self.speed = calculate_speed(self.x, self.y, x, y, time_since_last_updated)

        # predict where the ball is going to stop
        self.velocity = calculate_velocity(self.x, self.y, x, y, time_since_last_updated)
        self.acceleration = calculate_acceleration(initial_velocity, self.velocity, time_since_last_updated)
        self.predicted_stopping_coordinates_x, self.predicted_stopping_coordinates_y = predicted_coordinates(x, y, initial_velocity, self.acceleration)

        # time in seconds
        self.x = x
        self.y = y
        self.last_update_time = now()


class Goal(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Region(object):
    def __init__(self, left, right):
        self.left = left  # x co-ordinate of the very left of region
        self.right = right  # x co-ordinate of the very right of region

    def contains(self, x, y):
        """
        If these co-ordinates are within this region, return true otherwise return false. Regions are only split vertically,
        and so we don't care about the y co-oridnates
        :param x:
        :param y:
        """
        if self.left <= x <= self.right:
            return True
        else:
            return False


class World(object):
    """
    This class describes the environment; the pitch, the ball, the robots...
    """

    def __init__(self, pitch_num):
        self._ball = Ball(0, 0)
        self._our_robot = Robot(0, 0, 0)
        self._teammate = Robot(0, 0, 0)
        self._their_attacker = Robot(0, 0, 0)
        self._their_defender = Robot(0, 0, 0)
        self._task = Task(self)
        self._their_goal = Goal(640, 240)
        self._our_goal = Goal(0, 240)
        self._defender_region = Region(0, 0)
        self._attacker_region = Region(0, 0)
        self._safety_padding = 10
        self._robot_safety_padding = 40
        self._pitch_boundary_bottom = 0
        self._pitch_boundary_top = 0
        self._pitch_boundary_right = 0
        self._pitch_boundary_left = 0

    @property
    def ball(self):
        return self._ball

    @property
    def safety_padding(self):
        return self._safety_padding

    @safety_padding.setter
    def safety_padding(self, value):
        self._safety_padding = value

    @property
    def robot_safety_padding(self):
        return self._robot_safety_padding

    @safety_padding.setter
    def safety_padding(self, value):
        self._robot_safety_padding = value

    @property
    def our_goal(self):
        return self._our_goal

    @property
    def their_goal(self):
        return self._their_goal

    @property
    def our_robot(self):
        return self._our_robot

    @property
    def their_attacker(self):
        return self._their_attacker

    @property
    def their_defender(self):
        return self._their_defender

    @property
    def teammate(self):
        return self._teammate

    @property
    def pitch_boundary_bottom(self):
        return self._pitch_boundary_bottom

    @property
    def pitch_boundary_top(self):
        return self._pitch_boundary_top

    @property
    def pitch_boundary_left(self):
        return self._pitch_boundary_left

    @property
    def pitch_boundary_right(self):
        return self._pitch_boundary_right

    @pitch_boundary_bottom.setter
    def pitch_boundary_bottom(self, value):
        self._pitch_boundary_bottom = value

    @pitch_boundary_top.setter
    def pitch_boundary_top(self, value):
        self._pitch_boundary_top = value

    @pitch_boundary_left.setter
    def pitch_boundary_left(self, value):
        self._pitch_boundary_left = value

    @pitch_boundary_right.setter
    def pitch_boundary_right(self, value):
        self._pitch_boundary_right = value

    @property
    def task(self):
        return self._task

    @property
    def defender_region(self):
        return self._defender_region

    @property
    def attacker_region(self):
        return self._attacker_region

    def update_positions(self, pos_dict):
        """
        This method will update the positions of the pitch objects
            that it gets passed by the vision system
        :param pos_dict:
        :return:
        """
        for robot in pos_dict['robots']:
            if robot['team'] == self.our_robot.team_color and robot['group'] == self.our_robot.group_color:
                new_x = robot['center'][0]
                new_y = robot['center'][1]
                self.our_robot.angle = robot['angle']
                self.our_robot.update_speed(new_x, new_y)

            if robot['team'] == self.teammate.team_color and robot['group'] == self.teammate.group_color:
                new_x = robot['center'][0]
                new_y = robot['center'][1]
                self.teammate.angle = robot['angle']
                self.teammate.update_speed(new_x, new_y)

            if robot['team'] == self.their_attacker.team_color and robot['group'] == self.their_defender.group_color:
                new_x = robot['center'][0]
                new_y = robot['center'][1]
                self.their_attacker.angle = robot['angle']
                self.their_attacker.update_speed(new_x, new_y)

            if robot['team'] == self.their_defender.team_color and robot['group'] == self.their_defender.group_color:
                new_x = robot['center'][0]
                new_y = robot['center'][1]
                self.their_defender.angle = robot['angle']
                self.their_defender.update_speed(new_x, new_y)

        if pos_dict['ball']:
            # Before we update the positions, we can calculate the velocity of the ball by comparing it with its
            # previous position
            new_x = pos_dict['ball']['center'][0]
            new_y = pos_dict['ball']['center'][1]
            if new_x == 0 or new_y == 0:
                pass
            else:
                self.ball.update_speed(new_x, new_y)  # this also updates positions
            # print(self.our_robot.x, self.our_robot.y, self.our_robot.angle)
            # print(self.ball.x, self.bal
