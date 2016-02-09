from models import *
from communication.controller import Controller
import time


class Task(object):
    def __init__(self, world):
        self._world = world
        self._communicate = Controller()

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, world):
        self._world = world

    """
    Big tasks are things such as "move and grab ball"; these are made up of smaller tasks
    """

    def task_move_to_ball(self):

        print("move_to_ball command called")
        # If we're happy with ball rotation and movement stop
        if self.rotate_to_ball() and self.move_to_ball():
            return True
        else:
            return False

    def task_move_and_grab_ball(self):
        self.rotate_to_alignment(self.world.ball.x, self.world.ball.y)
        self.move_to_coordinates(self.world.ball.x, self.world.ball.y)
        self.grab_ball()

    def task_kick_ball_in_goal(self):

        goal_x = self.world.goal.x
        goal_y = self.world.goal.y

        # Turn and face the goal, then kick the ball
        self.rotate_to_alignment(goal_x, goal_y)
        self.ungrab_ball()
        self.kick_ball()

    def move_to_coordinates(self, x, y):
        """
        Given a specific robot, it will try and move this robot to a given co-ordinate, assuming it is facing the correct way
        already
        :param target_vector
        """

        print("Move to these co-ordinates: (", x, ",", y, ")")

        # Calculate how long we need to run the motor for
        distance = self._world.our_robot.get_displacement_to_point(x, y)

        print("Need to moev this distance: ", distance)

        if distance < 10:
            return True
        else:
            calculated_duration = self.calculate_motor_duration(distance)
            print ("RUnnin g for duration: ", calculated_duration)

            # Tell arduino to move for the duration we've calculated
            self._communicate.move_duration(-calculated_duration)

            # Wait until this task has completed
            print("We're sleeping for a bit while arudino gets it shit together", calculated_duration)
            time.sleep(calculated_duration / 1000)
            return False

    def rotate_to_ball(self):
        self.rotate_to_alignment(self._world.ball.x, self._world.ball.y)

    def move_to_ball(self):
        self.move_to_coordinates(self._world.ball.x, self._world.ball.y)

    def rotate_to_alignment(self, x, y):
        """
        Given a specific robot, it will rotate to face a specific angle

        :param target_vector:
        """
        print ("robots coordinates", self._world.our_robot.x, self._world.our_robot.y)
        print("Rotate to face these co-ordinates: (", x, ",", y, ")")
        angle_to_rotate = self._world.our_robot.get_rotation_to_point(x, y)

        print("calculated angle is ", angle_to_rotate)
        # If the angle of rotation is less than 15 degrees, leave it how it is
        if 15 >= angle_to_rotate >= -15:
            print("We're happy with the angle, no more rotation")
            return True
        else:
            duration = self.calculate_motor_duration_turn(angle_to_rotate)
            print("turning for duration ", duration)
            wait_time = self._communicate.turn(duration)
            print("We're sleeping for a bit while arudino gets it shit together", wait_time)
            time.sleep(abs(wait_time))
            return False

    def ungrab_ball(self):
        wait_time = self._communicate.ungrab()
        time.sleep(wait_time)
        return True

    def grab_ball(self):
        wait_time = self._communicate.grab()
        time.sleep(wait_time)
        return True

    def kick_ball(self):
        wait_time = self._communicate.kick()
        time.sleep(wait_time)
        return True

    @staticmethod
    def calculate_motor_duration_turn(angle_to_rotate):
        """
        :param angle_to_rotate: given in degrees
        """
        # crude angle -> duration conversion
        duration = 100 + (abs(angle_to_rotate) * 7.1)

        if angle_to_rotate < 0:
            duration = -duration

        return duration

    @staticmethod
    def calculate_motor_duration(distance):
        """
        Given a distance to travel, we need to know how long to run the motor for
        :param distance: provided in metres
        """

        # some crude distance -> duration measure. assumes 10cm of movement equates to 100ms, past the initial 100ms
        duration = 100 + (distance * 10)
        return duration
