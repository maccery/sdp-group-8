from Polygon.cPolygon import Polygon
from math import cos, sin, hypot, pi, atan2
from vision import tools
from milestone2.tasks import Task

# Width measures the front and back of an object
# Length measures along the sides of an object

ROBOT_WIDTH = 30
ROBOT_LENGTH = 45
ROBOT_HEIGHT = 10

BALL_WIDTH = 5
BALL_LENGTH = 5
BALL_HEIGHT = 5

GOAL_WIDTH = 140
GOAL_LENGTH = 1
GOAL_HEIGHT = 10


class Coordinate(object):
    def __init__(self, x, y):
        if x is None or y is None:
            raise ValueError('Can not initialize to attributes to None')
        else:
            self._x = x
            self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, new_x):
        if new_x == None:
            raise ValueError('Can not set attributes of Coordinate to None')
        else:
            self._x = new_x

    @y.setter
    def y(self, new_y):
        if new_y == None:
            raise ValueError('Can not set attributes of Coordinate to None')
        else:
            self._y = new_y

    def __repr__(self):
        return 'x: %s, y: %s\n' % (self._x, self._y)


class Vector(Coordinate):
    def __init__(self, x, y, angle):
        super(Vector, self).__init__(x, y)
        if angle is None or angle < 0 or angle >= (2 * pi):
            raise ValueError('Can not initialise attributes of Vector to None')
        else:
            self._angle = angle

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, new_angle):
        if new_angle == None or new_angle < 0 or new_angle >= (2 * pi):
            raise ValueError('Angle can not be None, also must be between 0 and 2pi')
        self._angle = new_angle

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and (self.__dict__ == other.__dict__))

    def __repr__(self):
        return ('x: %s, y: %s, angle: %s\n' %
                (self.x, self.y, self._angle))


class PitchObject(object):
    """
    Abstract class for describing objects on the pitch
    """

    def __init__(self, x, y, width, length, height, angle):
        if width < 0 or length < 0 or height < 0:
            raise ValueError('Object dimensions must be positive')
        else:
            self._width = width
            self._length = length
            self._height = height
            self._vector = Vector(x, y, angle)

    @property
    def width(self):
        return self._width

    @property
    def length(self):
        return self._length

    @property
    def height(self):
        return self._height

    @property
    def x(self):
        return self._vector.x

    @property
    def y(self):
        return self._vector.y

    @property
    def angle(self):
        return self._vector.angle

    @property
    def x(self):
        return self._vector.x

    @property
    def y(self):
        return self._vector.y

    @property
    def vector(self):
        return self._vector

    @vector.setter
    def vector(self, new_vector):
        if new_vector is None or not isinstance(new_vector, Vector):
            raise ValueError('The new vector can not be None and must be an instance of a Vector')
        else:
            self._vector = Vector(new_vector.x, new_vector.y, new_vector.angle)

    def get_generic_polygon(self, width, length):
        '''
        Get polygon drawn around the current object, but with some
        custom width and length:
        '''
        front_left = (self.x + length / 2, self.y + width / 2)
        front_right = (self.x + length / 2, self.y - width / 2)
        back_left = (self.x - length / 2, self.y + width / 2)
        back_right = (self.x - length / 2, self.y - width / 2)
        poly = Polygon((front_left, front_right, back_left, back_right))
        poly.rotate(self.angle, self.x, self.y)
        return poly[0]


class Robot(PitchObject):
    def __init__(self, zone, x, y, angle):
        # Inherit the super class (PitchObjects) initialiser code
        super(Robot, self).__init__(x, y, ROBOT_WIDTH, ROBOT_LENGTH, ROBOT_HEIGHT, angle)
        self._catcher = 'open'
        self._is_busy = False

    @property
    def catcher_area(self):
        """

        :return: Polygon
        """
        front_left = (self.x + self._catcher_area['front_offset'] + self._catcher_area['height'],
                      self.y + self._catcher_area['width'] / 2.0)
        front_right = (self.x + self._catcher_area['front_offset'] + self._catcher_area['height'],
                       self.y - self._catcher_area['width'] / 2.0)
        back_left = (self.x + self._catcher_area['front_offset'], self.y + self._catcher_area['width'] / 2.0)
        back_right = (self.x + self._catcher_area['front_offset'], self.y - self._catcher_area['width'] / 2.0)
        area = Polygon((front_left, front_right, back_left, back_right))
        area.rotate(self.angle, self.x, self.y)

        return area

    @catcher_area.setter
    def catcher_area(self, area_dict):
        self._catcher_area = area_dict

    @property
    def is_busy(self):
        return self._is_busy

    @is_busy.setter
    def is_busy(self, boolean):
        self._is_busy = boolean

    @property
    def catcher(self):
        return self._catcher

    @catcher.setter
    def catcher(self, new_position):
        assert new_position in ['open', 'closed']
        self._catcher = new_position

    def can_catch_ball(self, ball):
        """
        Get if the ball is in the catcher zone but may not have possession. This is done using the vision system
        to detect whether the ball is inside the catcher area
        """
        return self.catcher_area.isInside(ball.x, ball.y)

    def has_ball(self, ball):
        '''
        Gets if the robot has possession of the ball
        '''
        return (self._catcher == 'closed') and self.can_catch_ball(ball)

    def get_rotation_to_point(self, target_vector):
        """
        Calculates the rotation required to achieve alignment with given co-ordinates

        :param target_coordinates:
        :return: angle
        """

        delta_x = target_vector.x - self.x
        delta_y = target_vector.y - self.y
        displacement = hypot(delta_x, delta_y)
        if displacement == 0:
            theta = 0
        else:
            theta = atan2(delta_y, delta_x) - atan2(sin(self.angle), cos(self.angle))
            if theta > pi:
                theta -= 2 * pi
            elif theta < -pi:
                theta += 2 * pi
        assert -pi <= theta <= pi

        return theta

    def get_displacement_to_point(self, target_vector):
        """
        Uses the euclidean distance to calculate the displacement between this robot and a target co-ordinates

        :param target_coordinates:
        :return: displacement
        """

        delta_x = target_vector.x - self.x
        delta_y = target_vector.y - self.y
        displacement = hypot(delta_x, delta_y)

        return displacement


class Ball(PitchObject):
    def __init__(self, x, y, angle, velocity):
        super(Ball, self).__init__(x, y, angle, BALL_WIDTH, BALL_LENGTH, BALL_HEIGHT)


class Goal(PitchObject):
    def __init__(self, zone, x, y, angle):
        super(Goal, self).__init__(x, y, angle, 0, GOAL_WIDTH, GOAL_LENGTH, GOAL_HEIGHT)
        self._zone = zone

    @property
    def zone(self):
        return self._zone

    def __repr__(self):
        return ('zone: %s\nx: %s\ny: %s\nangle: %s\nvelocity: %s\ndimensions: %s\n' %
                (self._zone, self.x, self.y, self.angle, self.velocity, (self.width, self.length, self.height)))


class Pitch(object):
    def __init__(self, pitch_num):
        """
        :param pitch_num: Number of the pitch, as specified in the calibration file
        """

        # Parse the JSON data from the calibrations file which describes the pitch
        config_json = tools.get_croppings(pitch=pitch_num)

        # Work out the height and width of the pitch and update these parameters
        self._width = max([point[0] for point in config_json['outline']]) - min(
                [point[0] for point in config_json['outline']])
        self._height = max([point[1] for point in config_json['outline']]) - min(
                [point[1] for point in config_json['outline']])

        # Initialise the zones and create polygons to represent these zones
        self._zones = []
        self._zones.append(Polygon([(x, self._height - y) for (x, y) in config_json['Zone_0']]))
        self._zones.append(Polygon([(x, self._height - y) for (x, y) in config_json['Zone_1']]))
        self._zones.append(Polygon([(x, self._height - y) for (x, y) in config_json['Zone_2']]))
        self._zones.append(Polygon([(x, self._height - y) for (x, y) in config_json['Zone_3']]))

    def is_within_bounds(self, robot, x, y):
        """
        Checks whether the position/point planned for the robot is reachable
        """
        zone = self._zones[robot.zone]
        return zone.isInside(x, y)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


class World(object):
    """
    This class describes the environment; the pitch, the ball, the robots...
    """

    def __init__(self, pitch_num):
        self._pitch = Pitch(pitch_num)
        self._ball = Ball(0, 0, 0, 0)
        self._our_robot = Robot(0, 0, 0, 0)
        self._task = Task(self)

    @property
    def pitch(self):
        return self._pitch

    @property
    def ball(self):
        return self._ball

    @property
    def our_robot(self):
        return self._our_robot

    @property
    def task(self):
        return self._task