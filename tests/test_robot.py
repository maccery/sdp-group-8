import unittest
import math
import time
from planning.models import World


class TestRobot(unittest.TestCase):
    def test_updating_our_robots_coordinates(self):
        world = World(0)
        task = world.task
        world.our_robot.x = 5
        self.assertEqual(task.world.our_robot.x, 5)

    def test_init_our_robot_with_current_time(self):
        world = World(0)
        now = int(round(time.time()))
        self.assertEqual(world.our_robot.last_update_time, now)
        self.assertEqual(world.our_robot.speed, 0)

    def test_update_speed(self):
        world = World(0)
        now = int(round(time.time()))

        # we've gone from 0,0 -> 2,2 in 0 seconds therefore out speed is sqrt(8)
        world.our_robot.update_speed(2, 2)
        self.assertEqual(world.our_robot.speed, math.sqrt(8))

    def test_update_speed_time(self):
        world = World(0)

        # sleep for 3s
        time.sleep(3)

        # we've gone from 0,0 -> 2,2 in 10 seconds therefore out speed is sqrt(8)/3
        world.our_robot.update_speed(2, 2)
        self.assertEqual(world.our_robot.speed, math.sqrt(8)/3)
        self.assertEqual(world.our_robot.x, 2)
        self.assertEqual(world.our_robot.x, 2)

    def test_update_speed_update_time(self):
        world = World(0)
        time.sleep(3)
        now = int(round(time.time()))
        world.our_robot.update_speed(2, 2)
        self.assertEqual(world.our_robot.last_update_time, now)

    def test_update_speed_stop(self):
        world = World(0)
        # we've gone from 0,0 -> 2,2 in 0 seconds therefore out speed is sqrt(8)
        world.our_robot.update_speed(2, 2)
        time.sleep(1)
        world.our_robot.update_speed(2, 2)
        # we've gone from 2,2 -> 2,2 in 1 second therefore out speed is 0-
        self.assertEqual(world.our_robot.speed, 0)

if __name__ == '__main__':
    unittest.main()
