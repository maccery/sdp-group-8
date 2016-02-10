from milestone2.models import World, Task
from milestone2.logger import Logger
from postprocessing import PostProcessing
from multiprocessing import Process
from vision.vision import Vision, GUI
from vision.vision import dump_calibrations
from vision import tools
from cv2 import waitKey
import cv2
import time


class Runner(object):
    def __init__(self, pitch, color, task, video_port=0, comm_port='/dev/ttyACM0', comms=1):
        """
        Parameters:
            [int] pitch        0 - left pitch, 1 - right pitch
            [string] color     the color of the team(yellow or blue)
            [int] video_port   port number for the camera
            [string] comm_port port number for the Arduino.
        """
        assert pitch in [0, 1]
        assert color in ['yellow', 'blue']
        self.task = task
        self.pitch = pitch

        # Set up Arduino communications.
        # self.robot =
        self.calib_file = "vision/calibrations/calibrations.json"
        self.vision = Vision(self.calib_file)
        self.gui = GUI(self.vision.calibrations)

        # Set up world
        self.world = World(self.calib_file)

        # Set up post-processing
        self.postprocessing = PostProcessing()

        # Set up GUI
        self.color = color

        self.wait_for_vision = True

    def run(self):
        """
       Constantly updates the vision feed, and positions of our models
       """

        counter = 0
        timer = time.clock()

        # wait 10 seconds for arduino to connect
        print("waiting 10 seconds for Arduino to get its shit together")
        time.sleep(10)
        Logger.log_write("test")
        try:
            c = True
            # self.robot.ping()
            while c != 27:  # the ESC key
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
                if counter % 30 == 0:
                    self.task_execution()

                key = cv2.waitKey(4) & 0xFF
                if key == ord('q'):
                    break
                    # self.save_calibrations()

                counter += 1

        finally:
            pass
            # self.robot.stop()

    def task_execution(self):
        """
        Executes the current task
        """

        # Only execute a task if the robot isn't currently in the middle of doing one
        print ("task is ", self.task)
        task_to_execute = None
        if self.task == 'task_move_to_ball':
            task_to_execute = self.world.task.task_move_to_ball
        if self.task == 'task_kick_ball_in_goal':
            task_to_execute = self.world.task.task_kick_ball_in_goal
        if self.task == 'task_move_and_grab_ball':
            task_to_execute = self.world.task.task_move_and_grab_ball

        # if the task has executed, this will return true and we set our task as complete
        if task_to_execute:
            if task_to_execute():
                self.task = None
                print("Task completed ")

    def save_calibrations(self):
        dump_calibrations(self.vision.calibrations, self.calib_file)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    # Havent done anything for right pitch yet. So choose option 0.
    parser.add_argument("pitch", help="[0] Left pitch, [1] Right pitch")
    # parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    parser.add_argument("task")
    # parser.add_argument("attack_defend", help="Are we attacking or defending? - ['attack', 'defend']")
    # parser.add_argument(
    #     "-n", "--nocomms", help="Disables sending commands to the robot.", action="store_true")

    args = parser.parse_args()
    # if args.nocomms:
    #     c = Runner(
    #         pitch=int(args.pitch), color=args.color, our_side=args.side, attack_defend='attack', comms=0).run()
    # else:
    c = Runner(
            pitch=int(args.pitch), color=args.color, task=args.task).run()
