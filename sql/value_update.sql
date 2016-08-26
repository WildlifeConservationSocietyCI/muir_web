-- UPDATE ELEMENT DEFINITIONS

-- update combinations
UPDATE welikia_mw_element
   SET mw_definition = 1
 WHERE mw_definition = 1  -- union
    OR mw_definition = 3  -- intersection
    OR mw_definition = 4  -- dependency
    OR mw_definition = 5; -- union

-- update adjacency
UPDATE welikia_mw_element
   SET mw_definition = 3
 WHERE mw_definition = 6; -- spatial adjacency

 -- update stops
UPDATE welikia_mw_element
   SET mw_definition = 0
 WHERE mw_definition = 0  -- undefined
    OR mw_definition = 7  -- temporal adjacency
    OR mw_definition = 8; -- stop

 -- update welikia_mw_definitiontype

UPDATE welikia_mw_definitiontype
   SET description = 'stop'
 WHERE id = 0;


UPDATE welikia_mw_definitiontype
   SET description = 'combination'
 WHERE id = 1;


UPDATE welikia_mw_definitiontype
   SET description = 'subset'
 WHERE id = 2;


UPDATE welikia_mw_definitiontype
   SET description = 'adjacency'
 WHERE id = 3;


DELETE
  FROM welikia_mw_definitiontype
 WHERE id > 3;


-- UPDATE SUBSET RULES
UPDATE welikia_mw_element AS e
   SET subset_rule =
       (SELECT d.description
          FROM welikia_mw_element_description AS d
         WHERE (d.id = e.description_id
           AND e.mw_definition = 2)
           AND (d.description IS NOT NULL)
           AND (e.automap = TRUE));

-- UPDATE ADJACENCY RULES
UPDATE welikia_mw_element AS e
   SET adjacency_rule =
       (SELECT d.description::integer
          FROM welikia_mw_element_description AS d
         WHERE (d.id = e.description_id
           AND e.mw_definition = 3)
           AND (d.description IS NOT NULL)
           AND (e.automap = TRUE)
           AND (d.description ~ E'^\\d+$'));


/*
"relationship_type" was previously used to group similar kinds of
requirements (food, water, shelter).

This field now refers to the effect an object's on the pressence of its
subject. Enhancing and attenuating types increase and decrease the
suitability of "core habitat" through scaling multiplication.
The type attribute will point relationships to the appropriate operation.

The field will filled using old strength_types

relationship_types:
  required = 0      (object * weigth)
  enhancing = 1     1 + (object * weight)
  attenuating = 2   1 - (object * weight)
*/

-- update required relationship_type
-- UPDATE welikia_mw_relationship
--    SET relationship_type = 0
--  WHERE strengthtype = 0  -- central
--     OR strengthtype = 3  -- required
--     OR strengthtype = 5  -- central
--     OR strengthtype = 6; -- subcentral

-- -- update enhancing relationship_type
-- UPDATE welikia_mw_relationship
--    SET relationship_type = 1
--  WHERE strengthtype = 1;  -- enhancing

-- -- update attenuating relationship_type
-- UPDATE welikia_mw_relationship
--    SET relationship_type = 2
--  WHERE strengthtype = 2  -- attenuating
--     OR strengthtype = 4; -- exclusionary

-- REFACTOR STRENGTH TYPES
/*
New schema seperates the idea of strength and relationship type
(ie. a relationship can be strongly attenuating or strongly enhancing).
The new strength value is on a scale ranging from weak (0) -> strong (1).
Only refactor after the new relationship_type field is populated
new strength scale:
  0 = 0.25,
  1 = 0.50
  2 = 0.75
  3 = 1.00
*/

-- UPDATE welikia_mw_relationship
--    SET strengthtype_id = 2
--  WHERE strengthtype_id = 6  -- subcentral
--     OR strengthtype_id = 2; -- attenuating


-- UPDATE welikia_mw_relationship
--    SET strengthtype_id = 3
--  WHERE strengthtype_id = 0  -- central
--     OR strengthtype_id = 3  -- required
--     OR strengthtype_id = 4  -- exclusionary
--     OR strengthtype_id = 5; -- central
