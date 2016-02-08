from models import *
from communication.controller import Communication
import time


class Task:
    def __init__(self, robot):
        self.subtasks = Subtasks(robot=robot)
        self.robot = robot

    """
    Big tasks are things such as "move and grab ball"; these are made up of smaller tasks
    """

    def move_to_ball(self, target_vector):
        # The list of subtasks we need to execute to complete this big task
        task_list = [self.subtasks.rotate_to_alignment(target_vector),
                     self.subtasks.move_to_coordinates(target_vector)]

        # Update the robot to state we're actually doing a task and busy
        self.robot.is_busy = True

        # Go through our task list, waiting for each task to complete before moving onto next task
        for task in task_list:
            task()

        # Update the robot to non-busy status
        self.robot.is_busy = False


class Subtasks:
    """
    Given a specific task; it will try and make the robot complete these
    """

    def __init__(self, robot):
        self.communicate = Communication()
        self.robot = robot

    def move_to_coordinates(self, target_vector):
        """
        Given a specific robot, it will try and move this robot to a given co-ordinate, assuming it is facing the correct way
        already
        :param robot
        :param move_to_cordinates
        """

        # Calculate how long we need to run the motor for
        distance = self.robot.get_displacement_to_point(target_vector)
        calculated_duration = self.calculate_motor_duration(distance)

        # Tell arduino to move for the duration we've calculated
        self.communicate.move_duration(calculated_duration)

        # Wait until this task has completed
        time.sleep(calculated_duration)

        return True

    def rotate_to_alignment(self, target_vector):
        """
        Given a specific robot, it will rotate to face a specific angle

        :param robot:
        :param rotate_to_angle:
        """

        angle_to_rotate = self.robot.get_rotation_to_point(target_vector)
        wait_time = self.communicate.turn_clockwise(angle_to_rotate)

        time.sleep(wait_time)

        return True

    @staticmethod
    def calculate_motor_duration(distance):
        """
        Given a distance to travel, we need to know how long to run the motor for
        :param distance:
        """

        # Crudely return 500ms until we have better shit
        return 500
