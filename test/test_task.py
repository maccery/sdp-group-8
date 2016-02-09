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
    def test_calculating_angle(self):
        angle_in_degrees = 0
        angle_in_radians = angle_in_degrees * math.pi / 180
        robot = Robot(0, 0, angle_in_radians)

        angle_to_rotate = robot.get_rotation_to_point(4, 4)

        self.assertEqual(angle_to_rotate, 45)
    
if __name__ == '__main__':
    unittest.main()