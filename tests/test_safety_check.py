import unittest
import math
import time
from planning.models import *


class TestSafetyCheck(unittest.TestCase):

    def test_robot_in_way(self):
        world = World(0)
        world.pitch_boundary_top = 10
        world.pitch_boundary_bottom = 0
        world.pitch_boundary_left = 0
        world.pitch_boundary_right = 10
        world.our_robot.x = 2
        world.our_robot.y = 2

        world.teammate.x = 3
        world.teammate.y = 3

        self.assertFalse(world.task.safety_check(5, 5))

    def test_robot_not_in_way(self):
        world = World(0)
        world.pitch_boundary_top = 10
        world.pitch_boundary_bottom = 0
        world.pitch_boundary_left = 0
        world.pitch_boundary_right = 10
        world.safety_padding = 1
        world.our_robot.x = 2
        world.our_robot.y = 2

        world.teammate.x = 9
        world.teammate.y = 9

        self.assertTrue(world.task.safety_check(3, 3))

    def test_safety_padding(self):
        world = World(0)
        world.pitch_boundary_top = 10
        world.pitch_boundary_bottom = 0
        world.pitch_boundary_left = 0
        world.pitch_boundary_right = 10
        world.safety_padding = 6
        world.our_robot.x = 2
        world.our_robot.y = 2

        world.teammate.x = 9
        world.teammate.y = 9

        self.assertFalse(world.task.safety_check(3, 3))

    def test_going_to_hit_wall(self):
        world = World(0)
        world.pitch_boundary_top = 10
        world.pitch_boundary_bottom = 0
        world.pitch_boundary_left = 0
        world.pitch_boundary_right = 10
        world.safety_padding = 2
        world.our_robot.x = 2
        world.our_robot.y = 2

        self.assertFalse(world.task.safety_check(8, 8))

    def test_near_work_not_hit_wall(self):
        world = World(0)
        world.pitch_boundary_top = 10
        world.pitch_boundary_bottom = 0
        world.pitch_boundary_left = 0
        world.pitch_boundary_right = 10
        world.safety_padding = 1
        world.our_robot.x = 2
        world.our_robot.y = 2

        self.assertTrue(world.task.safety_check(8, 8))

    def test_fine_to_move(self):
        world = World(0)
        world.pitch_boundary_top = 10
        world.pitch_boundary_bottom = 0
        world.pitch_boundary_left = 0
        world.pitch_boundary_right = 10
        world.safety_padding = 0
        world.our_robot.x = 2
        world.our_robot.y = 2

        self.assertTrue(world.task.safety_check(5, 5))


if __name__ == '__main__':
    unittest.main()
