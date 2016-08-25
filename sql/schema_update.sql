
-- UPDATE ELEMENT DEFINITIONS
-- update adjacency
UPDATE  welikia_mw_element
   SET  mw_definition = 3 
 WHERE 
 		mw_definition = 6;

-- update combinations
UPDATE  welikia_mw_element
   SET  mw_definition = 1
 WHERE 
		mw_definition = 3 
		OR mw_definition = 4
		OR mw_definition = 5;
	 

-- update stops
UPDATE  welikia_mw_element
   SET  mw_definition = 0
 WHERE
    	mw_definition = 7
    	OR mw_definition = 8;

-- update welikia_mw_definitiontype
UPDATE 	welikia_mw_definitiontype
   SET	description = 'stop'
 WHERE  id = 0;

 UPDATE welikia_mw_definitiontype
   SET	description = 'combination'
 WHERE  id = 1;

 UPDATE welikia_mw_definitiontype
   SET	description = 'subset'
 WHERE  id = 2;

 UPDATE welikia_mw_definitiontype
   SET	description = 'adjacency'
 WHERE  id = 3;

DELETE FROM welikia_mw_definitiontype
 WHERE	id > 3 ;

-- DROP UNUSED ELEMENT ATTRIBUTES
ALTER TABLE welikia_mw_element
DROP COLUMN mw_path,
DROP COLUMN mw_gridname,
DROP COLUMN externallink,
DROP COLUMN spatialsource,
DROP COLUMN notes,
DROP COLUMN lifetype;

-- ADD COLUMNS TO WELIKIA_MW_ELEMENT
ALTER TABLE welikia_mw_element
ADD COLUMN subset_rule text NOT NULL DEFAULT ''::text,

UPDATE 	welikia_mw_element e
   SET 	subset_rule = (SELECT d.description
   FROM	welikia_mw_element_description d
   WHERE (d.id = e.description_id AND e.mw_definition = 2)
	  AND (d.description IS NOT NULL)
	  AND (e.automap = TRUE));

ALTER TABLE welikia_mw_element
ADD COLUMN adjacency_rule integer;
UPDATE 	welikia_mw_element e
   SET 	adjacency_rule = (SELECT d.description::integer
   FROM	welikia_mw_element_description d

   WHERE (d.id = e.description_id AND e.mw_definition = 3)
	 AND (d.description IS NOT NULL)
	 AND (e.automap = TRUE)
	 AND (d.description ~ E'^\\d+$'));

-- ADD POLARITY TO RELATIONSHIP
ALTER TABLE welikia_mw_relationship
ADD COLUMN polarity boolean NOT NULL DEFAULT TRUE;

UPDATE 	welikia_mw_relationship
   SET 	polarity = FALSE
   WHERE strengthtype = 2
   		 strengthtype = 4;

-- REFACTOR STRENGTH TYPES
-- new strength scale: 0 = 0.25, 1 = 0.50, 2 = 0.75, 3 = 1.0
UPDATE 	welikia_mw_relationship
   SET 	strengthtype_id = 2
   WHERE strengthtype_id = 6   	-- subcentral
   		 OR strengthtype_id = 2 -- attenuating
   		 ;

UPDATE 	welikia_mw_relationship
   SET 	strengthtype_id = 2
   WHERE strengthtype_id = 6   	-- subcentral
   		 OR strengthtype_id = 2 -- attenuating
   		 ;