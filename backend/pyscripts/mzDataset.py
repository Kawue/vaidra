import numpy as np
from matplotlib import cm
from skimage import img_as_uint
import matplotlib as mpl
#mpl.use("TkAgg")


class MzMapping:
    def __init__(self, mzList):
        self.inverse = { index: value for value, index in enumerate(mzList)}
        self.mzList = mzList

    def __len__(self):
        return len(self.mzList)

    def __iter__(self):
        return iter(self.mzList)

    def __getitem__(self, key):
        return self.mzList[key]

    def __str__(self):
        return ', '.join(["({}, {})".format(index, value) for value, index in enumerate(self.mzList)])

    def getMultipleInverse(self, mzValues):
        if type(mzValues) == list:
            return [self.inverse[i] for i in mzValues]
        else:
            return [self.inverse[mzValues]]


class MzDataSet:
    def __init__(self, dframe):
        self.__mapping = MzMapping(list(dframe.columns))
        gx = dframe.index.get_level_values("grid_x").astype('int')
        gy = dframe.index.get_level_values("grid_y").astype('int')

        mzimgs = []

        for mz in dframe.columns:
            img = np.full((gy.max()+1, gx.max()+1), np.nan)
            img[(gy, gx)] = dframe[mz]
            mzimgs.append(img)

        self.__cube = np.dstack(np.array(mzimgs)[None, :])
        self.__cube = np.moveaxis(self.__cube, 0, -1)

    def getMzValues(self):
        return self.__mapping.mzList

    def getMzIndex(self, mzValues):
        return self.__mapping.getMultipleInverse(mzValues)

    def getCube(self):
        return self.__cube

    def getGreyImage(self, mzValues, method=np.mean):
        intensity = method(self.__cube[:,:,self.__mapping.getMultipleInverse(mzValues)], 2)
        mask = (~np.isnan(intensity))
        intensity[mask] = np.interp(intensity[mask], (np.nanmin(intensity), np.nanmax(intensity)), (0, 1))
        return intensity

    def getColorImage(self, mzValues, method=np.mean, cmap='viridis', bytes=True):
        colorMap = cm.get_cmap(cmap)
        colorMap.set_bad(color='white')
        return colorMap(np.ma.masked_invalid(self.getGreyImage(mzValues, method)), bytes=bytes)


class DimRedDataSet:
    def __init__(self, dframe, dataset_name, embedding):
        gx = dframe.index.get_level_values("grid_x").astype('int')
        gy = dframe.index.get_level_values("grid_y").astype('int')
        subembedding = embedding.xs(dataset_name,level="dataset")
        mzimgs = []

        for component in subembedding.columns:
            img = np.full((gy.max() + 1, gx.max() + 1), np.nan)
            img[(gy, gx)] = subembedding[component]
            mzimgs.append(img)

        self.__cube = np.dstack(np.array(mzimgs)[None, :])
        self.__cube = np.moveaxis(np.dstack(np.array(mzimgs)[None, :]), 0, -1)

    def getCube(self):
        return self.__cube

    def getGreyImage(self, component):
        intensity = self.__cube[:,:,component]
        mask = (~np.isnan(intensity))
        intensity[mask] = np.interp(intensity[mask], (np.nanmin(intensity), np.nanmax(intensity)), (0, 1))
        return intensity

    def getColorImage(self, component, cmap='viridis', bytes=True):
        colorMap = cm.get_cmap(cmap)
        colorMap.set_bad(color='white')
        return colorMap(np.ma.masked_invalid(self.getGreyImage(component)), bytes=bytes)

    def getRGBImage(self, components):
        intensities = self.__cube[:,:,components]
        mask = (~np.isnan(intensities[:,:,0]))
        intensities[mask] = np.interp(intensities[mask], (np.nanmin(intensities), np.nanmax(intensities)), (0, 1))
        #for idx in range(intensities.shape[2]):
        #    intensities[:,:,idx][mask] = np.interp(intensities[:,:,idx][mask], (np.nanmin(intensities[:,:,idx]), np.nanmax(intensities[:,:,idx])), (0, 1))
        alpha = np.full((intensities.shape[0], intensities.shape[1]), np.nan)
        alpha[mask] = 1
        intensities = np.dstack((intensities, alpha))
        intensities[np.isnan(intensities)] = 0
        intensities = (intensities * 255).astype(np.uint8)
        return intensities