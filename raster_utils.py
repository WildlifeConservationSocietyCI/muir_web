import logging
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
    if ds.RasterCount > 1:
        logging.warning('%s has more than one layer; only the first will be used.' % ds)

    geotransform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    nodata = ds.GetRasterBand(1).GetNoDataValue()
    return geotransform, projection, nodata


def raster_to_ndarray(in_raster):
    src_ds = gdal.Open(in_raster, GA_ReadOnly)
    geotransform, projection, nodata = get_geo_info(src_ds)
    array = gdal_array.DatasetReadAsArray(src_ds)
    # print(array.dtype)
    # print(np.issubdtype(array.dtype, np.integer))
    # array[array == nodata] = np.nan
    print(nodata)
    print(array)
    array = np.ma.masked_values(array, nodata)
    # array = np.ma.masked_equal(array, nodata)
    print(array)

    # Force nodata value to avoid divergent input nodata values
    datatype = src_ds.GetRasterBand(1).DataType
    if datatype == gdal.GDT_Int16:
        nodata = s.NODATA_INT16
    elif datatype == gdal.GDT_Float32:
        nodata = s.NODATA_FLOAT32
    else:
        logging.exception('Raster data type %s not implemented' % datatype)
    array.set_fill_value(nodata)

    src_ds = None
    return array, geotransform, projection, nodata


def ndarray_to_raster(array, out_raster):
    y_size, x_size = array.shape
    dtype = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)
    # print(array.dtype)
    # print(dtype)
    output_raster = gdal.GetDriverByName(s.RASTER_DRIVER).Create(out_raster['file'], x_size, y_size, 1, dtype)

    output_raster.SetGeoTransform(out_raster['geotransform'])
    srs = osr.SpatialReference()
    srs.ImportFromWkt(out_raster['projection'])
    output_raster.SetProjection(srs.ExportToWkt())

    # nodata = float(out_raster['nodata'])
    # array.set_fill_value(nodata)
    array.set_fill_value(out_raster['nodata'])
    logging.info(array)
    logging.info(array.dtype)
    logging.info(array.mask)
    logging.info(array.fill_value)
    logging.info(out_raster['nodata'])
    # print(nodata)
    output_raster.GetRasterBand(1).WriteArray(array)
    output_raster.GetRasterBand(1).SetNoDataValue(out_raster['nodata'])
    # SetNoDataValue(np.float64(nodata))

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
