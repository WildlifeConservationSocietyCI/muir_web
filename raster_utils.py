import numpy as np
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import gdal_array
from osgeo import osr
import linecache
import mw_settings as s
# from wmi import WMI
# import os
# import muirweb as mw


def get_ascii_header(ascii_raster):
    """

    :param ascii_raster:
    :return:
    """

    header = [linecache.getline(ascii_raster, i) for i in range(1, 7)]
    header = {}

    for line in header:
        attribute, value = line.split()
        header[attribute] = value

    header['ncols'] = int(header['ncols'])
    header['nrows'] = int(header['nrows'])
    header['cellsize'] = int(header['cellsize'])
    header['xllcorner'] = float(header['xllcorner'])
    header['yllcorner'] = float(header['yllcorner'])

    return header


def get_geo_info(ds):
    geotransform = ds.GetGeoTransform()
    # projection = osr.SpatialReference()
    # projection.ImportFromWkt(sourceDS.GetProjectionRef())
    projection = ds.GetProjection()
    return geotransform, projection


def raster_to_ndarray(in_raster, metadata=True):
    """
    convert raster to numpy array
    metadata flag returns geotransform and projection GDAL objects
    :param in_raster object
    :param metadata whether to return metadata with array
    """
    # array = gdal_array.LoadFile(in_raster)
    # return_array = array
    # return_array[array == -3.40282e+038] = np.nan
    # return return_array

    src_ds = gdal.Open(in_raster, GA_ReadOnly)
    nodata = src_ds.GetRasterBand(1).GetNoDataValue()
    array = gdal_array.DatasetReadAsArray(src_ds)
    # array[array == nodata] = np.nan
    array = np.ma.masked_equal(array, nodata)

    geotransform, projection = get_geo_info(src_ds)
    src_ds = None
    return array, geotransform, projection, nodata

    # if metadata is True:
    #     geotransform, projection = get_geo_info(src_ds)
    #     return array, geotransform, projection, nodata
    # else:
    #     return array


# def ndarray_to_raster(array, out_raster, geotransform, projection, driver='GTiff', dtype=None):
def ndarray_to_raster(array, out_raster):
    # gdal_array.SaveArray(array, out_raster, driver, prototype)
    y_size, x_size = array.shape
    dtype = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)
    output_raster = gdal.GetDriverByName(s.RASTER_DRIVER).Create(out_raster['file'], x_size, y_size, 1, dtype)

    output_raster.SetGeoTransform(out_raster['geotransform'])
    srs = osr.SpatialReference()
    # epsg = int(projection.GetAttrValue("AUTHORITY", 1))
    # srs.ImportFromEPSG(epsg)
    srs.ImportFromWkt(out_raster['projection'])
    output_raster.SetProjection(srs.ExportToWkt())

    # write to array to raster
    output_raster.GetRasterBand(1).WriteArray(array)
    output_raster.GetRasterBand(1).SetNoDataValue(out_raster['nodata'])

    out_raster = None
    ourput_raster = None


def ndarray_to_ascii(out_ascii_path, array, header, fmt="%4i"):
    """
    write numpy array to ascii raster
    :rtype: object
    """
    out_asc = open(out_ascii_path, 'w')
    for attribute in header:
        out_asc.write(attribute)

    np.savetxt(out_asc, array, fmt=fmt)
    out_asc.close()


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