-- UPDATE ELEMENT DEFINITIONS
-- update adjacency

UPDATE welikia_mw_element
   SET mw_definition = 3
 WHERE mw_definition = 6;

 -- update combinations

UPDATE welikia_mw_element
   SET mw_definition = 1
 WHERE mw_definition = 3
    OR mw_definition = 4
    OR mw_definition = 5;

 -- update stops

UPDATE welikia_mw_element
   SET mw_definition = 0
 WHERE mw_definition = 7
    OR mw_definition = 8;

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

 -- DROP UNUSED ELEMENT ATTRIBUTES

ALTER TABLE welikia_mw_element
DROP COLUMN mw_path,
DROP COLUMN mw_gridname,
DROP COLUMN externallink,
DROP COLUMN spatialsource,
DROP COLUMN notes,
DROP COLUMN lifetype;

 -- ADD COLUMNS TO WELIKIA_MW_ELEMENT

ALTER TABLE welikia_mw_element ADD COLUMN subset_rule text NOT NULL DEFAULT ''::text,

UPDATE welikia_mw_element AS e
   SET subset_rule =
       (SELECT d.description
          FROM welikia_mw_element_description AS d
         WHERE (d.id = e.description_id
           AND e.mw_definition = 2)
           AND (d.description IS NOT NULL)
           AND (e.automap = TRUE));


ALTER TABLE welikia_mw_element ADD COLUMN adjacency_rule integer;

UPDATE welikia_mw_element AS e
   SET adjacency_rule =
	   (SELECT d.description::integer
		  FROM welikia_mw_element_description AS d
		 WHERE (d.id = e.description_id
  	       AND e.mw_definition = 3)
		   AND (d.description IS NOT NULL)
		   AND (e.automap = TRUE)
		   AND (d.description ~ E'^\\d+$'));

-- IMPLEMENT RELATIONSHIP GROUP
/*
this statement will be written by Kim
*/

-- IMPLEMENT RELATIONSHIP TYPE
/*
"relationship_type" was previously used to group similar kinds of
requirements (food, water, shelter).

This field now refers to the direction of an object's effect on its
subject. Enhancing and attenuating types scale the "core habitat"
(required) in positive and negative directions respectivly. The type
will point relationships to the appropriate arethmetic operation.

The field will filled using old strength_types

relationship_types:
	required = 0		(object * weigth)
	enhancing = 1		1 + (object * weight)
	attenuating = 2 	1 - (object * weight)
*/

ALTER TABLE welikia_mw_relationship ADD COLUMN relationship_type integer NOT NULL;

-- update required relationship_type
UPDATE welikia_mw_relationship
   SET relationship_type = 0
 WHERE strengthtype = 0  -- central
    OR strengthtype = 3  -- required
    OR strengthtype = 5  -- central
    OR strengthtype = 6; -- subcentral

-- update enhancing relationship_type
UPDATE welikia_mw_relationship
   SET relationship_type = 1
 WHERE strengthtype = 1;  -- attenuating

-- update attenuating relationship_type
UPDATE welikia_mw_relationship
   SET relationship_type = 2
 WHERE strengthtype = 2  -- attenuating
    OR strengthtype = 4; -- exclusionary

-- REFACTOR STRENGTH TYPES
/*
new schema seperates the idea of strength and type.
ie. a relationship can be strongly attenuating or strongly enhancing.
the new strength is a scale ranging from weak -> strong.
only refactor after the new relationship_type field is populated
new strength scale:
	0 = 0.25,
	1 = 0.50
	2 = 0.75
	3 = 1.00
*/

UPDATE welikia_mw_relationship
   SET strengthtype_id = 2
 WHERE strengthtype_id = 6  -- subcentral
    OR strengthtype_id = 2; -- attenuating


UPDATE welikia_mw_relationship
   SET strengthtype_id = 3
 WHERE strengthtype_id = 0  -- central
    OR strengthtype_id = 3  -- required
    OR strengthtype_id = 4  -- exclusionary
    OR strengthtype_id = 5; -- central


-- DROP UNUSED RELATIONSHIP ATTIBUTES
ALTER TABLE welikia_mw_relationship
DROP COLUMN explicit,
DROP COLUMN spatialrelationship,
DROP COLUMN spatialcomment;
