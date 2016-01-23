# Setup
- Firstly clone this repository onto DICE, or your machine
- Navigate to this folder on your machine

## Programming the robot
- Open up the application Arduino (installed on Dice, or [download](https://www.arduino.cc))
- Load the ``test.ino`` file in Ardunio
- Connect the robot to the computer using micro USB cable
- Unplug the battery
- Load the file onto the robot
- Unplug USB cable

# Starting the robot
- Make sure the battery is charged and plugged in
- Make sure the micro USB cable is unplugged
- Connect the SRF USB stick in
- Launch Terminal
- Issue command: ``screen /dev/ttyACMX``, where X is the port number (it will be either 0, 1, 2 depending on which port you've plugged it into)
- Press reset button on Arduino (on the robot)
- On Terminal, start issuing commands depending on task 

## Controlling the robot
These are entered in Terminal using the keyboard
- W *move forward*
- S *move backward*
- A *move left*
- D *move right*
- 0 *REAR_WHEEL_MOTOR*
- 1 *LEFT_WHEEL_MOTOR*
- 2 *RIGHT_WHEEL_MOTOR*
- 3 *KICKER_MOTOR*

# Engine IDs

Back single wheel #1
Front left wheel #4
Front right wheel #5
Kicker #3
