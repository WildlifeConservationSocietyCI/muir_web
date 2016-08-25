
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

--
-- SELECT 	elementid, 
-- 	mw_commonname, 
-- 	mw_definition, 
-- 	automap,
-- 	p.name,
-- 	es.mw_likelihood
-- FROM welikia_mw_element e

-- INNER JOIN welikia_mw_probability p
-- 	   ON e.probability = p.id

--       JOIN e_species es
--            ON e.elementid = es.mw_elementid
-- WHERE es.mw_likelihood != p.name