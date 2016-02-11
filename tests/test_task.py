import unittest
import math
from milestone2.models import World, Robot, Ball


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

    def test_calculating_angle_three(self):
        angle_in_degrees = 90
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)
        self.assertEqual(angle_to_rotate, 45)

    def test_calculating_angle_four(self):
        angle_in_degrees = 180
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)
        self.assertEqual(angle_to_rotate, -45)

    def test_calculating_angle_five(self):
        angle_in_degrees = 180
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(0, 0)
        self.assertEqual(angle_to_rotate, -90)

    def test_calculating_angle_six(self):
        angle_in_degrees = 180
        robot = Robot(4, 4, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(0, 0)
        self.assertEqual(angle_to_rotate, 135)

    def test_calculating_angle_seven(self):
        angle_in_degrees = 45
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)
        self.assertEqual(angle_to_rotate, 90)

    def test_calculating_angle_eight(self):
        angle_in_degrees = 180
        robot = Robot(0, 4, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(0, 0)
        self.assertEqual(angle_to_rotate, -180)

    def test_calculating_angle_nine(self):
        angle_in_degrees = -90
        robot = Robot(0, 0, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)
        self.assertEqual(angle_to_rotate, -135)

    def test_calculating_angle_ten(self):
        angle_in_degrees = -180
        robot = Robot(0, 4, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(0, 0)
        self.assertEqual(angle_to_rotate, 180)

    def test_calculating_angle_everything(self):
        angle_in_degrees = 64
        robot = Robot(3, 4, angle_in_degrees)

        angle_to_rotate = robot.get_rotation_to_point(1, 2)
        self.assertEqual(angle_to_rotate, -109)


class TestGetDisplacement(unittest.TestCase):
    def test_get_displacement(self):
        robot = Robot(0, 0, 0)
        displacement = robot.get_displacement_to_point(3, 3)
        self.assertEqual(round(displacement, 2), 4.24)

    def test_get_displacement_two(self):
        robot = Robot(2, 5, 0)
        displacement = robot.get_displacement_to_point(3, 3)
        self.assertEqual(round(displacement, 2), 2.24)


if __name__ == '__main__':
    unittest.main()
