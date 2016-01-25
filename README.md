# Setup
- Firstly clone this repository onto DICE, or your machine
- Navigate to this folder on your machine

## Programming the robot
- Open up the application Arduino (installed on Dice, or [download](https://www.arduino.cc))
- Load the ``controller.ino`` file from ``arduino/controller`` in Ardunio from File > Open.
- Connect the robot to the computer using micro USB cable
- Unplug the battery
- Verify the code by clicking the 'tick' icon.
- Upload the file onto the arduino by clicking the 'up arrow' icon.
- Unplug USB cable

# Starting the robot
- Make sure the battery is charged and plugged in
- Make sure the micro USB cable is unplugged
- Connect the SRF USB stick in
- Launch Terminal
- Navigate to the main folder.
- Enter the python interpreter by typing ``python``
- In the python interpreter, write the following: ``from communication import Controller as ct``
- Still in the python interpreter, write the following: ``tmp = ct("/dev/ttyACM0", ack_tries=10)`` (Note: ttyACM0 should be the channel that the arduino is on, though it is usually ttyACM0).

## Controlling the robot
The controller object is now held in ``ct``, and you can issue commands as normal methods to the object ``ct``. ``ct.move()`` is used to move the robot and ct.kick() is used to activate the kicker. 

An example use of ``move()`` is as follows:

```
ct.move(x=200)
```

This will move the robot "forward" by 200 units. Setting ``x=-100`` would move the robot "backwards" by 100 units. The ``x`` refers to the x-axis, so forward and backwards on 1-dimensional plane. You can also use ``y`` which turns the robot, for example setting ``y=100`` would turn the robot 100 units clockwise, and setting ``y=-200`` would turn the robot 200 units counter-clockwise.

# Engine IDs

Back single wheel #1 (NOTE: Currently a ball-bearing)
Front left wheel #4
Front right wheel #5
Kicker #3
