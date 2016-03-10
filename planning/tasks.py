import time

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
            # if the ball is in the defender region, this is our primary task
            self.task_grab_rotate_kick()

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
            if self.task_move_and_grab_ball():
                self.task_kick_ball_in_goal()

        # always return false, this means this task will keep running
        return False

    def task_penalty(self):
        """
        Robot will aim to take a penalty, playing by the penalty rules
        """
        pass

    """
    Big tasks; these are made up of smaller tasks
    """

    def task_vision(self):
        pass

    def task_rotate_and_grab(self):
        # rotate to face the ball
        if self.rotate_to_ball():
            # wait till ball has stopped
            print('ball speed', self._world.ball.speed)
            if self._world.ball.speed < 5:
                # move to the ball
                if self.task_move_to_ball():
                    if self.ungrab_ball():
                        if self.grab_ball():
                            return self.ball_received()
                        return False
                    return False
                else:
                    return False
            else:
                return False
        else:
            return False

    # Assuming we're facing the right direction
    def task_grab_rotate_kick(self):
        if self.move_to_ball():
            if self.ball_received():
                # grab the ball we've just be given
                if self.grab_ball():
                    # rotate to face the other robot
                    if self.rotate_to_alignment(self._world.teammate.x, self._world.teammate.y):
                        # kick ball to teammate
                        distance = self._world.our_robot.get_displacement_to_point(self._world.teammate.x,
                                                                                   self._world.teammate.y)
                        if self.kick_ball(distance_to_kick=distance):
                            # check ball reached teammate
                            return self.ball_received_by_teammate()
                        return False
                    return False
                return False
            return False
        return False

    def task_move_to_ball(self):
        print("move_to_ball command called")
        # If the ball isn't moving, we can just move to it
        if self._world.ball.speed < 5:
            if self.rotate_to_ball():
                return self.move_to_ball()
            else:
                return False
        # If the ball IS moving, we need to predict where it's going and move there...
        else:
            if self.rotate_to_ball():
                return self.move_to_ball()
            return False

    def task_move_and_grab_ball(self):
        # If we're happy with rotation and movement, grab the ball
        if self.rotate_to_ball():
            if self.move_to_ball():
                # self.ungrab_ball()
                return self.grab_ball()
            return False
        # Otherwise return false, and get more data from vision
        else:
            return False

    def task_kick_ball_in_goal(self):
        # If we're happy with rotation to face goal, ungarb and kick the ball
        if self.rotate_to_alignment(self.world.their_goal.x, self.world.their_goal.y):
            if self.ungrab_ball():
                return self.kick_ball()
            return False
        # Otherwise return false, and get more data from vision
        else:
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

        print("Move to these co-ordinates: (", x, ",", y, ")")

        # Calculate how long we need to run the motor for
        distance = self._world.our_robot.get_displacement_to_point(x, y)

        print("Need to move this distance: ", distance)

        if distance < 30:
            return True
        else:
            calculated_duration = self.calculate_motor_duration(distance)
            print ("Running for duration: ", calculated_duration)

            # Tell arduino to move for the duration we've calculated
            self._communicate.move_duration(calculated_duration)

            # Wait until this task has completed
            print("We're sleeping for a bit while arudino gets it shit together", calculated_duration)
            time.sleep(calculated_duration / 1000)
            # Returns false which means we'll get more data from vision first, run this function again, to verify ok
            return False

    def rotate_to_ball(self):
        print ("rotating ball")
        return self.rotate_to_alignment(self._world.ball.x, self._world.ball.y)

    def move_to_ball(self):
        return self.move_to_coordinates(self._world.ball.x, self._world.ball.y)

    def rotate_to_alignment(self, x, y):
        """
        Given a specific robot, it will rotate to face a specific angle

        :param x:
        :param y:
        """
        print ("robots coordinates", self._world.our_robot.x, self._world.our_robot.y)
        print("Rotate to face these co-ordinates: (", x, ",", y, ")")
        angle_to_rotate = self._world.our_robot.get_rotation_to_point(x, y)
        distance = self._world.our_robot.get_displacement_to_point(x, y)

        print("calculated angle is ", angle_to_rotate)
        print("calculated distance is ", distance)
        # If the angle of rotation is less than 15 degrees, leave it how it is
        if (15 >= angle_to_rotate >= -15 and distance > 40) or (10 >= angle_to_rotate >= -10 and distance <= 40):
            print("We're happy with the angle, no more rotation")
            return True
        else:
            duration = self.calculate_motor_duration_turn(angle_to_rotate)
            print("turning for duration ", duration)
            wait_time = self._communicate.turn(duration)
            print("We're sleeping for a bit while arudino gets it shit together", wait_time)
            time.sleep(abs(wait_time))
            # Returns false which means we'll get more data from vision first, run this function again, to verify ok
            return False

    def ungrab_ball(self):
        wait_time = self._communicate.ungrab()
        time.sleep(wait_time)
        return True

    def grab_ball(self):
        print('grabbing')
        wait_time = self._communicate.grab()
        time.sleep(wait_time)
        return True

    def kick_ball(self, distance_to_kick=None):
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

    def ball_received(self):
        # calculate displacement from us to ball
        distance = self._world.our_robot.get_displacement_to_point(self._world.ball.x, self._world.ball.y)

        if distance < 30:
            return True
        else:
            return False

    def ball_received_by_teammate(self):
        # calculate displacement from us to ball
        distance = self._world.teammate.get_displacement_to_point(self._world.ball.x, self._world.ball.y)

        if distance < 30:
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

    def safety_check(self, distance_from_us=30):
        """
        Before any movement is called, this is called. This essentially checks if the movement we're about to do will hit someone
        else (roughly).
        :param distance_from_us We move in iterations, this specifies the amount of movement we're literally just about to do
        :return: bool
        """

        # we need to work out the co-ordinates of where we roughly plan to be after this movement
        # we can do this by adding the distance onto the direction we're facing
        resultant_x = self._world.our_robot.y
        resultant_y = self._world.our_robot.y

        # is this co-ordinate within (z) units of other robots? if so we need to stop and think
        robots = [self._world.teammate, self._world.their_defender, self._world.their_attacker]
        for robot in robots:
            if (-20 <= (resultant_x - robot.x) <= 20) and (-20 <= (resultant_y - robot.y) <= 20):
                # danger, the robot is very close

                if robot.speed > 5:
                    return False

    @staticmethod
    def calculate_kick_power(distance):
        """
        Given a distance to kick, crudely calculates the power for the kicker; this is only used for ball kicking atm
        :param distance:
        """
        # power is between 0.0 and 1.0, assume distance given is between 0.0 and 2.0. this function needs improving
        power = (distance / 2)

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
        duration = 100 + (distance * 8.5)
        return duration
