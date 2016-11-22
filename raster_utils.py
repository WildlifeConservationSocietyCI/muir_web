import numpy as np
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import gdal_array
from osgeo import osr
import linecache


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



def raster_to_array(in_raster):
    """
    convert raster to numpy array
    :type in_raster object
    """
    # print in_ascii
    ascii = gdal.Open(in_raster, GA_ReadOnly)
    array = gdal_array.DatasetReadAsArray(ascii)

    return array


def array_to_raster(array, out_raster, geotransform, projection, driver='GTiff', dtype=None):
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
    x_size, y_size = array.shape

    # map numpy dtype to GDAL dtype if default arg is used
    if dtype is None:
        dtype = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)
        print dtype

    output_raster = gdal.GetDriverByName(driver).Create(out_raster, x_size, y_size, 1, dtype)

    # set coordinates
    output_raster.SetGeoTransform(geotransform)

    # set projection
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(projection)
    output_raster.SetProjection(srs.ExportToWkt())

    # write to array to raster
    output_raster.GetRasterBand(1).WriteArray(array)


def array_to_ascii(out_ascii_path, array, header, fmt="%4i"):
    """
    write numpy array to ascii raster
    :rtype: object
    """
    out_asc = open(out_ascii_path, 'w')
    for attribute in header:
        out_asc.write(attribute)

    np.savetxt(out_asc, array, fmt=fmt)
    out_asc.close()