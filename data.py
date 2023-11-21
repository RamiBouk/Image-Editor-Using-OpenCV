import numpy as np
import cv2
class MyImage(np.ndarray):
    def __new__(cls, path, info=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = cv2.imread(path).view(cls)
        # add the new attribute to the created instance
        obj.info = info
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self.info = getattr(obj, 'info', None)

