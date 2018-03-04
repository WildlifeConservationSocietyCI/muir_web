import numpy as np
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import gdal_array
from osgeo import osr
import mw_settings as s
# import os
# from wmi import WMI
# import muirweb as mw


def get_geo_info(ds):
    geotransform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    return geotransform, projection


def raster_to_ndarray(in_raster):
    src_ds = gdal.Open(in_raster, GA_ReadOnly)
    nodata = src_ds.GetRasterBand(1).GetNoDataValue()
    array = gdal_array.DatasetReadAsArray(src_ds)
    # array[array == nodata] = np.nan
    array = np.ma.masked_equal(array, nodata)

    geotransform, projection = get_geo_info(src_ds)
    src_ds = None
    return array, geotransform, projection, nodata


def ndarray_to_raster(array, out_raster):
    y_size, x_size = array.shape
    dtype = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)
    output_raster = gdal.GetDriverByName(s.RASTER_DRIVER).Create(out_raster['file'], x_size, y_size, 1, dtype)

    output_raster.SetGeoTransform(out_raster['geotransform'])
    srs = osr.SpatialReference()
    srs.ImportFromWkt(out_raster['projection'])
    output_raster.SetProjection(srs.ExportToWkt())

    output_raster.GetRasterBand(1).WriteArray(array)
    output_raster.GetRasterBand(1).SetNoDataValue(out_raster['nodata'])

    out_raster = None
    ourput_raster = None


# def get_memory():
#     # Reports current memory usage
#
#     w = WMI('.')
#     result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
#     memory = int(result[0].WorkingSet) / 1000000.0
#     print(memory, 'mb')
#
#
# def scale_test(num_rasters, size):
#     l = []
#
#     get_memory()
#     for i in range(0,num_rasters):
#         print('raster %s' % i)
#         l.append(np.random.randint(0, 100, size, dtype=np.int16))
#         get_memory()
#     print('sum arrays')
#     mw.union(l)
#     get_memory()
#     # sum(l)
