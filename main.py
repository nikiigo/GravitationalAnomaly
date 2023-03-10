import logging
import sys
from numpy import sqrt, cbrt, pi, arccos

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)


class Vector:

    # Initialize 3D Coordinates of the Vector
    def __init__(self, x, y, z):
        if not (not (isinstance(x, int) or isinstance(x, float)) or not (
                isinstance(y, int) or isinstance(y, float)) or not (isinstance(z, int) or isinstance(z, float))):
            self.x = x
            self.y = y
            self.z = z
        else:
            raise ValueError

    # Method to calculate magnitude of a Vector
    def magnitude(self):

        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    # Method to calculate Unit Vector
    def unit(self):

        return Vector(self.x / self.magnitude(), self.y / self.magnitude(), self.z / self.magnitude())

    # Method to calculate an angle between 2 Vectors
    def angle(self, v):

        if isinstance(v, Vector):
            return arccos((self ^ v) / (self.magnitude() * v.magnitude()))
        else:
            raise ValueError

    # Method to add to Vector
    def __add__(self, v):

        if isinstance(v, Vector):
            return Vector(self.x + v.x, self.y + v.y, self.z + v.z)
        else:
            raise ValueError

    # Method to subtract 2 Vectors
    def __sub__(self, v):

        if isinstance(v, Vector):
            return Vector(self.x - v.x, self.y - v.y, self.z - v.z)
        else:
            raise ValueError

    # Method to calculate the dot product of two Vectors
    def __xor__(self, v):

        if isinstance(v, Vector):
            return self.x * v.x + self.y * v.y + self.z * v.z
        else:
            raise ValueError

    # Method to calculate the cross product of 2 Vectors
    def __mul__(self, v):

        if isinstance(v, int) or isinstance(v, float):
            return Vector(self.x * v, self.y * v, self.z * v)
        elif isinstance(v, Vector):
            return Vector(self.y * v.z - self.z * v.y,
                          self.z * v.x - self.x * v.z,
                          self.x * v.y - self.y * v.x)
        else:
            raise ValueError

    # Method to define the representation of the Vector
    def __repr__(self):

        out = "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"
        return out


def decdeg2dms(dd):
    mult = -1 if dd < 0 else 1
    mnt, sec = divmod(abs(dd) * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return mult * deg, mult * mnt, mult * sec


if __name__ == "__main__":
    # Define a mountain as a truncated cone with height and radius in meters
    h = 1080
    r1 = 3000
    r2 = 50
    vol = pi / 3 * h * (r1 ** 2 + r1 * r2 + r2 ** 2)
    vol1 = vol / 5

    # Define gravitation in a flat gravitational field without mountain in m/s^2 and gravitational constant
    gf = 9.81
    fvece = Vector(0, 0, -gf)
    gc = 6.67e-11

    # Define mass density of some rocks in kg/m^3
    d: tuple[float, float, float, float, float] = (2000, 2500, 3000, 3500, 4000)

    # Model cone as 1 sphere (1 point model of centers of masses)
    # Calculate coordinates of this point
    zc = (r2 * h ** 2 / 2 + (r1 - r2) * h ** 2 / 6) / (r2 * h + (r1 - r2) * h / 2)
    # If the plumb is on the level of the mountain foot, and it is the center of coordinates now then this is the vector
    # to the center of the mass:
    mvecp = Vector(0, 0, 0)
    mvec = Vector(-r1, 0, zc)

    # Model cone as 5 spheres (5 points model of centers of masses)
    # Split the cone on 5 equal volumes (one is upper part of the mountain
    # and 4 others are at the foot of the mountain)
    # Calculate coordinates of these points
    rs = cbrt(1 / 5 * (r1 ** 3 - r2 ** 3) + r2 ** 3)
    hs2 = h * (rs - r2) / (r1 - r2)
    hs1 = h - hs2
    logging.debug(f'Calculated split parameters are: rs = {rs} hs2 = {hs2} hs1 = {hs1}')
    z2c = (r2 * hs2 ** 2 / 2 + (rs - r2) * hs2 ** 2 / 6) / (r2 * hs2 + (rs - r2) * hs2 / 2)
    z1c = (rs * hs1 ** 2 / 2 + (r1 - rs) * hs1 ** 2 / 6) / (rs * hs1 + (r1 - rs) * hs1 / 2)
    x1c = (r1 - (r1 - rs) * z1c / hs1) * 4 / (3 * pi)
    y1c = x1c
    logging.debug(f'Coordinates are: z2c = {z2c} z1c = {z1c} x1c = {x1c}')

    # If the plumb is on the level of the mountain foot, and it is the center of coordinates now then these are
    # the vectors to the centers of the masses:
    mvec1 = Vector(x1c - r1, y1c, z1c)
    mvec2 = Vector(-x1c - r1, y1c, z1c)
    mvec3 = Vector(-x1c - r1, -y1c, z1c)
    mvec4 = Vector(x1c - r1, -y1c, z1c)
    mvec5 = Vector(-r1, 0, z2c + hs1)
    logging.debug(f'Vectors to the centers of the masses from the plumb:'
                  f'{str(mvec1)}, {str(mvec2)}, {str(mvec3)}, {str(mvec4)}, {str(mvec5)}')

    for den in d:
        logging.info(f'the density is: {str(den)}')
        # we can find out the resulting unit force vector for the 5 points model as:
        fvec5m = (mvec1.unit() * (gc * vol1 * den / mvec1.magnitude() ** 2) +
                  mvec2.unit() * (gc * vol1 * den / mvec2.magnitude() ** 2) +
                  mvec3.unit() * (gc * vol1 * den / mvec3.magnitude() ** 2) +
                  mvec4.unit() * (gc * vol1 * den / mvec4.magnitude() ** 2) +
                  mvec5.unit() * (gc * vol1 * den / mvec5.magnitude() ** 2))
        logging.info(f'the resulting force vector in the 5 points model: {str(fvec5m)}')

        fvec1m = mvec.unit() * (gc * vol * den / mvec.magnitude() ** 2)
        logging.info(f'the resulting force vector in the 1 point model: {str(fvec1m)}')

        # Calculate angle between plumb line at the foot of the mountain and the line without mountain
        # the angle in accordance with 5 point model:
        angle5 = (fvece + fvec5m).angle(fvece)
        # the angle in accordance with 1 point model:
        angle1 = (fvece + fvec1m).angle(fvece)
        print("-----------------------------------------------------------------------------------------------------")
        print(f'For rock density {den} kg/m^3')
        print('The plumb is at the level of the foot of the mountain')
        print("-----------------------------------------------------------------------------------------------------")
        print(f'5 points model predicts that the angle is {decdeg2dms(angle5 / pi * 180)} degrees, minutes, seconds')
        print(f'1 point model  predicts that the angle  is {decdeg2dms(angle1 / pi * 180)} degrees, minutes, seconds')
        print(f'The difference is {(angle5 - angle1) / angle5 * 100} percents')
