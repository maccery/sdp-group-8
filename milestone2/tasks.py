from models import *
from communication.controller import Communication
import time


class Task(object):
    def __init__(self, world):
        self._subtasks = Subtasks(world)
        self._world = world

    """
    Big tasks are things such as "move and grab ball"; these are made up of smaller tasks
    """

    def move_to_ball(self, ball_vector):
        # The list of subtasks we need to execute to complete this big task
        subtask_list = [self._subtasks.rotate_to_alignment(ball_vector),
                        self._subtasks.move_to_coordinates(ball_vector)]

        self.execute_tasks(subtask_list)

    def move_and_grab_ball(self, ball_vector):
        subtask_list = [self._subtasks.rotate_to_alignment(ball_vector),
                        self._subtasks.grab_ball(),
                        self._subtasks.move_to_coordinates(ball_vector)]

        self.execute_tasks(subtask_list)

    def kick_ball_in_goal(self, goal_vector):
        target_vector = goal_vector

        # Turn and face the goal, then kick the ball
        subtask_list = [self._subtasks.rotate_to_alignment(target_vector),
                        self._subtasks.ungrab_ball(),
                        self._subtasks.kick_ball()]

        self.execute_tasks(subtask_list)

    def execute_tasks(self, subtask_list):
        # Update the robot to state we're actually doing a task and busy
        self._world.our_robot.is_busy = True

        # Go through our task list, waiting for each task to complete before moving onto next task
        for subtask in subtask_list:
            subtask()

        # Update the robot to non-busy status
        self._world.our_robot.is_busy = False


class Subtasks(object):
    def __init__(self, world):
        self._communicate = Communication()
        self._world = world

    """
    Subtasks are one specific thing, such as 'kick', that is communicated to the Arduino
    """

    def move_to_coordinates(self, target_vector):
        """
        Given a specific robot, it will try and move this robot to a given co-ordinate, assuming it is facing the correct way
        already
        :param target_vector
        """

        # Calculate how long we need to run the motor for
        distance = self._world.our_robot.get_displacement_to_point(target_vector)
        calculated_duration = self.calculate_motor_duration(distance)

        # Tell arduino to move for the duration we've calculated
        self._communicate.move_duration(calculated_duration)

        # Wait until this task has completed
        time.sleep(calculated_duration)

    def rotate_to_alignment(self, target_vector):
        """
        Given a specific robot, it will rotate to face a specific angle

        :param target_vector:
        """

        angle_to_rotate = self._world.get_rotation_to_point(target_vector)
        wait_time = self._communicate.turn_clockwise(angle_to_rotate)

        time.sleep(wait_time)

    def ungrab_ball(self):
        wait_time = self._communicate.ungrab()
        time.sleep(wait_time)

    def grab_ball(self):
        wait_time = self._communicate.grab()
        time.sleep(wait_time)

    def kick_ball(self):
        wait_time = self._communicate.kick()
        time.sleep(wait_time)

    @staticmethod
    def calculate_motor_duration(distance):
        """
        Given a distance to travel, we need to know how long to run the motor for
        :param distance:
        """

        # Crudely return 500ms until we have better shit
        return 500
