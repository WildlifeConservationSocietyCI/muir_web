# Recommended: use a conda environment, make pycharm work with it
# https://stackoverflow.com/a/47660948

import logging
import re
import pprint as pp
import mw_settings as s
import raster_utils as ru
from os.path import join, isfile
from osgeo import gdal
from numpy import *  # not doing the usual import numpy as np because we want to keep subset_rule evaluation simple

gdal.UseExceptions()
seterr(divide='raise', over='print', under='print', invalid='raise')
elements = {}
relationships = {}
frequency_types = []
strength_types = []


# CLASSES

class Element(object):

    def __init__(self, obj):
        # for attr, value in obj.iteritems():
        for attr, value in obj.items():
            self[attr] = value

        self.relationships = {}
        self.object_list = []

    def __setitem__(self, objkey, value):
        self.__dict__[objkey] = value

    def __repr__(self):
        return self.name

    @property
    def id_path(self):
        elementid = id_str(self.elementid)
        path = join(s.GRID_DIR, '%s.tif' % elementid)
        return path

    @property
    def status(self):
        if isfile(self.id_path):
            return True
        return False

    def set_relationships(self):
        self.object_list = []
        rel_dict = {}
        subject_rels = [r for r in relationships if r['id_subject'] == self.elementid]

        for r in subject_rels:
            state = r['state']
            group = r['relationshiptype']
            if state not in rel_dict.keys():
                rel_dict[state] = {}
            if group not in rel_dict[state].keys():
                rel_dict[state][group] = []

            # append the object element and its relationship to list keyed by state and group
            rel_dict[state][group].append({
                'id': r['id'], 
                'obj': elements[r['id_object']],
                'rel': r,
            })

            if r['id_object'] not in self.object_list:
                self.object_list.append(elements[r['id_object']])

        self.relationships = rel_dict

    def show_relationships(self):
        self.set_relationships()
        logging.info(' '.join([str(self.elementid), self.name, 'requirements:']))
        logging.info('\n%s' % pp.pformat(self.relationships))

    def has_requirements(self):
        """
        check the status of objects in objects list, if all required grids exist
        return True, else return False
        :return: boolean
        """
        ro_false = []
        for o in self.object_list:
            if o.status is False:
                ro_false.append(o)

        if len(ro_false) == 0:
            logging.info('All required objects exist for %s' % self.name)
            return True
        else:
            logging.error('Unable to map %s; objects missing: %s' % (self.name, ro_false))
            return False


# UTILITIES

def api_headers(client=False):
    # If we need to authorize to get to the API, this is where we'd do it; 'Authorization': 'Bearer %s' % access_token
    if client:
        pass
    headers = {}
    return {'params': s.params, 'headers': headers}


def calc_grid(elementid):
    subject = elements[elementid]
    logging.info('Mapping %s [%s]' % (subject.elementid, subject.name))
    if subject.has_requirements():
        try:
            if subject.mw_definition == s.COMBINATION:
                combination(subject)
            elif subject.mw_definition == s.SUBSET:
                subset(subject)
            elif subject.mw_definition == s.ADJACENCY:
                adjacency(subject)
            return True
        except Exception as e:
            logging.exception('exception!')
            return False
    else:
        return False


def get_by_id(list_of_dicts, dictkey, prop):
    for d in list_of_dicts:
        if d['id'] == dictkey:
            return d[prop]
    return None


def get_maxprob(element):
    return float(get_by_id(frequency_types, element.frequencytype, 'maxprob')) or 100.0


def get_object(element):  # for subjects with a relationship (subset, adjacency) depending on a single object
    # state = element.relationships.keys()[0]
    # group = element.relationships[state].keys()[0]
    # return element.relationships[state][group][0]
    return element.object_list[0] or None


def id_str(id_decimal):  # form is decimal, but datatype can be str
    return str(id_decimal).replace('.', '_')


def parse_calc(expression):
    dict_str = r"arrays['\1']"
    p = re.compile('\[([0|[1-9]\d*?\.\d+?(?<=\d))]')
    return p.sub(dict_str, expression)


# MAPPING METHODS

def round_int(arr):
    return floor(arr + 0.5).astype(int16)


def union(object_list):
    if len(object_list) == 1:
        return object_list[0]
    # object_list = [i / 100.0 for i in object_list]
    u = reduce(lambda x, y: x + y, object_list)
    # u *= 100
    u[u > 100] = 100
    return u


def intersection(object_list):
    if len(object_list) == 1:
        return object_list[0]
    object_list = [i / 100.0 for i in object_list]
    u = reduce(lambda x, y: x * y, object_list)
    u *= 100
    u[u > 100] = 100
    return u


def combination(element):
    element.set_relationships()

    states = []
    habitat_mods = []
    geotransform = None
    projection = None
    nodata = None
    default_habitat = None

    for state in element.relationships:
        groups = []
        for group in element.relationships[state]:
            rasters = []
            for rel in element.relationships[state][group]:
                arr, geotransform, projection, nodata = ru.raster_to_ndarray(rel['obj'].id_path)
                strength = float(get_by_id(strength_types, rel['rel']['strengthtype'], 'prob')) / 100
                if default_habitat is None:
                    default_habitat = ma.copy(arr)
                    default_habitat[default_habitat >= 0] = 1

                if rel['rel']['interactiontype'] == s.REQUIRED:
                    rasters.append(arr * strength)
                elif rel['rel']['interactiontype'] == s.ENHANCING:
                    habitat_mods.append(100 + (arr * strength))
                elif rel['rel']['interactiontype'] == s.ATTENUATING:
                    habitat_mods.append(100 - (arr * strength))

            if len(rasters) > 0:
                groups.append(union(rasters))

        if len(groups) > 0:
            states.append(intersection(groups))

    if len(states) > 0:
        habitat = union(states)
    else:
        habitat = default_habitat

    # habitat mods (enhancing/attenuating) are applied (intersected) after calculation of core habitat.
    # This means the states and groups of relationships for this interaction type are labels only;
    # the union/intersection logic they imply for core habitat does not apply to mods.
    habitat = intersection([habitat] + habitat_mods)

    # scale by prevalence
    habitat *= get_maxprob(element) / 100

    out_raster = {
        'file': element.id_path,
        'geotransform': geotransform,
        'projection': projection,
        'nodata': nodata
    }
    ru.ndarray_to_raster(round_int(habitat), out_raster)


def subset(element):
    """
    requires element.subset_rule to adhere to gdalnumeric syntax using +-/* or any
    numpy array functions (e.g. logical_and()) (http://www.gdal.org/gdal_calc.html)
    and use [elementid] as placeholders in calc string
    https://stackoverflow.com/questions/3030480/numpy-array-how-to-select-indices-satisfying-multiple-conditions
    note on bitwise vs. logical:
    https://stackoverflow.com/questions/10377096/multiple-conditions-using-or-in-numpy-array
    Example: logical_and([31.00] >= 2, [31.00] <= 5)
    """
    arrays = {}
    geotransform = None
    projection = None
    nodata = None
    present = None
    absent = None
    element.set_relationships()

    if len(element.object_list) > 0:
        calc_expression = parse_calc(element.subset_rule)

        for idx, obj in enumerate(element.object_list):
            arrays[obj.elementid], geotransform, projection, nodata = ru.raster_to_ndarray(obj.id_path)
            if idx == 0:
                # present/absent need both proper mask AND nodata vals in that mask
                # this relies on nodata being assigned the lowest possible val
                present = ma.copy(arrays[obj.elementid])
                present[present > nodata] = 1
                absent = ma.copy(arrays[obj.elementid])
                absent[absent > nodata] = 0

        subset_array = ma.where(eval(calc_expression), present, absent)
        present = None
        absent = None
        # subset_array *= get_maxprob(element)
        subset_array = subset_array * get_maxprob(element)

        out_raster = {
            'file': element.id_path,
            'geotransform': geotransform,
            'projection': projection,
            'nodata': nodata
        }
        # ru.ndarray_to_raster(subset_array.astype(int16), out_raster)
        ru.ndarray_to_raster(round_int(subset_array), out_raster)


def adjacency(element):
    element.set_relationships()

    obj = get_object(element)
    # http://arijolma.org/Geo-GDAL/1.6/class_geo_1_1_g_d_a_l.html#afa9a3fc598089b58eb23445b8c1c88b4
    options = ['MAXDIST=%s' % (element.adjacency_rule / s.CELL_SIZE),
               'VALUES=%s' % ','.join(str(i) for i in range(1, 101)),
               'FIXED_BUF_VAL=%s' % get_maxprob(element),
               'USE_INPUT_NODATA=YES',
               ]

    src_ds = gdal.Open(obj.id_path)
    src_band = src_ds.GetRasterBand(1)
    dst_ds = gdal.GetDriverByName(s.RASTER_DRIVER).CreateCopy(element.id_path, src_ds, 0)
    dst_band = dst_ds.GetRasterBand(1)

    # logging.info(options)
    gdal.ComputeProximity(src_band, dst_band, options=options)

    src_ds = None
    dst_ds = None
