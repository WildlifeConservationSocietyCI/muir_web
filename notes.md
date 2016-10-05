# CLASSES

Element

Relationship

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
    not sure if this can be done using numpy arrays

*conditional*

#Issues to Address

## subset conditionals

Problem - The conditional rules used to create subset elements are
contained within the description of the element as strings. These strings are the
literal arcpy Con statements which are then executed using eval(). There are numerous issues
with the formatting and syntax of these statements, which make this portion of the script buggy.

Goals

1) Abstract the logic of each conditional statement using a cleaner schema in the db.
2) Develop a way of reading and dynamically created conditional indexing statements
   in the subset method.

## relationship type and the conditional entity

Problem - Relationship type ‘condition for (code = 5)’, receives a different treatment from defined types such as food, water, shelter, and reproductive resource. When stored in the habitats dictionary every relationship with code 5 is re-assigned a unique numeric code using a counter (variable: new_relationship_counter), which is incremented for each new instance of  relationship type of 5.



## strength
is a value between 0 and 1 used to scale probability and consequently the effect of object rasters on the distribution of a subject.

## relationship type (polarity)
this flag indicates whether the relationship is a requirement or an attenuating influence.

## strength and relationship type
the goal of generalizing strengths and separating out the idea of positive and negative relationships clarifies the logic in the database and allows for more generalized functions on the mapping end of the application. 
