UPDATE welikia_mw_element
SET automap = FALSE
WHERE automap IS NULL;
UPDATE welikia_mw_element
SET automap = TRUE
WHERE automap = FALSE AND mw_path != ''; -- 88 rows

-- DROP ATTRIBUTES THAT ARE ENTIRELY UNNECESSARY

ALTER TABLE welikia_mw_element
DROP COLUMN mw_path,  -- path conventions moved to script
DROP COLUMN mw_gridname,  -- path conventions moved to script
DROP COLUMN externallink,  -- in e_species
DROP COLUMN spatialsource,  -- existing vals: 0,2. Obsolete.
--DROP COLUMN notes,  -- empty -- but good to have available
-- see comparison queries; may want to edit e_species.mw_likelihood before doing this
DROP COLUMN probability, -- dropping in favor of e_species.historical_likelihood
DROP COLUMN lifetype;  -- not used anywhere

DROP TABLE welikia_mw_probability;

ALTER TABLE welikia_mw_frequencytype RENAME description TO name_primary;
ALTER TABLE welikia_mw_frequencytype ADD COLUMN name_secondary character varying(255) NOT NULL DEFAULT '';

ALTER TABLE welikia_mw_relationship DROP COLUMN explicit;  -- = FALSE for all records; not used
-- DROP COLUMN spatialrelationship,  -- ? true/false. Not used anywhere.
-- DROP COLUMN spatialcomment;  -- ? 12 distinct vals, not used anywhere.

-- ? check apps to be sure we're using taxon_id everywhere
ALTER TABLE e_species DROP COLUMN mw_taxontype; -- constraint gets dropped as well

-- ADD COLUMNS WE'LL BE NEEDING IN THE REFACTOR

ALTER TABLE welikia_mw_element ADD COLUMN species_id integer;
ALTER TABLE welikia_mw_element ADD COLUMN subset_rule character varying(255) NOT NULL DEFAULT '';
ALTER TABLE welikia_mw_element ADD COLUMN adjacency_rule integer;
ALTER TABLE welikia_mw_element ADD COLUMN description text NOT NULL DEFAULT '';
ALTER TABLE welikia_mw_element ADD COLUMN native_units boolean NOT NULL DEFAULT FALSE;
-- These refer to an outmoded Access table of 20 references that we need to integrate into wobsadmin_reference.
-- Leaving these here and clearly marking until we can come back and do that.
ALTER TABLE welikia_mw_element ADD COLUMN access_description_reference_id integer;
ALTER TABLE welikia_mw_element RENAME referencenumber TO access_reference_id;
ALTER TABLE welikia_mw_element ALTER COLUMN access_reference_id DROP NOT NULL;
-- elementclass isn't used anywhere
ALTER TABLE welikia_mw_element RENAME elementclass TO access_elementclass;
ALTER TABLE welikia_mw_element ALTER COLUMN access_elementclass DROP NOT NULL;
ALTER TABLE welikia_mw_element ALTER COLUMN mw_taxontype DROP NOT NULL;
ALTER TABLE welikia_mw_element ALTER COLUMN mw_class DROP NOT NULL;
ALTER TABLE welikia_mw_element ALTER COLUMN aggregationtype DROP NOT NULL;
ALTER TABLE welikia_mw_element ADD COLUMN last_modified timestamp with time zone;

ALTER TABLE e_species ADD COLUMN name_genus character varying(255) NOT NULL DEFAULT '';
ALTER TABLE e_species ADD COLUMN name_species character varying(255) NOT NULL DEFAULT '';
-- TODO: create family and genus tables to contain species hierarchically (separating names a good first step)
ALTER TABLE e_species ADD COLUMN historical_likelihood SMALLINT;

-- Base function to update mwelement name from species. Can be called by itself if need be.
CREATE OR REPLACE FUNCTION public.update_mwelement_name_from_species(sid integer)
  RETURNS boolean AS
$BODY$
DECLARE
    r RECORD;

BEGIN
    FOR r in EXECUTE 'SELECT welikia_mw_element.id AS eid, COALESCE(name_genus, '''') || '' '' || COALESCE(name_species, '''') || '' ['' || COALESCE(name_common, '''') || '']'' AS name FROM e_species INNER JOIN welikia_mw_element ON (e_species.ide_species = welikia_mw_element.species_id) WHERE ide_species = $1;' USING sid
    LOOP
        EXECUTE 'UPDATE welikia_mw_element SET name = $1 WHERE id = $2' USING r.name, r.eid;
        RAISE NOTICE 'MW element % name updated from species %', r.eid, sid;
    END LOOP;

    RETURN TRUE;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.update_mwelement_name_from_species(integer)
  OWNER TO mannahatta;

-- Trigger function to call the mwelement name update function using new/updated data passed in by trigger
CREATE OR REPLACE FUNCTION public.update_mwelement_name_trigger()
  RETURNS trigger AS
$BODY$
BEGIN
    PERFORM update_mwelement_name_from_species(NEW.ide_species);
    RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.update_mwelement_name_trigger()
  OWNER TO mannahatta;

-- Actual trigger that tells postgres to run the mwelement name update whenever a species row is added/updated
CREATE TRIGGER mwelement_name_trigger_update
  AFTER INSERT OR UPDATE
  ON public.e_species
  FOR EACH ROW
  EXECUTE PROCEDURE public.update_mwelement_name_trigger();

DROP TRIGGER IF EXISTS searchtext_index_update ON public.e_species;
CREATE TRIGGER searchtext_index_update
    BEFORE INSERT OR UPDATE
    ON public.e_species
    FOR EACH ROW
    EXECUTE PROCEDURE tsvector_update_trigger('searchtext_index', 'pg_catalog.english', 'name_family', 'name_genus', 'name_species', 'name_common');


-- ADD NEW TABLES

CREATE TABLE e_likelihood
(
  id serial NOT NULL,
  name character varying(100) NOT NULL,
  CONSTRAINT e_likelihood_pkey PRIMARY KEY (id)
);
ALTER TABLE e_likelihood
  OWNER TO mannahatta;

CREATE TABLE welikia_mw_state_label
(
  id serial NOT NULL,
  name character varying(100) NOT NULL DEFAULT '',
  CONSTRAINT welikia_mw_state_label_pkey PRIMARY KEY (id),
  CONSTRAINT welikia_mw_state_label_name_uq UNIQUE (name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE welikia_mw_state_label
  OWNER TO mannahatta;

CREATE TABLE welikia_mw_state
(
  id serial NOT NULL,
  label_id integer REFERENCES welikia_mw_state_label,
  legacy_habitatstate_id integer,
  CONSTRAINT welikia_mw_state_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE welikia_mw_state
  OWNER TO mannahatta;

CREATE TABLE welikia_mw_group_label
(
  id serial NOT NULL,
  name character varying(100) NOT NULL DEFAULT '',
  notes text NOT NULL DEFAULT '',
  CONSTRAINT welikia_mw_group_label_pkey PRIMARY KEY (id),
  CONSTRAINT welikia_mw_group_label_name_uq UNIQUE (name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE welikia_mw_group_label
  OWNER TO mannahatta;

CREATE TABLE welikia_mw_group
(
  id serial NOT NULL,
  label_id integer REFERENCES welikia_mw_group_label,
  legacy_relationshiptype_id integer,
  CONSTRAINT welikia_mw_group_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE welikia_mw_group
  OWNER TO mannahatta;

-- create interaction type table
CREATE TABLE public.welikia_mw_interactiontype
(
   id serial,
   name character varying(100) NOT NULL,
   operation character varying(100) NOT NULL,
   CONSTRAINT welikia_mw_interaction_pkey PRIMARY KEY (id)
)
WITH (
  OIDS = FALSE
)
;
ALTER TABLE public.welikia_mw_interactiontype
  OWNER TO mannahatta;

ALTER TABLE welikia_mw_relationship ADD COLUMN state_id integer;
ALTER TABLE welikia_mw_relationship ADD COLUMN group_id integer;
ALTER TABLE welikia_mw_relationship ADD COLUMN interactiontype_id integer;
ALTER TABLE welikia_mw_relationship DROP CONSTRAINT mw_relationship_mw_habitatstate;


-- What follows is for the model inheritance approach we've abandoned for the time being.

-- ALTER TABLE e_species ADD COLUMN welikia_element_ptr_id integer;
-- ALTER TABLE e_species DROP CONSTRAINT wobsadmin_species_pkey;

-- ALTER TABLE welikia_mw_element ADD CONSTRAINT welikia_mw_element_reference_id_fk_wobsadmin_reference_id
--   FOREIGN KEY (reference_id) REFERENCES wobsadmin_reference (id) ON UPDATE NO ACTION ON DELETE NO ACTION;

-- ALTER TABLE welikia_mw_element ADD COLUMN welikia_element_ptr_id integer;
-- ALTER TABLE welikia_mw_element DROP CONSTRAINT welikia_mw_element_pkey;

-- Base element with properties common to e_species, welikia_mw_element, and any other variant of
-- a Muir Web element (e.g. ecocommunity) we want to create
-- CREATE TABLE welikia_element
-- (
--   id serial NOT NULL,
--   name_common character varying(255) NOT NULL,
--   description text NOT NULL,
--   CONSTRAINT welikia_element_pkey PRIMARY KEY (id)
-- )
-- WITH (
--   OIDS=FALSE
-- );
-- ALTER TABLE welikia_element
--   OWNER TO mannahatta;
