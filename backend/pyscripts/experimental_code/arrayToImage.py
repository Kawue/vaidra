import numpy as np

class ArrayToImage:
    _types = {
        "uInt8": np.uint8,
        "uInt16": np.uint16,
        "uInt32": np.uint32,
    }
    
    def __init__(self, hdf5, convertType):
        self.hdf5 = hdf5
        self.gx = hdf5.index.get_level_values("grid_x")
        self.gy = hdf5.index.get_level_values("grid_y")
        self.array = hdf5.values
        self._array_min = np.amin(self.array)
        self._array_max = np.amax(self.array)
        self._type = self._types[convertType]
        self._typeinfo = np.iinfo(self._type)
        self._type_min = self._typeinfo.min
        self._type_max = self._typeinfo.max
        self.narray = self.normalize(self.array)
        

    def mapper(self):
        self.image = np.full((self.gy, self.gx, 4), np.nan)
        component = ?
        for (gx,gy,_), value in self.hdf5[component].iteritems():
            self.image[gy,gx,:] = self._value_to_rgba(value)

    def _value_to_rgba(self, value):
        a = value % 255
        _a = value // 255
        b = _a % 255
        _b = _a // 255
        g = _b % 255
        _g = _b // 255 
        r = _g % 255
        return r,g,b,a

    def _rgba_to_value(self, r,g,b,a):
        return ((r*255+g)*255+b)*255+a
        

    def normalize(self, array):
        return ((self._type_max - self._type_min) * ((array-self._array_min)/(self._array_max-self._array_min)) + self._type_min).astype(self._type)