from math import hypot
import time

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
