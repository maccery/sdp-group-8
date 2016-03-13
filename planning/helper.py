import time
from math import hypot


def now():
    return int(round(time.time()))


def calculate_speed(start_x, start_y, end_x, end_y, time):
    """
    Given co-ordinates and the time taken, it will return the speed. The function is independent on units; the
    output is given in whatever units inputted

    :param start_x:
    :param start_y:
    :param end_x:
    :param end_y:
    :param time:
    :return speed
    """

    # calculate speed
    delta_x = end_x - start_x
    delta_y = end_y - start_y
    displacement = hypot(delta_x, delta_y)

    if time == 0:
        return displacement
    else:
        return displacement / time


def calculate_velocity(start_x, start_y, end_x, end_y, time):
    if time == 0:
        velocity_x = end_x - start_x
        velocity_y = end_y - start_y
    else:
        velocity_x = (end_x - start_x) / time
        velocity_y = (end_y - start_y) / time

    return velocity_x, velocity_y


def calculate_midpoint(x1, y1, x2, y2):
    midpoint_x = (x1 + x2) / 2
    midpoint_y = (y1 + y2) / 2

    return midpoint_x, midpoint_y


def calculate_acceleration(old_speed, new_speed, time):
    if time == 0:
        return 0
    else:
        return new_speed - old_speed / time


def predicted_coordinates(current_x, current_y, initial_velocity, current_velocity):
    # assuming the ball is moving in a straight line
    # v = v0 + at
    # we want to know 0 = initial_velocity + at (arrange to calculate t)
    # t = 0 - initial_velocity / a

    acceleration_x = calculate_acceleration(initial_velocity[0], current_velocity[0])
    acceleration_y = calculate_acceleration(initial_velocity[1], current_velocity[1])

    # calculate horizontal acceleration
    time_when_ball_stops = 0
    if acceleration_x > 0:
        time_when_ball_stops = -initial_velocity[0] / acceleration_x

    # calculate position at this point
    # s = ut + (1/2)a t^2
    distance_till_stop_x = (initial_velocity[0] * time_when_ball_stops) + ((1 / 2) * acceleration_x * time * time)

    # calculate vertical acceleration
    time_when_ball_stops = 0
    if acceleration_y > 0:
        time_when_ball_stops = -initial_velocity[1] / acceleration_y

    # calculate position at this point
    # s = ut + (1/2)a t^2
    distance_till_stop_y = (initial_velocity[1] * time_when_ball_stops) + ((1 / 2) * acceleration_y * time * time)

    return current_x + distance_till_stop_x, current_y + distance_till_stop_y
