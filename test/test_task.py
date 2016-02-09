import unittest
import math
from milestone2.models import World, Robot


class TestModels(unittest.TestCase):
    def test_updating_balls_coordinates(self):
        world = World(0)
        task = world.task

        world.ball.x = 5

        self.assertEqual(task.world.ball.x, 5)


class TestRotation(unittest.TestCase):
    """
    Tests the get_rotation_to_point function of the robot to ensure it returns the correct angle
    """

    def test_calculating_angle(self):
        angle_in_degrees = 0
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)

        self.assertEqual(angle_to_rotate, 45)

    def test_calculating_angle_two(self):
        angle_in_degrees = -90
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)

        self.assertEqual(angle_to_rotate, 135)

    def test_calculating_angle_three(self):
        angle_in_degrees = 90
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)

        self.assertEqual(angle_to_rotate, -45)

    def test_calculating_angle_four(self):
        angle_in_degrees = 180
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)

        self.assertEqual(angle_to_rotate, -135)

    def test_calculating_angle_five(self):
        angle_in_degrees = 180
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)

        self.assertEqual(angle_to_rotate, -135)

    if __name__ == '__main__':
        unittest.main()
