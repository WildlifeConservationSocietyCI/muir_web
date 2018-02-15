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

        self.relationships = []
        self.object_list = []

    def __setitem__(self, key, value):
        self.__dict__[key] = value

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
        subject_rels = [r for r in relationships if r.id_subject == self.elementid]

        for r in subject_rels:
            if r.state not in rel_dict.keys():
                rel_dict[r.state] = {}
            if r.group not in rel_dict[r.state].keys():
                rel_dict[r.state][r.group] = []

            # append the object grid to list keyed by state and rel type
            # rel_dict[r.state][r.group].append(ru.raster_to_ndarray(elements[r.id_object].id_path))
            rel_dict[r.state][r.group].append(elements[r.id_object])

            if r['id_object'] not in elements[r['id_subject']].object_list:
                elements[r['id_subject']].object_list.append(elements[r['id_object']])

        self.relationships = rel_dict

    def show_relationships(self):
        print self.elementid, self.name, 'requirements:'
        rel_dict = {}

        for r in self.relationships:
            if r.state not in rel_dict.keys():
                rel_dict[r.state] = {}
            if r.group not in rel_dict[r.state].keys():
                rel_dict[r.state][r.group] = []

            rel_dict[r.state][r.group].append('%s\t%s' % (r.id_object, elements[r.id_object].name))

        pp.pprint(rel_dict)

    def has_requirements(self):
        """
        check the status of objects in objects list, if all required grids exist
        return True, else return False
        :return: boolean
        """
        ro_false = []
        for o in self.object_list:
            if elements[o].status is False:
                ro_false.append(o)

        if len(ro_false) == 0:
            print 'all required objects exist for %s' % self.name
            return True
        else:
            print 'objects %s missing, unable to map %s' % (ro_false, self.name)
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

def union(object_list):
    # TODO object list is the element object, grid is a attribute of an element object, scale by strength
    # object_list = [i.grid / 100.0 * i.strength for i in object_list]
    object_list = [i / 100.0 for i in object_list]
    u = reduce(lambda x, y: x + y, object_list)
    u *= 100
    u[u > 100] = 100
    return u


def intersection(object_list):
    object_list = [i / 100.0 for i in object_list]
    return reduce(lambda x, y: x * y, object_list)


def combination(element):
    element.set_relationships()

    states = []
    # excl = []

    for state in element.relationships:
        groups = []
        for group in element.relationships[state]:
            rasters = []
            for obj in element.relationships[state][group]:
                rasters.append(ru.raster_to_ndarray(obj.id_path))

            # if relationship is negative
            # element.relationships[state][group].type == 1:
                # excl.append(union(element.relationships[state][group]))
            # else:
            groups.append(union(rasters))

        states.append(intersection(groups))

    print states
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
    habitat *= element.maxprob
    habitat = np.floor(habitat + 0.5)
    # convert dtype to int
    habitat = habitat.astype(dtype=np.int16)

    # save raster
    grid = arcpy.NumPyArrayToRaster(habitat)
    grid.save(element.id_path)


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

    # adjacency relationship parameters
    obj = element.relationship[0][10]  # ? why the 11th group of the first state?
    subject = element
    maxdist = element.description

    # gdal proximity parameters
    distance = ['MAXDIST=%s' % (maxdist / s.CELL_SIZE)]
    filename, ext = os.path.splitext(subject.id_path)
    dst_temp_filename = '%s_temp%s' % (filename, ext)

    drivername = gdal.GetDriverByName(s.RASTER_DRIVER)
    src_ds = gdal.Open(obj.id_path)
    src_band = src_ds.GetRasterBand(1)

    dst_ds = drivername.CreateCopy(dst_temp_filename, src_ds, 0)
    dst_band = dst_ds.GetRasterBand(1)

    gdal.ComputeProximity(src_band, dst_band, distance)

    # load product of proximity calculation replace all non-zero values with
    # element maxprob
    # TODO: Do we need to save temp file?
    adj, geotransform, projection = ru.raster_to_ndarray(dst_temp_filename, metadata=True)
    adj[adj > 0] = element.maxprob
    adj[adj <= 0] = 0

    # save ndarray to tif
    ru.ndarray_to_raster(adj, subject.id_path, geotransform=geotransform, projection=projection)
    os.remove(dst_temp_filename)
