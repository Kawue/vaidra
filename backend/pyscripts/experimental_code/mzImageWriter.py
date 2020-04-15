import numpy as np
import matplotlib
matplotlib.use('Agg')
#matplotlib.use('TkAgg') # in case of plotting
import matplotlib.pyplot as plt
import os
from skimage.measure import label, regionprops

class MsiImageWriter:
    def __init__(self, dframe, cmap=plt.cm.get_cmap("viridis"), colorscale_boundary=(0,100)):
        self.dframe = dframe
        self.grid_x = np.array(self.dframe.index.get_level_values("grid_x")).astype(int)
        self.grid_y = np.array(self.dframe.index.get_level_values("grid_y")).astype(int)
        self.height = self.grid_y.max() + 1
        self.width = self.grid_x.max() + 1
        self.colormap = plt.cm.ScalarMappable(plt.Normalize(), cmap=cmap)
        self.colorscale_boundary = colorscale_boundary
    
    def write_mzImage_img(self, mzValue):
        intens = self.dframe[mzValue]
        self.colormap.set_clim(np.percentile(intens, self.colorscale_boundary))
        img = self._create_empty_img(True)
        img[(self.grid_y, self.grid_x)] = self.colormap.to_rgba(np.array(intens), bytes=True)
        return img

    # def write_dimvis_rgb(self, red_ch, green_ch, blue_ch, method_name):
    #     # Use matplotlibs reverse gray colormap to scale intensities in colorscale boundary
    #     tmp_cm = plt.cm.ScalarMappable(plt.Normalize(), cmap=plt.cm.get_cmap("Greys_r"))
    #     tmp_cm.set_clim(np.percentile(red_ch, self.colorscale_boundary))
    #     r_intens = tmp_cm.to_rgba(red_ch, bytes=True)[:, 0]
    #     tmp_cm.set_clim(np.percentile(green_ch, self.colorscale_boundary))
    #     g_intens = self.colormap.to_rgba(green_ch, bytes=True)[:, 0]
    #     tmp_cm.set_clim(np.percentile(blue_ch, self.colorscale_boundary))
    #     b_intens = self.colormap.to_rgba(blue_ch, bytes=True)[:, 0]
        
    #     rgb_img = np.zeros((self.height, self.width, 3))
    #     rgb_img[(self.grid_y, self.grid_x, 0)] = r_intens
    #     rgb_img[(self.grid_y, self.grid_x, 1)] = g_intens
    #     rgb_img[(self.grid_y, self.grid_x, 2)] = b_intens

    #     self.colormap.set_clim(np.percentile(red_ch, self.colorscale_boundary))
    #     r_img = np.zeros((self.height, self.width))
    #     r_img[(self.grid_y, self.grid_x)] = self.colormap.to_rgba(red_ch, bytes=True)[:, 0]
        
    #     self.colormap.set_clim(np.percentile(green_ch, self.colorscale_boundary))
    #     g_img = np.zeros((self.height, self.width))
    #     g_img[(self.grid_y, self.grid_x)] = self.colormap.to_rgba(green_ch, bytes=True)[:, 0]
        
    #     self.colormap.set_clim(np.percentile(blue_ch, self.colorscale_boundary))
    #     b_img = np.zeros((self.height, self.width))
    #     b_img[(self.grid_y, self.grid_x)] = self.colormap.to_rgba(blue_ch, bytes=True)[:, 0]
        
    #     return r_img, g_img, b_img, rgb_img

    def _create_empty_img(self, rgba):
        if rgba:
            return np.zeros((self.height + 1, self.width + 1, 4))
        else:
            return np.zeros((self.height + 1, self.width + 1))


        