import numpy as np
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import gdal_array
from osgeo import osr
import linecache
from wmi import WMI
import os
import muirweb as mw



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


def get_geo_info(FileName):
    sourceDS = gdal.Open(FileName, GA_ReadOnly)
    geoT = sourceDS.GetGeoTransform()
    projection = osr.SpatialReference()
    projection.ImportFromWkt(sourceDS.GetProjectionRef())
    return geoT, projection

def raster_to_array(in_raster, metadata=False):
    """
    convert raster to numpy array
    metadata flag returns geotransform and projection GDAL objects
    :type in_raster object
    """
    # print in_ascii
    src_ds = gdal.Open(in_raster, GA_ReadOnly)
    array = gdal_array.DatasetReadAsArray(src_ds)

    if metadata is True:
        geotransform, projection = get_geo_info(in_raster)
        return array, geotransform, projection

    else:
        return array

def ndarray_to_raster(array, out_raster, geotransform, projection, driver='GTiff', dtype=None):
    """
    write numpy array to raster
    :param array:
    :param out_raster:
    :param geotransform:
    :param projection:
    :param driver:
    :param dtype:
    :return:
    """

    # get array dimensions
    y_size, x_size = array.shape

    # map numpy dtype to GDAL dtype if default arg is used
    if dtype is None:
        dtype = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)
        print(dtype)

    output_raster = gdal.GetDriverByName(driver).Create(out_raster, x_size, y_size, 1, dtype)

    # set coordinates
    output_raster.SetGeoTransform(geotransform)

    # set projection
    srs = osr.SpatialReference()
    epsg = int(projection.GetAttrValue("AUTHORITY", 1))
    srs.ImportFromEPSG(epsg)
    output_raster.SetProjection(srs.ExportToWkt())

    # write to array to raster
    output_raster.GetRasterBand(1).WriteArray(array)


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


def get_memory():
    # Reports current memory usage

    w = WMI('.')
    result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
    memory = int(result[0].WorkingSet) / 1000000.0
    print(memory, 'mb')


def scale_test(num_rasters, size):
    l = []

    get_memory()
    for i in range(0,num_rasters):
        print('raster %s' % i)
        l.append(np.random.randint(0, 100, size, dtype=np.int16))
        get_memory()
    print('sum arrays')
    mw.union(l)
    get_memory()
    # sum(l)