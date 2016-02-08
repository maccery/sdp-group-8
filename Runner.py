from milestone2.models import World, Task
from postprocessing import PostProcessing
from vision.vision import Vision, GUI
from vision.vision import dump_calibrations
from vision import tools
from cv2 import waitKey
import cv2
import time


class Runner(object):
    def __init__(self, pitch, color, video_port=0, comm_port='/dev/ttyACM0', comms=1):
        """
        Parameters:
            [int] pitch        0 - left pitch, 1 - right pitch
            [string] color     the color of the team(yellow or blue)
            [int] video_port   port number for the camera
            [string] comm_port port number for the Arduino.
        """
        assert pitch in [0, 1]
        assert color in ['yellow', 'blue']

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

    def run(self, task):
        """
        Ready your sword, here be dragons.
        """

        counter = 1L
        timer = time.clock()

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

                # Recgonise the ball and our robot; note these functions don't currently return vectors....
                ball_vector = self.vision.recognize_ball()
                our_robot_vector = self.vision.recognize_plates()

                # Update the vector of our ball and our robot in the world; vector describes position, size, velocity...
                self.world.ball.vector = ball_vector
                self.world.our_robot.vector = our_robot_vector

                # Execute the given task requested
                if self.world.our_robot.is_busy is False:
                    if task is 'move_to_ball':
                        self.world.task.move_to_ball(ball_vector)
                    if task is 'kick_ball_in_goal':
                        self.world.task.kick_ball_in_goal()
                    if task is 'move_and_grab_ball':
                        self.world.task.move_and_grab_ball()

                key = cv2.waitKey(4) & 0xFF
                if key == ord('q'):
                    end = True
                    # self.save_calibrations()

                counter += 1

        finally:
            pass
            # self.robot.stop()

    def save_calibrations(self):
        dump_calibrations(self.vision.calibrations, self.calib_file)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    # Havent done anything for right pitch yet. So choose option 0.
    parser.add_argument("pitch", help="[0] Left pitch, [1] Right pitch")
    # parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    # parser.add_argument("attack_defend", help="Are we attacking or defending? - ['attack', 'defend']")
    # parser.add_argument(
    #     "-n", "--nocomms", help="Disables sending commands to the robot.", action="store_true")

    args = parser.parse_args()
    # if args.nocomms:
    #     c = Runner(
    #         pitch=int(args.pitch), color=args.color, our_side=args.side, attack_defend='attack', comms=0).run()
    # else:
    c = Runner(
            pitch=int(args.pitch), color=args.color).run()
