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

# Basic commands
- In the python interpreter, write the following: ``from communication import Controller as ct``
- Still in the python interpreter, write the following: ``tmp = ct("/dev/ttyACM0", ack_tries=10)`` (Note: ttyACM0 should be the channel that the arduino is on, though it is usually ttyACM0).

## Move forward for given distance
The controller object is now held in ``ct``, and you can issue commands as normal methods to the object ``ct``. ``ct.move()`` is used to move the robot and ct.kick() is used to activate the kicker. 

An example use of ``move()`` is as follows:

```
ct.move_distance(x=200)
```

This will move the robot "forward" by 200 units. **These are arbitrary units** (you can see how these units equate to distance using [this spreadsheet](https://docs.google.com/spreadsheets/d/1Wiwqk3x_8VJf5Og2c1d-C5w0c_pkGMPa_0722nI-RGs/edit). Setting ``x=-100`` would move the robot "backwards" by 100 units. The ``x`` refers to the x-axis, so forward and backwards on 1-dimensional plane. 

**Note: moving left/right (on the y-axis) is not properly implemented yet**

- You can also use ``y`` which turns the robot, for example setting ``y=100`` would turn the robot 100 units clockwise, and setting ``y=-200`` would turn the robot 200 units counter-clockwise.

## Move forward for given duration
`x` is given in ms.

```
ct.move_duration(200)
```

## Run specific motor 
```
ct.run_motor(id, power, duration)
```

## Turn at a certain angle
Note `angle` is given in radians. However this function is not properly implemented yet.

```
ct.turn_clockwise(angle)
```

## Kick the ball at a certain power
Here you can specific how hard to kick it. The ``power`` is given between -1.0 and 1.0
```
ct.kick(power)
```


# Engine IDs
-  wheel #4
- Right wheel #5
- Kicker #3
- Right grabber #2
- Left grabber #1

# Models
Our system is made up of simply four models: `Ball`, `World`, `Robot` and `Goal`.

In `models.py`, the function `update_positions` takes the data from the vision system and saves the locations of the robot.


# Playing football (and smaller tasks)
These commands take data from the vision system and integrate it with our lower-level Arduino commands, allowing
the robot to perform actual tasks.

In `Runner.py` you need to specify the color and team of both our robot and its teammate. This is done in the ``initiate_world`` function.. You also need to give the
coordinates of the pitch. THIS CHANGES DEPENDING IF WE ARE LEFT OR RIGHT SIDE OF THE PITCH (as seen by the camera)

In `communinication/controller.py` you must edit the port of the Arduino USB. These are hardcoded but we plan to put them as parameters at some point. 

Once done, simply run the command:
```
python Runner.py
```

This will the start the task runner.

After it's connected to the Arduino you'll be asked which task you want to execute, simply enter it and press enter (tasks below).
Once the task is successfully completed, you can give it another task.

## Play football: defending
To make our robot act as a defender you simply run `task_defender`. If the ball is in our half, our robot will go to the ball, grab it and pass
to our teammate. If the ball is in the attacking region, our robot will strive to be half way between the ball and the goal at any given time.
If the ball is in both the attacking and defending region, if our teammate is closer - it will let the teammate get it, otherwise we will go to get it.

To kick off first, run `task_defender_kick_off`. This will kick the ball into the attacking region for our teammate to get, then continue its regular defender task.

In both cases, this task will never end. It cannot be completed.

## Playing football: penalty
Assuming the ball is with our robot, with grabbers closed, run `task_penalty` and our robot will shoot the ball at the goal. Once completed, you can give
it other tasks. It will kick the ball after a random amount of time between 2-10s to "surprise" the teammate.

## Playing football: penalty goalie
``task_penalty_goalie``. The robot will rotate to look at the ball, open grabbers, then grab them after a specified time.

## Task: Move to ball
``task_move_to_ball`` will gradually move the robot to the ball. It does this through an iterative method; it first
will rotate to point to the ball, it will then wait for vision feedback, and repeat the process until the robot
is facing it within ±25 degrees of accuracy. It then moves to the ball gradually, doing the same. Every time it moves forward, it will
repeat the process of rotation - this means at each stage of movement, it will re-rotate to face the ball.

It will finally stop when within a displacement of 30 (arbitrary units) of the ball.

## Task: Move and grab ball
Run ``task_move_and_grab_ball``. This is the same as ``task_move_to_ball`` except that when it reaches the ball, it opens the grabber.

## Task: Kick ball in goal
Given the goal's co-ordinates, it will keep rotating until it's happy with the angle, based on vision data, and then will
open the grabber and kick the ball (it assumes the ball is already caught).


## Task: Receiving and grabbing
Run the command ``task_rotate_and_grab``. This will rotate the robot to our teammate, and grab the ball when it's within reach.

## Task: Receive, turn and pass
Run the command ``task_grab_rotate_kick``. This will wait till we've received the ball, then grab it, then rotate our robot to the teammate,
then kick it at them. The function that calculates how hard to kick it is in ``tasks.py``, called `calculate_kick_power`.

## Task: Intercepting
One way to get the robot 'intercepting' the ball, is simply to tell it to move and grab the ball. Simply run ``task_move_and_grab_ball``.

# Tests
We have written some tests which are contained within the `tests` folder. These test things like our angle calculation and our
binary sender.

# File structure
`communication/controller.py` is our file that controls which messages to send to the Arduino, low-level tasks such as 'move forward' and 'open kicker'.

`vision/` folder contains all our code relating to the vision system

`planning/models.py` has our model structures.

`planning/tasks.py` is our file that contains the tasks that can be performed by the robot, such as 'move and grab ball'

`Runner.py` is the main controller file that takes command line input, and executes the appropriate command, linking together with visino.

`arduino/controller/controller.ino` contains the code that is programmed onto the Arduino, for receiving messages and executing them.
