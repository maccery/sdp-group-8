from models import *
from communication.controller import Controller
import time


class Task(object):
    def __init__(self, world):
        self._subtasks = Subtasks(world)
        self._world = world

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, world):
        self._world = world

    """
    Big tasks are things such as "move and grab ball"; these are made up of smaller tasks
    """

    def move_to_ball(self):
        # The list of subtasks we need to execute to complete this big task
        subtask_list = [self._subtasks.rotate_to_alignment(self.world.ball.x, self.world.ball.y),
                        self._subtasks.move_to_coordinates(self.world.ball.x, self.world.ball.y)]

        self.execute_tasks(subtask_list)

    def move_and_grab_ball(self):
        subtask_list = [self._subtasks.rotate_to_alignment(self.world.ball.x, self.world.ball.y),
                        self._subtasks.grab_ball(),
                        self._subtasks.move_to_coordinates(self.world.ball.x, self.world.ball.y)]

        self.execute_tasks(subtask_list)

    def kick_ball_in_goal(self, goal_x, goal_y):

        # Turn and face the goal, then kick the ball
        subtask_list = [self._subtasks.rotate_to_alignment(goal_x, goal_y),
                        self._subtasks.ungrab_ball(),
                        self._subtasks.kick_ball()]

        self.execute_tasks(subtask_list)

    def execute_tasks(self, subtask_list):
        # Update the robot to state we're actually doing a task and busy
        self._world.our_robot.is_busy = True

        # Go through our task list, waiting for each task to complete before moving onto next task
        for subtask in subtask_list:
            subtask_complete = subtask()

            # if the subtask isn't complete, don't move onto the next task
            if subtask_complete is False:
                exit()

        # Update the robot to non-busy status
        self._world.our_robot.is_busy = False


class Subtasks(object):
    def __init__(self, world):
        self._communicate = Controller()
        self._world = world

    """
    Subtasks are one specific thing, such as 'kick', that is communicated to the Arduino
    """

    def move_to_coordinates(self, x, y):
        """
        Given a specific robot, it will try and move this robot to a given co-ordinate, assuming it is facing the correct way
        already
        :param target_vector
        """

        # Calculate how long we need to run the motor for
        distance = self._world.our_robot.get_displacement_to_point(x, y)

        if distance < 10:
            return True
        else:
            calculated_duration = self.calculate_motor_duration(distance)

            # Tell arduino to move for the duration we've calculated
            self._communicate.move_duration(calculated_duration)

            # Wait until this task has completed
            time.sleep(calculated_duration)
            return False

    def rotate_to_alignment(self, x, y):
        """
        Given a specific robot, it will rotate to face a specific angle

        :param target_vector:
        """

        angle_to_rotate = self._world.get_rotation_to_point(x, y)

        # If the angle of rotation is less than 15 degrees, leave it how it is
        if angle_to_rotate <= 15:
            return True
        else:
            duration = self.calculate_motor_duration_turn(angle_to_rotate)
            wait_time = self._communicate.turn(duration)
            time.sleep(wait_time)

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
        duration = angle_to_rotate * 0.5
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
