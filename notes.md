# CLASSES

Element

Relationship

# SPECIES LIST

varify the all mannahatta species are in wobsadmin
compare refferences

file review LIST
mannahatta_plant_summary2.0.mdb
FIN.FinalBirds.11-Joost03-09-08.2.xlsha

do we divide by bourogh

develop rule set
filter by introduced
add in extinct

add new species

count observations
reference to probability

# SETUP METHODS

*def read_db* [completed]
parse json feed and convert to element and relationship objects

*status*
identify the elements that have already been mapped
and those that still need to be mapped

*create_object_list* [completed]
for each element that needs to be mapped
collect and organize relationships by state and type

# MAPPING METHODS

*union*

*subset*

*combination*

*adjacency*

*conditional*

# DATABASE UPDATE

## subset conditionals
Problem - The conditional rules used to create subset elements are contained within the description of the element as strings. These strings are the literal arcpy Con statements which are then executed using eval(). There are numerous issues with the formatting and syntax of these statements, which make this portion of the script buggy.

Goals

1) Abstract the logic of each conditional statement using a cleaner schema in the db.
2) Develop a way of reading and dynamically created conditional indexing statements
   in the subset method.

## relationship type and the conditional entity

Problem - Relationship type ‘condition for (code = 5)’, receives a different treatment from defined types such as food, water, shelter, and reproductive resource. When stored in the habitats dictionary every relationship with code 5 is re-assigned a unique numeric code using a counter (variable: new_relationship_counter), which is incremented for each new instance of  relationship type of 5. The changes proposed bellow accommodate all of the existing relationships under one set of mapping rules.

## States and Groups

States and groups are the two levels of organization in our habitat model. Habitat is made up of one or more states, and each state is made up of one or more groups. All elements will have at least one state. Multiple states are generally used when a species uses more than one distinct kinds of habitat (summer and winter grounds).

A Group represents a set of conditions that are required to map the subject. In the case of wildlife they stand for categories like food, water, shelter or reproductive resources. Groups are also used to describe the conditions needed to map abiotic feature and ecological community. The members of a group are substitutable, however groups themselves are non-substitutable.

Interpreting and coding expert opinion and textual habitat descriptions

## strength and interaction
the goal of the changes to the strength concept and the introduction of influence type and separating is to clarify the logic in the database and allows for more generalized functions on the mapping end of the application.

### strength
Strength is a scalar value between 0 and 1 used to modify the influence of an object, and consequently the distribution of a subject.

### interaction type
This property indicates whether the relationship is a requirement, enhancing or attenuating influence. The interaction type determines the arithemtic rules for combining an object with the other members of its group.

interaction types:

|name         |id  | operation                  |
|-------------|----|----------------------------|
|required     |0   |(object * strength)         |
|enhancing    |1   |(1 + (object * strength))   |
|attenuating  |2   |(1 - (object * strength))   |


