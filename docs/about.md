# Runner.py
This is the main 'controller' file, that connects vision and communication together

`run.py` continuous loops, getting data from the vision system and updating our 'world'. It
recognises the ball from the vision data, then updates the vector values of the robot, ball and
other objects, within the World object.


# Models
## PitchObject
An abstract class that is "inherited" by robot, vector and ball

## World
This model contains other models: the pitch, our robot, and the ball.

## Pitch
## Coordinate
## Vector
## Robot
## Ball