import os
from prettyprint import pp
import numpy as np
import operator
import arcpy


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
        self.name = None
        self.maxprob = None
        self.definition = None
        self.description = None
        self.relationships = []
        self.object_list = []

        self.path = os.path.join('a_%s.tif' % id)
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

    def show_requirements(self):
        print self.name, 'requirements:'
        # pp([(elements[r.object].name, r.object) for r in self.relationships])
        pp(self.relationships)

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
            print 's.logging.info(all required objects exist' % self.name
            return True
        else:
            print 's.logging.info(objects %s missing, unable to map %s' % (ro_false, self.name)
            return False

    def sort_relationships(self):
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

            rel_dict[r.state][r.type].append((r.object, elements[r.object].name))

        self.relationships = rel_dict


class Relationship(object):
    """
    an object that mirrors a single relationship record from the mw_database
    """

    def __init__(self):
        self.subject = None
        self.object = None
        self.type = None
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
    relationship_instance.state = relationship["habitatstate"]
    relationship_instance.type = relationship["relationshiptype"]
    relationship_instance.id = relationship["id"]
    return relationship_instance


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
    object_list = [i / 100.0 for i in object_list]
    u = reduce(lambda x, y: x + y, object_list)
    u *= 100
    u[u > 100] = 100
    return u


def intersection(object_list):
    object_list = [i / 100.0 for i in object_list]
    return reduce(lambda x, y: x * y, object_list) * 100


def combination(element):

    states = []
    excl = []

    for state in element.relationships:
        rel_types = []
        for rel_type in state:
            rel_types.append(union(rel_type))

        states.append(intersection(rel_types))

    habitat = union(states)

    for e in excl:
        habitat *= (1 - e / 100.0)

    # scale by prevalence
    habitat *= element.maxprob

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
    """
    spatial adjacency: e.g. 47.1 Eutrophic pond shore
    assumes:  1) presence of value to be less than in descrip
              2) only 1 object for subject to be adjacent to
    """
    # get object grid
    obj = element.relationship[0][10]

    # calculate euclidean allocation up to maximum distance
    allocation = arcpy.sa.EucAllocation(in_source_data=obj,
                                        maximum_distance=element.description)

    allocation = arcpy.RasterToNumPyArray(allocation)
    obj = arcpy.RasterToNumPyArray(obj)

    # remove the cells containing the obj from array
    allocation[(obj >= 0)] = 0

    # allocation convert null values to zero
    allocation = np.nan_to_num(allocation)

    element.grid = arcpy.NumPyArrayToRaster(allocation)
