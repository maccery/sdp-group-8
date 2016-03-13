import unittest
import math
import time
from planning.helper import *


class TestHelpers(unittest.TestCase):
    def test_calculate_acceleration(self):
        old_velocity = (0,0)
        new_velocity = (2,2)
        time = 0
        acceleration = calculate_acceleration(old_velocity,new_velocity,time)
        self.assertEqual(acceleration, (2,2))

    def test_calculate_velocity(self):
        start_x = 0
        start_y = 0
        end_x = 2
        end_y = 2
        time = 0
        velocity = calculate_velocity(start_x, start_y, end_x, end_y, time)
        self.assertEqual(velocity, (2,2))

    def test_predicted_coordinates(self):
        current_x = 2
        current_y = 2
        initial_velocity = (2, 2)
        acceleration = (-2, -2)

        predict = predicted_coordinates(current_x, current_y, initial_velocity, acceleration)
        self.assertEqual((3,3), predict)

if __name__ == '__main__':
    unittest.main()
