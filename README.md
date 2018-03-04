# MUIR WEB DB REFACTOR AND SPATIAL DATA SCRIPT

This repository contains 
1) SQL for refactoring the schema of Muir Web-related data in the Visionmaker database--but NOT the changes to the 
code of other apps (such as Visionmaker Django models) that depend on these schema. 
2) Code for consuming data via a simple Visionmaker API and producing a tif file for every Muir Web element listed in
 the API that has all required dependent spatial data available.

## INSTALLATION

Requirements (note that arcpy is NOT a requirement):
- gdal
- numpy
- requests
- pprint

Recommended: use a conda environment, and make pycharm work with it 
https://stackoverflow.com/a/47660948

For the full (recursive) spatial computation process (i.e. having already done the database and associated extrinsic 
application refactoring), clone this repository, make sure you have access to the API, and 
edit the settings in mw_settings.py. Then run script.py. Other uses of the mapping functions with respect to the 
API, such as calculation of a single Muir Web element, are similarly easy to script.

## DB REFACTOR

The SQL portion of this repository:
1. Makes smaller tweaks for consistency in data and original Access import errors
2. Adds/removes fields and tables to support the spatial calculation refactoring, or simply the natural 
evolution of the Muir Web concepts themselves
3. Makes changes to support the spatial calculation abstraction/generalization of states, groups, and relationship 
strengths/interactions (see below).

### Implementation steps:
1. schema_update.sql
2. value_update.sql
3. schema_cleanup.sql
4. description_fix.sql
5. Commit code for Visionmaker (including wobsadmin), welikia.org, and welikia.net
6. Visionmaker: delete migrations from mannahatta2409 and wobsadmin migrations folders
7. Visionmaker: python manage.py makemigrations mannahatta2409
8. Visionmaker: python manage.py migrate --fake mannahatta2409
9. Visionmaker: python manage.py makemigrations wobsadmin
10. Visionmaker: python manage.py migrate --fake wobsadmin
11. Visionmaker: python manage.py migrate
12. Visionmaker: wipe m2409static/, then run collectstatic

### relationship type and the conditional entity

Problem: In the original Muir Web (Perl/Access), relationship type 'condition for (code = 5)' receives a different 
treatment from defined types such as food, water, shelter, and reproductive resources. When stored in the habitats 
dictionary every relationship with code 5 is re-assigned a unique numeric code using a counter (variable: new_relationship_counter), which is incremented for each new instance of  relationship type of 5. The changes proposed bellow accommodate all of the existing relationships under one set of mapping rules.

### States and Groups

States and groups are the two levels of organization in our habitat model. Habitat is made up of one or more states, 
and each state is made up of one or more groups. All elements will have at least one state. Multiple states are 
generally used when a species uses more than one distinct kind of habitat (e.g. summer and winter grounds).

A Group represents a set of conditions that are required to map the subject. In the case of wildlife they stand for 
categories like food, water, shelter or reproductive resources. Groups are also used to describe the conditions 
needed to map abiotic features and ecological communities. The members of a group are substitutable (added together 
using `union`); groups themselves are non-substitutable (multiplied together using `intersection`).

### strength and interaction
The goal of the changes to the strength concept and the introduction of interaction type and separating is to clarify 
the logic in the database and allow for more generalized functions on the mapping end of the application.

#### strength
Strength is a scalar value between 0 and 100 used to modify the influence of an object, and consequently the 
distribution of a subject.

#### interaction type
This property indicates whether the relationship is a required, enhancing, or attenuating influence. The interaction 
type determines the arithmetic rules for combining an object with the other members of its group.

Interaction types:

|name         |id  | operation                  |
|-------------|----|----------------------------|
|required     |0   |(object * strength)         |
|enhancing    |1   |(1 + (object * strength))   |
|attenuating  |2   |(1 - (object * strength))   |

## SPATIAL METHODS
All Muir Web element spatial data outputs are masked 16-bit-integer tifs with values from 0 to 100 representing the 
probability of that element in each cell. However, subset operations are capable of dealing with input tifs that 
represent arbitrary values (e.g. elevation in feet); these input elements are calculated manually and marked as 
'native units' in the database.

`union`  
`intersection`  
These atomic operations essentially add and multiply (respectively) lists of numpy arrays, clamping the result to a 
maximum of 100.

`combination`  
See https://goo.gl/FB5Jxc for an explanation of how states and groups are organized into union/intersection 
(and/or) combinations to map a Muir Web subject, based on the concepts of relationshiptype and habitatstate in the 
Mannahatta version of the Muir Web.

`subset`  
Calculate Muir Web subject as a subset of another grid or grids according to the logic specified in `subset_rule`. In 
fact this operation will execute any well-formed `subset_rule` with any number of Muir Web element referents. The 
subset rule must adhere to gdalnumeric syntax using +-/* or any numpy array functions (e.g. `logical_and()`) 
(http://www.gdal.org/gdal_calc.html) and use `[elementid]` as placeholders in calc string:  
https://stackoverflow.com/questions/3030480/numpy-array-how-to-select-indices-satisfying-multiple-conditions  
Example: `logical_and([31.00] >= 2, [31.00] <= 5)`

`adjacency`  
Calculate (at the object's maxprob) all cells within the distance in meters specified in the Muir Web subject's 
`adjacency_rule`.

## TODO
*Note: there are currently 1932 Muir Web elements*
- [ ] Update strength types and their descriptions. 
- [ ] Determine what we want to do about references - integrate old access records into wobsadmin_reference? Straight to zotero? Then populate for every element.
- [ ] Make sure of proper subset_rule for all elements where mw_definition = 2 (and in general); similar for adjacency
- [ ] For element descriptions previously used to contain rules, write human version
- [ ] welikia_mw_relationship: check states and groups
- [ ] class and aggregationtype: remove or revise/check to reflect categories for visualization

### SPECIES LIST
- [ ] Check the genus/species names that resulted from splitting name into name_genus and name_species
- [ ] Go through species that are not yet Muir Web elements (Where did values for s.mw_elementid < 10000 that don't 
match MW elements come from? Should they match MW elements? s.mw_elementid > 10000 were added via wobsadmin but no 
matching Muir Web elements were created). Once this is done, drop mw_elementid from e_species.
- [ ] Add new species
  - species requiring "per-borough" treatment - create MW elements (e.g. "south of moraine") that put them in the 
  right place
  - file review LIST
    - mannahatta_plant_summary2.0.mdb
    - FIN.FinalBirds.11-Joost03-09-08.2.xlsha
