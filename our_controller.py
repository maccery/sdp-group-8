from communication.controller import Arduino, Communication
from planning.models import World
from vision.vision import Vision, Camera, GUI
from postprocessing.postprocessing import Postprocessing
from preprocessing.preprocessing import Preprocessing
import vision.tools as tools


class Controller:
    """
    Our main file for controlling the robot; interfaces with vision and communications to perform actions
    """

    def __init__(self):
        # Set up the Arduino communications
        self.arduino = Arduino()

        # Set up camera for frames
        self.camera = Camera(port=video_port, pitch=self.pitch)
        frame = self.camera.get_frame()
        # gets center of the frame based on the table croppings,
        center_point = self.camera.get_adjusted_center()

        # Set up vision
        self.calibration = tools.get_colors(pitch)
        self.vision = Vision(
            pitch=pitch, color=color, our_side=our_side,
            frame_shape=frame.shape, frame_center=center_point,
            calibration=self.calibration)

        # Set up postprocessing for vision
        self.postprocessing = Postprocessing()

        # Set up GUI
        self.GUI = GUI(calibration=self.calibration, arduino=self.arduino, pitch=self.pitch, capture=self.camera.capture)

        self.color = color
        self.side = our_side

        self.preprocessing = Preprocessing()
        self.comms_manager = CommunicationsManager(self.arduino)


    def main(self):
        """
        Loops through frames; updates world; runs strategy on world state
        """
        counter = 1L
        timer = time.clock()

        try:
            c = True
            while c != 27:  # the ESC key
                # gets frame, and sets whether we are using real video feed or calibration one
                frame = self.camera.get_frame(self.GUI.calibration_loop)

                pre_options = self.preprocessing.options
                # Apply pre-processing methods toggled in the UI
                preprocessed = self.preprocessing.run(frame, pre_options)
                frame = preprocessed['frame']
                if 'background_sub' in preprocessed:
                    cv2.imshow('bg sub', preprocessed['background_sub'])

                # Find object positions
                # model_positions have their y coordinate inverted

                model_positions, regular_positions = self.vision.locate(frame)
                if not regular_positions["ball"]:
                    regular_positions["ball"] = {
                        "x": self.strategy.world.ball.x,
                        "y": self.strategy.world.pitch.height - self.strategy.world.ball.y
                    }
                model_positions = self.postprocessing.analyze(model_positions)

                # ###################### PLANNING ########################
                # Find appropriate action
                self.strategy.update_world(model_positions, self.postprocessing.attacker_lost)
                self.strategy = self.strategy.execute()

                # Information about the grabbers from the world
                grabbers = {
                    'red': self.strategy.world.our_defender.catcher_area,
                    'orange': self.strategy.world.our_defender.caught_area,
                    'black': self.strategy.world.our_defender.area_behind_catcher,
                    'teal': self.strategy.world.our_defender.front_area,
                }

                # Information about states
                defender_state = [repr(self.strategy), self.strategy.state]
                # ######################## END PLANNING ###############################

                # Use 'y', 'b', 'r' to change color.
                c = waitKey(2) & 0xFF
                fps = float(counter) / (time.clock() - timer)

                # Draw vision content and actions
                self.GUI.draw(
                    frame, model_positions, regular_positions, fps,
                    defender_state, grabbers,
                    our_color=self.color, our_side=self.side, key=c, preprocess=pre_options)
                counter += 1

        except Exception as e:
            print e.message
            self.comms_manager.shutdown()
            raise

        finally:
            # Write the new calibrations to a file.
            tools.save_colors(self.pitch, self.calibration)
            self.comms_manager.shutdown()
            if self.arduino.isOpen:
                self.arduino.close()

