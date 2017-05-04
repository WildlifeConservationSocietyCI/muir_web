import os
from prettyprint import pp
import numpy as np
import operator
import arcpy
import mw_settings as s
import sys
import gdal
import os.path
import raster_utils as ru

# CLASSES


class Element(object):
    """
    element should mirror database element model,
    with the addition of grid and relationship attributes
    """

    def __init__(self):

        self.id = None
        self.name = None
        self.automap = None
        self.maxprob = None
        self.definition = None
        self.description = None
        self.relationships = []
        self.object_list = []

        self.path = id_path(self.id)
        self.status = False
        self.grid = None

    def show_attributes(self):
        """

        :return:
        """
        print 'id: %s \n' % self.id, \
              'name: %s \n' % self.name,\
              'description: %s \n' % self.description, \
              'definition: %s \n' % self.definition, \
              'maxprob: %s \n' % self.maxprob,\
              'object list: %s \n' % self.object_list, \
              'automap: %s\n' % self.automap, \
              'status: %s' % self.status

    def check_status(self):
        """
        if grid exists status == True, this method differs from set_grid()
        in that it does not load the raster into memory
        :return:
        """
        if os.path.isfile(self.path):
            self.status = True

    def set_grid(self):
        """
        if exists assign to grid attribute
        :return:
        """
        if os.path.isfile(self.path):
            self.grid = 'raster_to_numpy(self.path) or arcpy.Raster(self.path)'

    def show_relationships(self):
        print self.id, self.name, 'requirements:'
        rel_dict = {}

        for r in self.relationships:
            if r.state not in rel_dict.keys():
                rel_dict[r.state] = {}
            if r.group not in rel_dict[r.state].keys():
                rel_dict[r.state][r.group] = []

            rel_dict[r.state][r.group].append('%s\t%s' % (r.object, s.ELEMENTS[r.object].name))

        pp(rel_dict)

    def check_requirements(self):
        """
        check the status of objects in objects list, if all required grids exist
        return True, else return False
        :return:
        """
        ro_false = []
        for o in self.object_list:
            s.ELEMENTS[o].check_status()
            print s.ELEMENTS[o].status
            if s.ELEMENTS[o].status is False:
                ro_false.append(o)

        if len(ro_false) == 0:
            print 's.logging.info(all required objects exist'
            return True
        else:
            print 's.logging.info(objects %s missing, unable to map %s' % (ro_false, self.name)
            return False

    def set_relationship_grids(self):
        """
        sort and group object grids according to state and relationship type
        :return:
        """
        rel_dict = {}

        for r in self.relationships:
            if r.state not in rel_dict.keys():
                rel_dict[r.state] = {}
            if r.type not in rel_dict[r.state].keys():
                rel_dict[r.state][r.type] = []

            # append the object grid to list keyed by state and rel type
            rel_dict[r.state][r.type].append(ru.raster_to_array(s.ELEMENTS[r.object].path))

        self.relationships = rel_dict


class Relationship(object):
    """
    an object that mirrors a single relationship record from the mw_database
    """

    def __init__(self):
        self.subject = None
        self.object = None
        self.group = None
        self.strength = None
        self.state = None
        self.id = None


# TRANSLATION

def json_element_to_object(element):
    """
    convert json element object into mw.element instance
    :param element:
    :return: mw.element
    """
    element_instance = Element()
    element_instance.id = element['elementid']
    element_instance.name = element['scientificname']
    element_instance.maxprob = element['maxprob']
    element_instance.definition = element['definition']
    element_instance.description = element['description']
    element_instance.automap = element['automap']
    element_instance.path = id_path(element_instance.id)
    return element_instance


def json_relationship_to_object(relationship):
    """
    convert json relationship object into mw.relationship instance
    :param relationship:
    :return: mw.relationship
    """
    relationship_instance = Relationship()
    relationship_instance.strength = relationship["strength"]
    relationship_instance.subject = relationship["id_subject"]
    relationship_instance.object = relationship["id_object"]
    relationship_instance.state = int(relationship["habitatstate"])
    relationship_instance.group = int(relationship["relationshiptype"])
    relationship_instance.id = relationship["id"]
    return relationship_instance


def id_path(element_id):
    """
    convert element id into grid path
    :param element_id:
    :return:path
    """
    element_id = str(element_id).replace('.', '_')
    path = os.path.join(s.ROOT_DIR, '%s.tif' % element_id)
    return path


# MAPPING METHODS


def num(s):
    try:
        return int(s)
    except ValueError:
        return s


def boolean_parser(s):
    ops = {'==': operator.eq,
           '!=': operator.ne,
           '<=': operator.le,
           'or': operator.or_,
           'and': operator.and_}

    con_expresison = []

    for sym in str.split(s):
        if sym in ops:
            con_expresison.append(ops[sym])
        else:
            con_expresison.append(num(sym))

    return con_expresison


def union(object_list):
    #TODO object list is the element object, grid is a attribute of and element object, scale by strength
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

    states = []
    excl = []

    for state in element.relationships:
        groups = []
        for group in element.relationships[state]:
            # if relationship is negative
            # element.relationships[state][group].type == 1:
                # excl.append(union(element.relationships[state][group]))
            # else:
            groups.append(union(element.relationships[state][group]))

        states.append(intersection(group))

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
    habitat *= (element.maxprob)
    habitat = np.floor(habitat + 0.5)
    # convert dtype to int
    habitat = habitat.astype(dtype=np.int16)

    # convert to np.array to arcpy raster object
    element.grid = arcpy.NumPyArrayToRaster(habitat)

    # save raster
    element.grid.save(element.path)


def subset(element):
    """
    subsets: e.g. 31.1 Gently sloping slopes
    assumes:  1) presence of 'Grid' and 'MaxProb' strings in descrip for substitution
               2) only 1 object for subject to be a subset of
    returns a subjet of an array using conditional indexing
    """

    obj = element.object_list[0]

    obj = arcpy.RasterToNumPyArray(obj)
    shape = obj.shape

    present = np.full(shape=shape, fill_value=1, dtype=np.int16)
    absent = np.full(shape=shape, fill_value=0, dtype=np.int16)
    subset = np.where(eval(element.description), present, absent)
    subset *= element.maxprob

    element.grid = arcpy.NumPyArrayToRaster(subset)


def adjacency(element):

    # adjacency relationship parameters
    obj = element.relationship[0][10]
    subject = element.id
    maxdist = element.description

    # gdal proximity parameters
    format = 'GTiff'
    distance = ['MAXDIST=%s' % (maxdist / s.CELL_SIZE)]
    src_filename = os.path.join(s.ROOT_DIR, '%s.tif' % obj)
    dst_temp_filename = os.path.join(s.ROOT_DIR, '%s_temp.tif' % subject)
    dst_filename = os.path.join(s.ROOT_DIR, '%s.tif' % subject)

    driver = gdal.GetDriverByName('GTiff')
    src_ds = gdal.Open(src_filename)
    src_band = src_ds.GetRasterBand(1)

    dst_ds = driver.CreateCopy(dst_temp_filename, src_ds, 0)
    dst_band = dst_ds.GetRasterBand(1)

    gdal.ComputeProximity(src_band, dst_band, distance)

    srcband = None
    dstband = None
    src_ds = None
    dst_ds = None

    # load product of proximity calculation replace all non-zero values with
    # element maxprob
    adj, geotransform, projection = ru.raster_to_array(dst_temp_filename, metadata=True)
    adj[adj > 0] = element.maxprob
    adj[adj <= 0] = 0

    # save ndarray to tif
    ru.ndarray_to_raster(adj, dst_filename, geotransform=geotransform, projection=projection)
    os.remove(dst_temp_filename)
