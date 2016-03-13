import time
from random import randint

import helper
from communication.controller import Controller


class Task(object):
    def __init__(self, world):
        self._world = world
        self._communicate = Controller()

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, world):
        self._world = world

    """
    Strategies
    """

    def task_defender(self):
        """
        Robot will strive to stay in the defending region, avoid other robots, and intercept ball.
        Once it has the ball, it shall pass to teammate.
        If the ball is in the attacking region, it shall just protect the goal and wait.
        """

        # while the ball is with us, just go to it. When you've got it, pass to teammate
        if self.ball_in_defender_region():
            print ("Ball in defender region")
            # if the ball is in the attacker region as well, we need to check who's closer - attacker or us
            if self.ball_in_attacker_region() and not self.are_we_closer_than_teammate():
                print ("Sit and wait for the ball")
                self.task_sit_between_goal_and_ball()

            # we're good to go, get ball and kick to teammate
            self.task_grab_rotate_kick()
        # the ball is in just the attacker region, our task is to be half way between the ball and the goal
        else:
            print "Ball is not in defender region, sit and wait for ball"
            self.task_sit_between_goal_and_ball()

        # always return false, this means this task will keep running
        return False

    def task_attacker(self):
        """
        Robot will not enter defending region. It will stay in attacking region.
        If the ball is in the defending region (which it cannot enter), it will wait to receive the ball from teammate.
        If the ball is in the attacking region, it will strive to grab the ball.
        Once it has the ball, it will look to shoot it in the goal.
        """
        if self.ball_in_attacker_region():
            # if the ball is in the defender region as well, we need to check who's closer - defender or us
            if self.ball_in_defender_region() and not self.are_we_closer_than_teammate():
                return False

            # we're good to go
            if self.task_move_and_grab_ball():
                self.task_kick_ball_in_goal()

        # always return false, this means this task will keep running
        return False

    def task_penalty(self):
        """
        Robot will aim to take a penalty, playing by the penalty rules. Assumes robot is holding ball
        """
        # wait a random amount of time
        random_number = randint(1, 5)
        time.sleep(random_number)

        # shoot
        return self.task_kick_ball_in_goal()

    def task_penalty_goalie(self):
        """
        Robot will be goalie for penality. Robot will randomly open grabbers, close them, while facing the ball
        """
        if self.rotate_to_ball():
            if self.ungrab_ball():
                time.sleep(20)
                self.grab_ball()

        return False

    """
    Big tasks; these are made up of smaller tasks
    """

    def task_vision(self):
        pass

    def task_rotate_and_grab(self):
        # rotate to face the ball
        if self.rotate_to_ball():
            # wait till ball has stopped
            if self._world.ball.speed < 5:
                # move to the ball with grabbers open
                if self.ungrab_ball():
                    if self.task_move_to_ball():
                        if self.grab_ball():
                            return self.ball_received()
        return False

    # Assuming we're facing the right direction
    def task_grab_rotate_kick(self):
        """
        Opens grabbers and moves to the ball, grabs it, rotates to teammate, kicks it to teammate.
        Does not check if ball is received by teammate
        """
        print ("Go grab the ball, kick it to teammate")
        #if self.ungrab_ball():
        if self.rotate_to_ball():
            if self.move_to_ball():
                if self.ball_received():
                        # grab the ball we've just be given
                    if self.grab_ball():
                            # rotate to face the other robot
                        if self.rotate_to_alignment(self._world.teammate.x, self._world.teammate.y):
                            if self.ungrab_ball():
                                    # kick ball to teammate
                                distance = self._world.our_robot.get_displacement_to_point(self._world.teammate.x,
                                                                                               self._world.teammate.y)
                                return self.kick_ball(distance_to_kick=distance)

        return False

    def task_move_to_ball(self):
        # If the ball isn't moving, we can just move to it
        if self._world.ball.speed < 5:
            if self.rotate_to_ball():
                return self.move_to_ball()
            else:
                return False
        # If the ball IS moving, we need to predict where it's going and move there...
        else:
            # move to predicted stopping point, but only when the ball is deceleration
            if self.world.ball.acceleration[0] < 0:
                predicted_x = self.world.ball.predicted_stopping_coordinates_x
                predicted_y = self.world.ball.predicted_stopping_coordinates_y

                if self.rotate_to_alignment(predicted_x, predicted_y):
                    return self.move_to_coordinates(predicted_x, predicted_y)
            return False

    def task_move_and_grab_ball(self):
        # If we're happy with rotation and movement, grab the ball
        if self.rotate_to_ball():
            if self.ungrab_ball():
                if self.move_to_ball():
                    return self.grab_ball()
        return False

    def task_kick_ball_in_goal(self):
        # If we're happy with rotation to face goal, ungarb and kick the ball
        if self.rotate_to_alignment(self.world.their_goal.x, self.world.their_goal.y):
            if self.ungrab_ball():
                return self.kick_ball()
        return False

    def task_sit_between_goal_and_ball(self):
        # work out co-ordinates half way between goal and ball
        midpoint_x, midpoint_y = helper.calculate_midpoint(self.world.our_goal.x, self.world.our_goal.y,
                                                           self.world.ball.x, self.world.ball.y)

        print ("our goal x, our goal y, ball x, ball y", self.world.our_goal.x, self.world.our_goal.y,
                                                         self.world.ball.x, self.world.ball.y)
        if self.rotate_to_alignment(midpoint_x, midpoint_y):
            if self.move_to_coordinates(midpoint_x, midpoint_y):
                return self.ungrab_ball()
        return False

    """
    Smaller tasks
    """

    def move_to_coordinates(self, x, y):
        """
        Given a specific robot, it will try and move this robot to a given co-ordinate, assuming it is facing the correct way
        already
        :param target_vector
        """
        print ("Move to coordinates x, y", x, y)

        # Calculate how long we need to run the motor for
        distance = self._world.our_robot.get_displacement_to_point(x, y)

        # are we gonna hit anyone in this time
        if self.safety_check(x, y):

            if distance < 32:
                return True
            else:
                calculated_duration = self.calculate_motor_duration(distance)

                # Tell arduino to move for the duration we've calculated
                self._communicate.move_duration(calculated_duration)

                # Wait until this task has completed

                time.sleep(calculated_duration / 1000)
                # Returns false which means we'll get more data from vision first, run this function again, to verify ok
                return False
        else:

            print ("Safety check failed")
            return False

    def rotate_to_ball(self):
        print ("Rotate to ball")
        return self.rotate_to_alignment(self._world.ball.x, self._world.ball.y)

    def move_to_ball(self):
        return self.move_to_coordinates(self._world.ball.x, self._world.ball.y)

    def rotate_to_alignment(self, x, y):
        """
        Given a specific robot, it will rotate to face a specific angle

        :param x:
        :param y:
        """
        angle_to_rotate = self._world.our_robot.get_rotation_to_point(x, y)
        distance = self._world.our_robot.get_displacement_to_point(x, y)

        # If the angle of rotation is less than 15 degrees, leave it how it is
        if (15 >= angle_to_rotate >= -15 and distance > 40) or (5 >= angle_to_rotate >= -5 and distance <= 40) or (25 >= angle_to_rotate >= -25 and distance <= 30):
            return True
        else:
            duration = self.calculate_motor_duration_turn(angle_to_rotate)
            wait_time = self._communicate.turn(duration)
            time.sleep(abs(wait_time))
            # Returns false which means we'll get more data from vision first, run this function again, to verify ok
            return False

    def ungrab_ball(self):
        # if the grabbers are already open, don't do anything
        print ("Ungrab ball")
        #if not self.world.our_robot.grabbers_open:
        print "Grabbers aren't open, please open them"
        wait_time = self._communicate.ungrab()
        time.sleep(wait_time)
        self.world.our_robot.grabbers_open = True
        return True

    def grab_ball(self):
        # if the grabbers are already closed, don't do anything
        print ("Grab ball")
        #if self.world.our_robot.grabbers_open:
        print "Grabbers are open, please close them"
        wait_time = self._communicate.grab()
        time.sleep(wait_time)
        self.world.our_robot.grabbers_open = False
        return True

    def kick_ball(self, distance_to_kick=None):
        print ("Kick ball")
        if distance_to_kick:
            power = self.calculate_kick_power(distance_to_kick)
        else:
            power = 1

        wait_time = self._communicate.kick(power)
        time.sleep(wait_time)
        return True

    '''
    Helper methods
    '''

    def are_we_closer_than_teammate(self):
        distance_for_us = self.world.our_robot.get_displacement_to_point(self.world.ball.x, self.world.ball.y)
        distance_for_teammate = self.world.teammate.get_displacement_to_point(self.world.ball.x, self.world.ball.y)

        if distance_for_us > distance_for_teammate:
            return False
        else:
            return True

    def ball_received(self):
        # calculate displacement from us to ball
        distance = self._world.our_robot.get_displacement_to_point(self._world.ball.x, self._world.ball.y)

        if distance < 32:
            return True
        else:
            return False

    def ball_received_by_teammate(self):
        # calculate displacement from us to ball
        distance = self._world.teammate.get_displacement_to_point(self._world.ball.x, self._world.ball.y)

        if distance < 50:
            return True
        else:
            return False

    def ball_in_defender_region(self):
        if self._world.defender_region.contains(self._world.ball.x, self._world.ball.y):
            return True
        else:
            return False

    def ball_in_attacker_region(self):
        if self._world.attacker_region.contains(self._world.ball.x, self._world.ball.y):
            return True
        else:
            return False

    def safety_check(self, resultant_x, resultant_y):
        """
        Before any movement is called, this is called. This essentially checks if the movement we're about to do will hit someone
        else (roughly).

        Check we aren't gonna run into a wall either

        :param resultant_y:
        :param resultant_x:
        :return: bool
        """

        print ("Safety check. Our robot is at, x, y", self.world.our_robot.x, self.world.our_robot.y)

        # we're aiming for these co-ordinates, but realistically we aren't gonna move in a straight line
        # so let's see if there's any robots in our path (but not loop through every possibility, just every +padding
        # certaintly not most efficient way but who cares anymore...
        check_x = self.world.our_robot.x
        check_y = self.world.our_robot.y

        if self.world.safety_padding <= 0:
            self.world.safety_padding = 1

        while check_x <= resultant_x and check_y <= resultant_y:
            # is this co-ordinate within (z) units of other robots? if so we need to stop and think
            robots = [self.world.teammate, self.world.their_defender, self.world.their_attacker]
            for robot in robots:
                if (abs(resultant_x - robot.x) <= self.world.robot_safety_padding) and abs(
                                resultant_y - robot.y) <= self.world.robot_safety_padding:

                    print ("TOo close to another robot")
                    # if this robot is moving, don't do anything
                    if robot.speed > 5:
                        return False
                    # robot is unlikely to move, let's re-route
                    else:
                        # this needs to be implemented
                        return False

            check_x += self.world.safety_padding
            check_y += self.world.safety_padding

        # check if we're going to run into a wall
        print ("Trying to move to resultant_x, resultant_y", resultant_x, resultant_y)
        if self.world.pitch_boundary_bottom - self.world.safety_padding <= resultant_y:
            print("Trying to go somewhere greater than the greatest (bottom) boundary")
            return False
        if self.world.pitch_boundary_top + self.world.safety_padding >= resultant_y:
            print("Trying to go somewhere less than the lowest (top) boundary")
            return False
        if self.world.pitch_boundary_left + self.world.safety_padding >= resultant_x:
            print("Trying to go somewhere less than the left boundary")
            return False
        if self.world.pitch_boundary_right - self.world.safety_padding <= resultant_x:
            print("Trying to go somewhere greater than the right boundary")
            return False

        # we're good to move here
        return True

    @staticmethod
    def calculate_kick_power(distance):
        """
        Given a distance to kick, crudely calculates the power for the kicker; this is only used for ball kicking atm
        :param distance:
        """
        # power is between 0.0 and 1.0, assume distance given is between 0.0 and 2.0. this function needs improving
        power = (distance / 2)
        print ("calculated power is ", power)

        if power > 1:
            return 1

        return power

    @staticmethod
    def calculate_motor_duration_turn(angle_to_rotate):
        """
        :param angle_to_rotate: given in degrees
        """
        # crude angle -> duration conversion
        duration = 100 + (abs(angle_to_rotate) * 5)

        if angle_to_rotate < 0:
            duration = -duration

        return -duration

    @staticmethod
    def calculate_motor_duration(distance):
        """
        Given a distance to travel, we need to know how long to run the motor for
        :param distance: provided in metres
        """

        # some crude distance -> duration measure. assumes 10cm of movement equates to 100ms, past the initial 100ms
        duration = 50 + (distance * 8)
        return duration
