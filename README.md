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
- Left wheel #4
- Right wheel #5
- Kicker #3
- Right grabber #2
- Left grabber #1

# Models
Our system is made up of simply four models: `Ball`, `World`, `Robot` and `Goal`.

# Tasks, vision and movement
These commands take data from the vision system and integrate it with our lower-level Arduino commands, allowing
the robot to perform actual tasks.

Run the command:
```
python Runner.py pitch_number color task
```

- `pitch_number` is `0` or `1`
- `color` is `yellow` or `blue` depending on our robot's color
- `task` can be `vision`, `task_move_to_ball`, `task_move_and_grab_ball`, `task_kick_ball_in_goal`)

## Move to ball
``task_move_to_ball`` will gradually move the robot to the ball. It does this through an iterative method; it first
will rotate to point to the ball, it will then wait for vision feedback, and repeat the process until the robot
is facing it within ±25 degrees of accuracy. It then moves to the ball gradually, doing the same. Every time it moves forward, it will
repeat the process of rotation - this means at each stage of movement, it will re-rotate to face the ball.

It will finally stop when within a displacement of 30 (arbitrary units) of the ball.

## Move and grab ball
This is the same as ``task_move_to_ball`` except that when it reaches the ball, it opens the grabber.

## Kick ball in goal
Given the goal's co-ordinates, it will keep rotating until it's happy with the angle, based on vision data, and then will
open the grabber and kick the ball (it assumes the ball is already caught).

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