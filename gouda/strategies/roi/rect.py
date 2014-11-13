import collections

# TODO LH Duplicated in inselect

# Simple representations of Points and rectangles
Point = collections.namedtuple('Point', ['x', 'y'])
RectCoordinates = collections.namedtuple('Coordinates', ['x0', 'y0', 'x1', 'y2'])

class Rect(object):
    def __init__(self, r):
        x, y, width, height = r
        if x<0 or y<0 or width<0 or height<0:
            raise ValueError('Bad rectangle')
        self.x, self.y, self.width, self.height = x, y, width, height

    def __repr__(self):
        return 'Rect([{0}, {1}, {2}, {3}])'.format(self.x,
                                                   self.y,
                                                   self.width,
                                                   self.height)

    def __str__(self):
        return '{0}, {1}, {2}, {3} (Area {4})'.format(self.x,
                                                      self.y,
                                                      self.width,
                                                      self.height,
                                                      self.area)

    def __iter__(self):
        return iter( (self.x, self.y, self.width, self.height) )

    @property
    def area(self):
        return self.width*self.height

    @property
    def coordinates(self):
        return RectCoordinates(self.x, self.y, self.x+self.width, self.y+self.height)

    @property
    def centre(self):
        return Point(self.x+self.width/2,self.y+self.height/2)
