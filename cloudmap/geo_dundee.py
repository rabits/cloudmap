from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from io import BytesIO
import numpy as np
import requests
import os
import datetime
import glob
from PIL import Image
import sys


class GeoSatelliteDataDundee(object):

    """
    A class to download and process satellite image
    """

    def __init__(self, longitude, limit, rescale, base_url, suffix,
                 resolution, available, debug=False):
        """
        Args:

            * longitude:
                the longitude the satellite is positioned
            * limit:
                borders of the real satellite data in the
                downloaded image
            * rescale:
                function to rescale image colors (if not the
                full color space is used)
            * base_url:
                the url the image to download
            * suffix:
                suffix of the image name
            * resolution:
                resolution of the image to be downloaded (low, medium, high)
            * available:
                interval in minutes between shots
                can be used to find near image if target not found
        """

        resolution_str = {'low': 'S4',
                          'medium': 'S2',
                          'high': 'S1'}
        resolution_mult = {'low': 1,
                           'medium': 2,
                           'high': 4}

        self.available = available

        self.debug = debug

        try:
            resfile = resolution_str[resolution]
            self.resolution_mult = resolution_mult[resolution]
        except KeyError:
            sys.exit('Wrong resolution specified in config file! ' +
                     resolution +
                     ' Valid values are: low, medium, high')

        self.longitude = longitude
        self.limit = limit
        self.rescale = rescale
        self.base_url = "http://www.sat.dundee.ac.uk/xrit/" + base_url
        if self.debug:
            self.suffix = suffix + resfile + "_grid.jpeg"
        else:
            self.suffix = suffix + resfile + ".jpeg"

        self.filemodtime = 0
        self.outwidth = 0
        self.outheight = 0
        self.projection_method = "pyresample"

    def login(self, username, password):
        """
        Setup login data

        Args:
            * username:
                username of Dundee accoun
            * password:
                password of Dundee accoun
        """
        self.username = username
        self.password = password

#     @staticmethod
#     def curve(b):
#         """Rescale the brightness values used for MTSAT2 satellite"""
#         return np.minimum(b * 255.0 / 193.0, 255)
#
#     @staticmethod
#     def ID(b):
#         """Identity function"""
#         return b

    def set_time(self, dt, tempdir=""):
        """
        Setup satellite download image name based on time

        Args:
            * dt:
                datetime representation of time satellite image was taken
            * tempdir:
                directory to store downloaded images
        """
        self.dt = datetime.datetime(dt.year, dt.month, dt.day,
                                    dt.hour, dt.minute, 0)
        day = self.dt.strftime("%d").lstrip("0")
        month = self.dt.strftime("%m").lstrip("0")
        hour = self.dt.strftime("%H").lstrip("0")
        if not hour:  # if hour empty then assume midnight
            str1 = self.dt.strftime("%Y/") + month + "/" + day + "/" + "0/"
            str2 = self.dt.strftime("%Y_") + month + "_" + day + "_" + "0"
        else:
            str1 = self.dt.strftime("%Y/") + month + "/" + day + \
                "/" + hour + "00/"
            str2 = self.dt.strftime("%Y_") + month + "_" + day + \
                "_" + hour + "00"
        str3 = "*_*_*_*"
        self.url = self.base_url + str1 + str2 + self.suffix
        self.filename = os.path.join(tempdir, str2 + self.suffix)
        self.purge_pattern = os.path.join(tempdir, str3 + self.suffix)

    def purge(self):
        """Remove old satellite images"""
        for fl in glob.glob(self.purge_pattern):
            if fl == self.filename:
                continue
            os.remove(fl)

    def check_for_image_range(self, max_range):
        """
        Will check an image range dt - max_range < dt < dt + max_range
        starting from dt
        """
        if not self.check_for_image():
            original_dt = self.dt
            for delta in range(self.available, max_range, self.available):
                for d in [-delta, delta]:
                    self.set_time(original_dt+datetime.timedelta(minutes=d),os.path.dirname(self.filename))
                    if self.check_for_image():
                        print("WARNING:  found in range:", self.dt)
                        return True
            self.dt = original_dt
            print("WARNING:  not found in range:", self.dt)
            return False
        return True

    def check_for_image(self):
        """
        Test if image has already be downloaded or that it can be
        downloaded from the Dundee server
        """
        if os.path.isfile(self.filename):
            if self.debug:
                print("found image:", self.filename)
            return True
        r = requests.head(self.url, auth=(self.username, self.password))
        if r.status_code == requests.codes.ok:  # @UndefinedVariable
            if self.debug:
                print("can download image:", self.url)
            return True
        else:
            if self.debug:
                print("cannot download image:", self.url)
            return False

    def download_image(self):
        """Download the image if it has not been downloaded before"""
        if os.path.isfile(self.filename):
            if self.debug:
                print("image has alread been downloaded:", self.filename)
            self.filemodtime = os.path.getmtime(self.filename)
            return
        print("download image:", self.url)
        r = requests.get(self.url, auth=(self.username, self.password))
        i = Image.open(BytesIO(r.content))
        i.save(self.filename)
        self.filemodtime = os.path.getmtime(self.filename)

    def cut_borders(self, data):
        """Remove the white border of a satellite images (including text)"""

        l = {}
        l.update((x, y * self.resolution_mult) for x, y in self.limit.items())
        return data[l['top']:l['bottom'], l['left']:l['right']]

    def project(self):
        if self.projection_method == "pyresample":
            return self.project_pyresample()
        else:
            return self.project_cartopy()

    def project_cartopy(self):
        """
        Reproject the satellite image on an equirectangular map using the
        cartopy library
        """
        import cartopy.crs as ccrs
        from cartopy.img_transform import warp_array

        img = Image.open(self.filename).convert("L")
        self.data = self.cut_borders(np.array(img))

        width = self.outwidth
        height = self.outheight

        buf, _extent = \
            warp_array(self.data,
                       source_proj=ccrs.Geostationary(
                           central_longitude=self.longitude,
                           satellite_height=35785831.0
                       ),
                       target_proj=ccrs.PlateCarree(),
                       target_res=(width, height))

        dataResampledImage = self.rescale(buf.data)
        dataResampledImage = self.polar_clouds(dataResampledImage)
        weight = self.get_weight()

        result = np.array([dataResampledImage, weight])
        return result

    def get_weight(self):
        """Get weighting function for satellite image for overlaying"""
        weight_width = 55
        weight = np.array([max((weight_width -
                                min([abs(self.longitude - x),
                                    abs(self.longitude - x + 360),
                                    abs(self.longitude - x - 360)])) / 180,
                               1e-7)
                           for x in np.linspace(-180,
                                                180,
                                                self.outwidth)])

        weight = np.array([weight *
                           max(1e-7,
                               1 - 9/7 *
                               abs(i - self.outheight/2)/self.outheight*2)**0.5
                           for i in range(self.outheight)])

        return weight

    def project_pyresample(self):
        """
        Reproject the satellite image on an equirectangular map using the
        pyresample library
        """

        from pyresample import image, geometry
        from .satellites import pc

        img = Image.open(self.filename).convert("L")
        self.data = self.cut_borders(np.array(img))

        x_size = self.data.shape[1]
        y_size = self.data.shape[0]
        proj_dict = {'a': '6378137.0', 'b': '6356752.3',
                     'lon_0': self.longitude,
                     'h': '35785831.0', 'proj': 'geos'}
        self.extent = 5568742.4 * 0.964
        area_extent = (-self.extent, -self.extent,
                       self.extent, self.extent)
        area = geometry.AreaDefinition('geo', 'geostat', 'geo',
                                       proj_dict, x_size,
                                       y_size, area_extent)
        dataIC = image.ImageContainerQuick(self.data, area)

        dataResampled = dataIC.resample(pc(self.outwidth,
                                           self.outheight))
        dataResampledImage = self.rescale(dataResampled.image_data)
        dataResampledImage = self.polar_clouds(dataResampledImage)
        weight = self.get_weight()

        if self.debug:
            print("image max:", np.max(dataResampledImage))

        result = np.array([dataResampledImage, weight])
        return result

    def polar_clouds(self, dataResampledImage):
        # create fantasy polar clouds by mirroring high latitude data
        polar_height = int(95.0 / 1024.0 * self.outheight)
        north_pole_indices = range(0, polar_height)
        north_pole_copy_indices = range(2 * polar_height, polar_height, -1)
        dataResampledImage[north_pole_indices, :] =\
            dataResampledImage[north_pole_copy_indices, :]
        south_pole_indices = range(self.outheight - polar_height,
                                   self.outheight)
        south_pole_copy_indices = range(self.outheight - polar_height,
                                        self.outheight - 2 * polar_height,
                                        -1)
        dataResampledImage[south_pole_indices, :] = \
            dataResampledImage[south_pole_copy_indices, :]
        return dataResampledImage
