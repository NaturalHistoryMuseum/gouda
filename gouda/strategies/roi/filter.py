from gouda.util import debug_print

class AreaFilter(object):
    """ Filters rects by their areas
    """
    def __init__(self, min_area=5e3, max_area=5e5):
        if min_area and max_area and min_area>=max_area:
            raise ValueError('Inside-out limits [{0}] [{1}]'.format(min_area, max_area))
        self.min_area, self.max_area = min_area, max_area

    def filter(self, rects):
        debug_print('[{0}] rectangles'.format(len(rects)))
        for index,r in enumerate(rects):
            debug_print(index, r)

        if self.min_area:
            rects = [r for r in rects if r.area>=self.min_area]
        if self.max_area:
            rects = [r for r in rects if r.area<=self.max_area]

        debug_print('[{0}] rectangles after filtering by area'.format(len(rects)))
        for index,r in enumerate(rects):
            debug_print(index, r)

        return rects
