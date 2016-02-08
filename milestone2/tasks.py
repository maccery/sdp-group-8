from models import *
from communication.controller import Communication


class Tasks:
    """
    Given a specific task; it will try and make the robot complete these
    """

    def __init__(self):
        self.communicate = Communication()
        pass

    def move_to_coordinates(self, robot, target_coordinates):
        """
        Given a specific robot, it will try and move this robot to a given co-ordinate
        :param robot
        :param move_to_cordinates
        """

        # Rotate the robot to face the target
        self.rotate_to_alignment(robot, target_coordinates)

        # Calculate how long we need to run the motor for
        distance = robot.get_displacement_to_point(target_coordinates)
        calculated_duration = self.calculate_motor_duration(distance)

        # Tell arduino to move for the duration we've calculated
        self.communicate.move_duration(calculated_duration)

    def rotate_to_alignment(self, robot, target_coordinates):
        """
        Given a specific robot, it will rotate to face a specific angle

        :param robot:
        :param rotate_to_angle:
        """

        angle_to_rotate = robot.get_rotation_to_point(target_coordinates)
        self.communicate.turn_clockwise(angle_to_rotate)

    def calculate_motor_duration(self, distance):
        """
        Given a distance to travel, we need to know how long to run the motor for
        :param distance:
        """

        # Crudely return 500ms until we have better shit
        return 500

