import mw_settings as s
import muirweb as mw
import json
from prettyprint import *
import arcpy

arcpy.env.overwriteOutput = True

# load json db
with open(s.MW_DB) as json_file:
    mw_db = json.load(json_file)


# Definitions
COMBINATION = 1
SUBSET = 2
ADJACENCY = 6
CONDITIONAL = 0

num_to_map = {1: 0,
              2: 0,
              3: 0,
              6: 0}

num_mapped = 0


# convert json objects to mw.element objects and key by element id
for i in mw_db['elements']:
    # print i
    e = mw.json_element_to_object(i)
    s.ELEMENTS[e.id] = e

# store relationship records in their respective subject elements
for i in mw_db['relationships']:
    # print i
    r = mw.json_relationship_to_object(i)
    s.ELEMENTS[r.subject].relationships.append(r)
    if r.object not in s.ELEMENTS[r.subject].object_list:
        s.ELEMENTS[r.subject].object_list.append(r.object)

# combination test


# for id in elements:
#     elements[id].set_grid()
#     if elements[id].grid is None and elements[id].automap == True:
#         if elements[id].definition in num_to_map:
#             num_to_map[elements[id].definition] += 1
#         else:
#             num_to_map[elements[id].definition] = 1
#     else:
#         num_mapped += 1

# pp(num_to_map)
# print num_mapped


# map distribution

# for id in s.ELEMENTS:
#
#     if s.ELEMENTS[id].status == 0:
#
#         if s.ELEMENTS[id].definition == COMBINATION:
#             mw.combination(s.ELEMENTS[id])
#
#         elif s.ELEMENTS[id].definition == SUBSET:
#             mw.subset(s.ELEMENTS[id])
#
#         elif s.ELEMENTS[id].definition == ADJACENCY:
#             mw.adjacency(s.ELEMENTS[id])
