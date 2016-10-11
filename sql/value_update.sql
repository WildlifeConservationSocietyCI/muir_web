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


-- INSERT VALUES INTO INTERACTION TYPE TABLE
INSERT INTO welikia_mw_interactiontype (name, operation) VALUES ('required', '(object * weight)');
INSERT INTO welikia_mw_interactiontype (name, operation) VALUES ('enhancing', '(1 + (object * weight))');
INSERT INTO welikia_mw_interactiontype (name, operation) VALUES ('exclusionary', '(1 - (object * weight))');

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


-- REFACTOR GROUPING SYSTEM (relationshiptype and habitatstate)
-- update relationship state and group function
CREATE OR REPLACE FUNCTION public.update_relationships()
  RETURNS boolean AS
$BODY$
DECLARE
  s_new_event_row welikia_mw_state%ROWTYPE;
  g_new_event_row welikia_mw_group%ROWTYPE;
  s RECORD;
  g RECORD;
  g5 RECORD;
  mw_e welikia_mw_element;
  mw_r welikia_mw_relationship;
BEGIN
    FOR mw_e IN
    SELECT * FROM welikia_mw_element

    -- for elements in welikia_me_element table
    LOOP

      RAISE NOTICE 'MW element %', mw_e.mw_commonname;

      -- for distinct states in an element's relationships
      FOR s IN SELECT DISTINCT rels.habitatstate_id
      FROM welikia_mw_relationship AS rels
      WHERE rels.id_subject = mw_e.elementid
      LOOP
        RAISE NOTICE 'state: %', s.habitatstate_id;
        -- create a new record in welikia_mw_states
        -- and return into new_event_row

        -- loop over relationshiptype sets
        FOR g in SELECT DISTINCT rels.relationshiptype_id
        FROM welikia_mw_relationship AS rels
        WHERE rels.id_subject = mw_e.elementid
        AND rels.habitatstate_id = s.habitatstate_id
        LOOP
          -- for each record with relationshiptype_id = 5 create new group_id
          IF g.relationshiptype_id = 5 THEN
            FOR g5 IN SELECT *
            FROM welikia_mw_relationship AS rels
            WHERE rels.id_subject = mw_e.elementid
            AND rels.habitatstate_id = s.habitatstate_id
            AND rels.relationshiptype_id = 5

            LOOP
              WITH new_event AS (
              INSERT INTO welikia_mw_group (legacy_relationshiptype_id) VALUES (g5.relationshiptype_id)
              RETURNING *
              )
              SELECT * FROM new_event INTO g_new_event_row;
              RAISE NOTICE 'new group id %', g_new_event_row.id;
              -- update relationship group in welikia_mw_relationship using new group id
              UPDATE welikia_mw_relationship
              SET group_id = g_new_event_row.id
              WHERE id_subject = mw_e.elementid
                AND welikia_mw_relationship.habitatstate_id = s.habitatstate_id
                AND welikia_mw_relationship.relationshiptype_id = g_new_event_row.legacy_relationshiptype_id
                And welikia_mw_relationship.id = g5.id;
            END LOOP; -- end relationshiptype 5 loop
         -- else create new group_id for all relationships with shared relationshiptype_id
         ELSE
            WITH new_event AS (
            INSERT INTO welikia_mw_group (legacy_relationshiptype_id) VALUES (g.relationshiptype_id)
            RETURNING *
            )
            SELECT * FROM new_event INTO g_new_event_row;

            RAISE NOTICE 'new group id %', g_new_event_row.id;
            -- update relationship group in welikia_mw_relationship using new group id
            UPDATE welikia_mw_relationship
            SET group_id = g_new_event_row.id
            WHERE id_subject = mw_e.elementid
              AND welikia_mw_relationship.habitatstate_id = s.habitatstate_id
              AND welikia_mw_relationship.relationshiptype_id = g_new_event_row.legacy_relationshiptype_id;
          END IF; -- end relationshiptype_id conditional
        END LOOP; -- end group loop

        WITH new_event AS (
        INSERT INTO welikia_mw_state (legacy_habitatstate_id) VALUES (s.habitatstate_id)
        RETURNING *
        )
        SELECT * FROM new_event INTO s_new_event_row;

        RAISE NOTICE 'new state id %', s_new_event_row.id;
        -- update relationship state in welikia_mw_relationship using new state id
        UPDATE welikia_mw_relationship
        SET habitatstate_id = s_new_event_row.id
        WHERE id_subject = mw_e.elementid
          AND welikia_mw_relationship.habitatstate_id = s_new_event_row.legacy_habitatstate_id;

      END LOOP; -- end state loop
    END LOOP; -- end element loop
    RETURN TRUE;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.update_relationships()
  OWNER TO mannahatta;

SELECT update_relationships();

-- move new habitat state to state_id column
UPDATE welikia_mw_relationship
   SET state_id = habitatstate_id;

-- REFACTOR STRENGTH AND INTERACTION TYPES
/*
New schema separates the idea of strength and relationship type
(ie. a relationship can be strongly attenuating or strongly enhancing).
The new strength value is on a scale ranging from weak (0) -> strong (1).
Only refactor after the interactiontype_id field is populated
new strength scale:
  0 = 25,
  1 = 50
  2 = 75
  3 = 100
*/

-- update interactiontype_id based on original strength values
UPDATE welikia_mw_relationship AS r
   SET interactiontype_id = 1   -- requirement
   WHERE r.strengthtype_id = 0  -- central
      OR r.strengthtype_id = 3  -- required
      OR r.strengthtype_id = 5  -- central
      OR r.strengthtype_id = 6; -- subcentral

UPDATE welikia_mw_relationship AS r
   SET interactiontype_id = 1   -- requirement
   WHERE r.strengthtype_id = 1;  -- enhancing

UPDATE welikia_mw_relationship AS r
   SET interactiontype_id = 2   -- exculsionary
   WHERE r.strengthtype_id = 2  -- attenuating
      OR r.strengthtype_id = 4; -- exclusionary

-- update strengthtype table
UPDATE welikia_mw_strengthtype
   SET prob = 25
   WHERE id = 0;

UPDATE welikia_mw_strengthtype
  SET prob = 50
  WHERE id = 1;

UPDATE welikia_mw_strengthtype
   SET prob = 75
   WHERE id = 2;

UPDATE welikia_mw_strengthtype
    SET prob = 100
    WHERE id = 3;

-- delete unused strengthtype records
DELETE FROM welikia_mw_strengthtype
WHERE id > 3;

-- update strengthtype_id in welikia_mw_relationship
UPDATE welikia_mw_relationship
   SET strengthtype_id = 2  -- 75%
 WHERE strengthtype_id = 6  -- subcentral
    OR strengthtype_id = 2; -- attenuating


UPDATE welikia_mw_relationship
   SET strengthtype_id = 3  -- 100%`
 WHERE strengthtype_id = 0  -- central
    OR strengthtype_id = 3  -- required
    OR strengthtype_id = 4  -- exclusionary
    OR strengthtype_id = 5; -- central

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
