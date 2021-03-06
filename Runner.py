from planning.models import World, Task
from planning.logger import Logger
from postprocessing import PostProcessing
from vision.vision import Vision, GUI
from vision.vision import dump_calibrations
import sys
from vision import tools
from cv2 import waitKey
import cv2
import time


class Runner(object):
    def __init__(self):
        # Set up Arduino communications.
        # self.robot =
        self.calib_file = "vision/calibrations/calibrations.json"
        self.vision = Vision(self.calib_file)
        self.gui = GUI(self.vision.calibrations)
        self.task = None

        # Set up world
        self.world = World(self.calib_file)

        # Set up post-processing
        self.postprocessing = PostProcessing()

        self.wait_for_vision = True

    def run(self):
        """
       Constantly updates the vision feed, and positions of our models
       """

        counter = 0
        timer = time.clock()

        # wait 10 seconds for arduino to connect
        print("Connecting to Arduino, please wait till confirmation message")
        time.sleep(4)

        # This asks nicely for goal location, etc
        self.initiate_world()

        try:
            c = True

            while c != 27:  # the ESC key
                if self.task is None:
                    print("Please enter the task you wish to execute:")
                    self.task = sys.stdin.readline().strip()

                t2 = time.time()
                # change of time between frames in seconds
                delta_time = t2 - timer
                timer = t2

                # getting all the data from the world state
                data, modified_frame = self.vision.get_world_state()

                # update the gui
                self.gui.update(delta_time, self.vision.frame, modified_frame, data)

                # Update our world with the positions of robot and ball
                self.world.update_positions(data)

                # Only run the task every 20 cycles, this allows us to catch up with vision
                if counter % 21 == 0:
                    self.task_execution()

                key = cv2.waitKey(4) & 0xFF
                if key == ord('q'):
                    break
                    # self.save_calibrations()

                counter += 1

        finally:
            pass
            # self.robot.stop()

    def initiate_world(self):

        print("Which side are we?")
        self.world.our_side = sys.stdin.readline().strip()

        if self.world.our_side == "left":
            self.world.defender_region.left = 40 # 40, 320
            self.world.defender_region.right = 320 # 320, 600
            self.world.attacker_region.left = 320 # 40, 320
            self.world.attacker_region.right = 600 #320, 600
            self.world.our_goal.x = 40 # 600 or 40
            self.world.our_goal.y = 235
            self.world.their_goal.x = 600 # 40 or 600
            self.world.their_goal.y = 245
        else:
            self.world.defender_region.left = 320 # 40, 320
            self.world.defender_region.right = 600 # 320, 600
            self.world.attacker_region.left = 40 # 40, 320
            self.world.attacker_region.right = 320 #320, 600
            self.world.our_goal.x = 600 # 600 or 40
            self.world.our_goal.y = 235
            self.world.their_goal.x = 40 # 40 or 600
            self.world.their_goal.y = 245

        self.world.our_robot.team_color = "blue"
        self.world.teammate.team_color = "blue"
        self.world.their_attacker.team_color = "yellow"
        self.world.their_defender.team_color = "yellow"
        self.world.our_robot.group_color = "green"
        self.world.teammate.group_color = "pink"

        self.world.their_attacker.group_color = "pink"
        self.world.their_defender.group_color = "green"


        self.world.safety_padding = 25
        self.world.pitch_boundary_left = 40
        self.world.pitch_boundary_right = 600
        self.world.pitch_boundary_bottom = 450
        self.world.pitch_boundary_top = 30

    def task_execution(self):
        """
        Executes the current task
        """

        # Only execute a task if the robot isn't currently in the middle of doing one
        print ("Task: ", self.task)
        task_to_execute = None
        if self.task == 'task_vision':
            task_to_execute = self.world.task.task_vision
        if self.task == 'task_move_to_ball':
            task_to_execute = self.world.task.task_move_to_ball
        if self.task == 'task_kick_ball_in_goal':
            task_to_execute = self.world.task.task_kick_ball_in_goal
        if self.task == 'task_move_and_grab_ball':
            task_to_execute = self.world.task.task_move_and_grab_ball
        if self.task == 'task_rotate_and_grab':
            task_to_execute = self.world.task.task_rotate_and_grab
        if self.task == 'task_grab_rotate_kick':
            task_to_execute = self.world.task.task_grab_rotate_kick
        if self.task == 'task_defender':
            task_to_execute = self.world.task.task_defender
        if self.task == 'task_defender_kick_off':
            task_to_execute = self.world.task.task_defender_kick_off
        if self.task == 'task_attacker':
            task_to_execute = self.world.task.task_attacker
        if self.task == 'task_attacker_kick_off':
            task_to_execute = self.world.task.task_attacker_kick_off
        if self.task == 'task_penalty':
            task_to_execute = self.world.task.task_penalty
        if self.task == 'task_goalie':
            task_to_execute = self.world.task.task_penalty_goalie

        # if there's a task to do, let's try it
        if self.task:
            # if it's executed fine, then we've completed the task. otherwise we're going to loop round and try again
            if task_to_execute():
                self.task = None
                print("Task: COMPLETED")

    def save_calibrations(self):
        dump_calibrations(self.vision.calibrations, self.calib_file)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    Runner().run()
