# Recommended: use a conda environment, make pycharm work with it
# https://stackoverflow.com/a/47660948
# install archook (via pip within the conda env) for access to arcpy
# https://github.com/JamesRamm/archook

import os
# import operator
import gdal
import archook
archook.get_arcpy()
import arcpy
import numpy as np
import pprint as pp
import mw_settings as s
import raster_utils as ru

elements = {}
relationships = {}
frequency_types = []


# CLASSES

class Element(object):
    """
    element should mirror database element model,
    with the addition of grid and relationship attributes
    """

    def __init__(self, obj):
        for attr, value in obj.iteritems():
            self[attr] = value

        # self.id = None
        # self.name = None
        # self.automap = None
        # self.maxprob = None
        # self.definition = None
        # self.description = None

        self.relationships = {}
        self.object_list = []

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return self.name

    @property
    def id_path(self):
        """
        convert element id into grid path
        :return: path
        """
        elementid = str(self.elementid).replace('.', '_')
        path = os.path.join(s.GRID_DIR, '%s.tif' % elementid)
        return path

    @property
    def status(self):
        """
        if grid exists status == True, this method differs from set_grid()
        in that it does not load the raster into memory
        :return: boolean
        """
        if os.path.isfile(self.id_path):
            return True
        return False

    # def set_grid(self):
    #     """
    #     if exists assign to grid attribute
    #     :return:
    #     """
    #     if os.path.isfile(self.id_path):
    #         self.grid = 'raster_to_ndarray(self.id_path) or arcpy.Raster(self.id_path)'

    # def show_attributes(self):
    #     print 'id: %s \n' % self.id, \
    #           'name: %s \n' % self.name,\
    #           'description: %s \n' % self.description, \
    #           'definition: %s \n' % self.definition, \
    #           'maxprob: %s \n' % self.maxprob,\
    #           'object list: %s \n' % self.object_list, \
    #           'automap: %s\n' % self.automap, \
    #           'status: %s' % self.status

    def set_relationships(self):
        """
        group objects according to relationship state and group
        """
        rel_dict = {}
        subject_rels = [r for r in relationships if r['id_subject'] == self.elementid]

        for r in subject_rels:
            if r['state'] not in rel_dict.keys():
                rel_dict[r['state']] = {}
            if r['group'] not in rel_dict[r['state']].keys():
                rel_dict[r['state']][r['group']] = []

            # append the object grid to list keyed by state and rel type
            # rel_dict[r['state']][r['group']].append(ru.raster_to_ndarray(elements[r['id_object']].id_path))
            rel_dict[r['state']][r['group']].append(elements[r['id_object']])

            if r['id_object'] not in elements[r['id_subject']].object_list:
                elements[r['id_subject']].object_list.append(elements[r['id_object']])

        self.relationships = rel_dict

    def show_relationships(self):
        self.set_relationships()
        print(' '.join([str(self.elementid), self.name, 'requirements:']))
        pp.pprint(self.relationships)

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
            print('All required objects exist for %s' % self.name)
            return True
        else:
            print('Unable to map %s; objects missing: %s' % (self.name, ro_false))
            return False


# class Relationship(object):
#     """
#     an object that mirrors a single relationship record from the mw_database
#     """
#
#     def __init__(self):
#         self.subject = None
#         self.object = None
#         self.group = None
#         self.strength = None
#         self.state = None
#         self.id = None


# UTILITIES

def api_headers(client=False):
    # If we need to authorize to get to the API, this is where we'd do it; 'Authorization': 'Bearer %s' % access_token
    if client:
        pass
    headers = {}
    return {'params': s.params, 'headers': headers}


def calc_grid(elementid):
    subject = elements[elementid]
    print('Mapping %s [%s]' % (subject.elementid, subject.name))
    if subject.has_requirements():
        try:
            if subject.mw_definition == s.COMBINATION:
                combination(subject)
            elif subject.mw_definition == s.SUBSET:
                subset(subject)
            elif subject.mw_definition == s.ADJACENCY:
                adjacency(subject)
            return True
        except:
            return False
    else:
        return False


def get_by_id(list_of_dicts, key, prop):
    for d in list_of_dicts:
        if d['id'] == key:
            return d[prop]
    return None


def get_maxprob(element):
    return float(get_by_id(frequency_types, element.frequencytype, 'maxprob')) or 100.0


def get_object(element):  # for subjects with a relationship (subset, adjacency) depending on a single object
    # state = element.relationships.keys()[0]
    # group = element.relationships[state].keys()[0]
    # return element.relationships[state][group][0]
    return element.object_list[0] or None

# def num(string):
#     try:
#         return int(string)
#     except ValueError:
#         return s


# def boolean_parser(string):
#     ops = {'==': operator.eq,
#            '!=': operator.ne,
#            '<=': operator.le,
#            'or': operator.or_,
#            'and': operator.and_}
#
#     con_expression = []
#
#     for sym in string.split(string):
#         if sym in ops:
#             con_expression.append(ops[sym])
#         else:
#             con_expression.append(num(sym))
#
#     return ''.join(con_expression)


# store relationship records in their respective subject elements
# def attach_objects(relationships):
#     for r in relationships:
#         elements[r['id_subject']].relationships.append(r)
#         if r['id_object'] not in elements[r['id_subject']].object_list:
#             elements[r['id_subject']].object_list.append(r['id_object'])


# TRANSLATION

# def json_element_to_object(element):
#     """
#     convert json element object into mw.element instance
#     :param element:
#     :return: mw.element
#     """
#     element_instance = Element()
#     element_instance.id = element['elementid']
#     element_instance.name = element['scientificname']
#     element_instance.maxprob = element['maxprob']
#     element_instance.definition = element['definition']
#     element_instance.description = element['description']
#     element_instance.automap = element['automap']
#     element_instance.path = id_path(element_instance.id)
#     return element_instance
#
#
# def json_relationship_to_object(relationship):
#     """
#     convert json relationship object into mw.relationship instance
#     :param relationship:
#     :return: mw.relationship
#     """
#     relationship_instance = Relationship()
#     relationship_instance.strength = relationship["strength"]
#     relationship_instance.subject = relationship["id_subject"]
#     relationship_instance.object = relationship["id_object"]
#     relationship_instance.state = int(relationship["habitatstate"])
#     relationship_instance.group = int(relationship["relationshiptype"])
#     relationship_instance.id = relationship["id"]
#     return relationship_instance


# MAPPING METHODS

def round_int(array):
    return np.floor(array + 0.5).astype(np.int16)


def union(object_list):
    # TODO object list is the element object, grid is a attribute of an element object, scale by strength
    # We have strengthtype in the relationship
    # object_list = [i.grid / 100.0 * i.strength for i in object_list]
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
    # excl = []
    geotransform = None
    projection = None
    nodata = None

    for state in element.relationships:
        groups = []
        for group in element.relationships[state]:
            rasters = []
            for obj in element.relationships[state][group]:
                array, geotransform, projection, nodata = ru.raster_to_ndarray(obj.id_path)
                rasters.append(array)

            # if relationship is negative
            # element.relationships[state][group].type == 1:
                # excl.append(union(element.relationships[state][group]))
            # else:
            groups.append(union(rasters))

        states.append(intersection(groups))

    # print('states: %s' % states)
    habitat = union(states)
    """
        suitability of cell (probability of subject pressence) is inversely
        proportional to the likelihood of negatively influencing conditions
        scaled by the strength of the relationship.
    """

    # for i in excl:
    #     habitat *= ((1 - i.grid / 100.0 * i.strength))
    # if exlusionary conditions reduce subject probability to a value less than 0
    # set to 0
    # habitat[habitat < 0] = 0

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
    subsets: e.g. 31.1 Gently sloping slopes
    assumes:  1) presence of 'Grid' and 'MaxProb' strings in descrip for substitution
               2) only 1 object for subject to be a subset of
    returns a subjet of an array using conditional indexing
    """

    element.set_relationships()
    obj = element.object_list[0]

    obj_grid = arcpy.RasterToNumPyArray(obj.id_path)
    shape = obj_grid.shape

    present = np.full(shape=shape, fill_value=1, dtype=np.int16)
    absent = np.full(shape=shape, fill_value=0, dtype=np.int16)
    subset_array = np.where(eval(element.description), present, absent)
    subset_array *= element.maxprob

    grid = arcpy.NumPyArrayToRaster(subset_array)
    grid.save(element.id_path)


def adjacency(element):
    element.set_relationships()

    obj = get_object(element)
    # obj = element.relationship[0][10]  # ? why the 11th group of the first state?
    options = ['MAXDIST=%s' % (element.adjacency_rule / s.CELL_SIZE),
               'VALUES=%s' % ','.join(str(i) for i in range(1, 101)),
               'FIXED_BUF_VAL=%s' % get_maxprob(element),
               # 'NODATA=-32768',  # TODO: don't hardcode this
               'USE_INPUT_NODATA=YES',
               ]
    # dst_temp_filename = '%s_temp%s' % os.path.splitext(element.id_path)

    src_ds = gdal.Open(obj.id_path)
    src_band = src_ds.GetRasterBand(1)
    # dst_ds = gdal.GetDriverByName(s.RASTER_DRIVER).CreateCopy(dst_temp_filename, src_ds, 0)
    dst_ds = gdal.GetDriverByName(s.RASTER_DRIVER).CreateCopy(element.id_path, src_ds, 0)
    dst_band = dst_ds.GetRasterBand(1)

    # print(options)
    gdal.ComputeProximity(src_band, dst_band, options=options)

    # load product of proximity calculation replace all non-zero values with element maxprob
    # adj, geotransform, projection, nodata = ru.raster_to_ndarray(dst_temp_filename)
    # adj[adj > 0] = get_maxprob(element)
    # adj[adj <= 0] = 0

    # out_raster = {
    #     'file': element.id_path,
    #     'geotransform': geotransform,
    #     'projection': projection,
    #     'nodata': nodata
    # }
    # print(out_raster.__dict__)
    # ru.ndarray_to_raster(round_int(adj), out_raster)

    src_ds = None
    dst_ds = None
    # os.remove(dst_temp_filename)
