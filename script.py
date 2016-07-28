import json

from prettyprint import *

import muirweb as mw

# load json db
with open(r'F:\_data\Welikia\muir_web\welikia_muirweb.json') as json_file:
    db = json.load(json_file)


# Definitions
COMBINATION = 1
SUBSET = 2
ADJACENCY = 6
CONDITIONAL = 0
elements = {}
num_to_map = {1: 0,
              2: 0,
              3: 0,
              6: 0}

num_mapped = 0


# convert json objects to mw.element objects and key by element id
for i in db['elements']:
    # print i
    e = mw.json_element_to_object(i)
    elements[e.id] = e

# store relationship records in their respective subject elements
for i in db['relationships']:
    # print i
    r = mw.json_relationship_to_object(i)
    elements[r.subject].relationships.append(r)
    elements[r.subject].object_list.append(r.object)

# elements[116.1].show_attributes()

for id in elements:
    elements[id].set_grid()
    if elements[id].grid is None and elements[id].automap == True:
        if elements[id].definition in num_to_map:
            num_to_map[elements[id].definition] += 1
        else:
            num_to_map[elements[id].definition] = 1
    else:
        num_mapped += 1

pp(num_to_map)
print num_mapped


elements[54.10].sort_relationships(elements)
elements[54.10].show_requirements()
# map distribution
# for id in elements:
#
#     if elements[id].status == 0:
#
#         if elements[id].definition == COMBINATION:
#             mw.combination(elements[id])
#
#         elif elements[id].definition == SUBSET:
#             mw.subset(elements[id])
#
#         elif elements[id].definition == ADJACENCY:
#             mw.adjacency(elements[id])
