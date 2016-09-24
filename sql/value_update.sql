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

This field now refers to the effect an object's on the presence of its
subject. Enhancing and attenuating types increase and decrease the
suitability of "core habitat" through scaling multiplication.
The type attribute will point relationships to the appropriate operation.

The field will filled using old strength_types

relationship_types:
  required = 0      (object * weight)
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
New schema separates the idea of strength and relationship type
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

-- E LIKELIHOOD
-- fill lookup table
INSERT INTO e_likelihood (id, name)
VALUES (1, 'likely');

INSERT INTO e_likelihood (id, name)
VALUES (2, 'probable');

INSERT INTO e_likelihood (id, name)
VALUES (3, 'possible');

INSERT INTO e_likelihood (id, name)
VALUES (4, 'remotely possible');

-- update historical_likelihood based on mw_likelihood
UPDATE e_species
   SET historical_likelihood = 1
 WHERE mw_likelihood = 'Likely';

UPDATE e_species
   SET historical_likelihood = 2
 WHERE mw_likelihood = 'Probable';

UPDATE e_species
   SET historical_likelihood = 3
 WHERE mw_likelihood = 'Possible';

UPDATE e_species
   SET historical_likelihood = 4
 WHERE mw_likelihood = 'Remotely Possible';


UPDATE welikia_mw_element
SET description = d.description,
  access_description_reference_id = d.reference_id
FROM(SELECT e.id, COALESCE(ed.description, '') AS description, reference_id
  FROM welikia_mw_element e
  LEFT JOIN welikia_mw_element_description ed ON (e.description_id = ed.id)) AS d
WHERE welikia_mw_element.id = d.id;

UPDATE welikia_mw_element SET description = 'tubular red flowers such as salvia and trumpet creeper' WHERE id = 1548;
UPDATE welikia_mw_element SET description = 'well-drained' WHERE id = 202;
UPDATE welikia_mw_element SET description = '>256 mm in size' WHERE id = 172;
UPDATE welikia_mw_element SET description = 'combination of boulders and gravel' WHERE id = 174;
UPDATE welikia_mw_element SET description = 'shallow' WHERE id = 189;
UPDATE welikia_mw_element SET description = 'poorly drained' WHERE id = 201;
UPDATE welikia_mw_element SET description = 'wet ' WHERE id = 204;
UPDATE welikia_mw_element SET description = 'moist' WHERE id = 205;
UPDATE welikia_mw_element SET description = 'dry' WHERE id = 206;
UPDATE welikia_mw_element SET description = 'organic soils' WHERE id = 215;
UPDATE welikia_mw_element SET description = 'inorganic soils' WHERE id = 216;
UPDATE welikia_mw_element SET description = 'sand or gravel' WHERE id = 134;
UPDATE welikia_mw_element SET description = 'gently sloping' WHERE id = 32;
UPDATE welikia_mw_element SET description = 'vertical' WHERE id = 33;
UPDATE welikia_mw_element SET description = 'south-facing' WHERE id = 38;
UPDATE welikia_mw_element SET description = 'ravines' WHERE id = 44;
UPDATE welikia_mw_element SET description = 'slopes' WHERE id = 45;
UPDATE welikia_mw_element SET description = 'exposed' WHERE id = 52;
UPDATE welikia_mw_element SET description = 'sheltered' WHERE id = 53;
UPDATE welikia_mw_element SET description = '"subtidal": Below low tide (mean low water to 6 feet)' WHERE id = 106;
UPDATE welikia_mw_element SET description = '"intertidal": Littoral zone:  between low tide (mean low water) and high tide (mean high water)' WHERE id = 107;
UPDATE welikia_mw_element SET description = 'rough' WHERE id = 119;
UPDATE welikia_mw_element SET description = 'quiet waters' WHERE id = 120;
UPDATE welikia_mw_element SET description = 'silt or sand' WHERE id = 133;
UPDATE welikia_mw_element SET description = 'moderate to steep' WHERE id = 165;
UPDATE welikia_mw_element SET description = 'moderate to gentle' WHERE id = 166;
UPDATE welikia_mw_element SET description = '65-256 mm in size' WHERE id = 171;
UPDATE welikia_mw_element SET description = 'low terraces' WHERE id = 260;
UPDATE welikia_mw_element SET description = 'bluffs and headlands' WHERE id = 258;
UPDATE welikia_mw_element SET description = 'a hardwood forest with oaks (Quercus spp.) and beech (Fagus grandifolia) codominant that occurs in dry well-drained' WHERE id = 394;
UPDATE welikia_mw_element SET description = 'the siting of Lenape villages appears to be a function of topographic exposure (protection from prevailing winds)' WHERE id = 405;
UPDATE welikia_mw_element SET description = 'in general, ecological communities are a function of geomorphological feature, innundation (water depth), water salinity, soil type, climate, and disturbance regime' WHERE id = 457;
UPDATE welikia_mw_element SET description = 'Height of the land above mean tide. Elevation is a function of topography.' WHERE id = 30;
UPDATE welikia_mw_element SET description = 'Precipitation that falls in the form of solid water. Snowfall is a function of weather and topographic position.' WHERE id = 14;
UPDATE welikia_mw_element SET description = 'animal physical disturbance is trampling' WHERE id = 334;
UPDATE welikia_mw_element SET description = 'Precipitation that falls in the form of liquid water. Rainfall is a function of temperature.' WHERE id = 13;

UPDATE e_species SET name_common = 'winter squash (pumpkin)' WHERE ide_species = 1150;
UPDATE e_species SET name_common = 'summer squash (field pumpkin)' WHERE ide_species = 1151;
UPDATE e_species SET name_common = 'maize (corn)' WHERE ide_species = 1575;
UPDATE e_species SET name_scientific = 'Ambystoma jeffersonianum' WHERE ide_species = 4316;
UPDATE e_species
SET name_genus = s.name_genus,
name_species = s.name_species
FROM (
    SELECT ide_species, name_scientific,
        COALESCE(split_part(name_scientific, ' ', 1), '') as name_genus,
        COALESCE(substring(name_scientific from E'[^\\s]*\\s(.+)$'), '') AS name_species,
        name_common
    FROM e_species
    ORDER BY name_scientific
) AS s
WHERE e_species.ide_species = s.ide_species;
-- TODO: When going through species/elements, check the genus/species names that result from this

UPDATE welikia_mw_element e SET mw_scientificname =
  COALESCE(
  (SELECT mw_scientificname || ' [' || mw_commonname || ']' AS name
    FROM welikia_mw_element e2
    WHERE lower(mw_scientificname) != lower(mw_commonname)
    AND elementid < 29038
    AND elementid > 1000
    AND (mw_definition = 1 OR mw_definition = 4)
    AND id NOT IN (585, 1508, 1641, 1699, 1704, 1725)
    AND e.id = e2.id
  ), e.mw_scientificname);

UPDATE welikia_mw_element e SET species_id =
  (SELECT ide_species
    FROM e_species s
    WHERE e.elementid = s.mw_elementid);

-- UPDATE e_species s SET welikia_mw_element_id =
--   (SELECT id
--     FROM welikia_mw_element e
--     WHERE s.mw_elementid = e.elementid);


-- What follows is for the model inheritance approach we've abandoned for the time being.

-- insert new welikia_elements that are species. keep existing ids because they are
-- more likely to mean something somewhere else.
-- INSERT INTO welikia_element (id, name_common, description)
--     SELECT ide_species, name_common, description FROM e_species;
--
-- UPDATE e_species SET e_species_ptr_id = ide_species;

-- add temp_id to welikia_mw_element
-- add sequence for temp_id that starts at the max of the welikia_element id seq
-- UPDATE welikia_mw_element SET temp_id = DEFAULT;
-- insert new welikia_elements to link welikia_mw_element to
-- INSERT INTO welikia_element (id, name_common, description)
--     SELECT temp_id, mw_commonname,
--     FROM welikia_mw_element
-- drop temp_id seq
-- drop temp_id
