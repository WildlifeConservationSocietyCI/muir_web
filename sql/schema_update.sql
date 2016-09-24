-- To set up a fresh instance of the objects necessary for the sql in this dir to run:
-- Select a db server that doesn't have an active mannahatta2409 instance already
-- In pg_admin, as administrative postgres user (create db statement must be run by itself):
-- (only if mannahatta user doesn't yet exist)
-- CREATE ROLE mannahatta LOGIN
--     ENCRYPTED PASSWORD 'md535041b17824854b4325d29f4f88ea1f5'
--     SUPERUSER INHERIT CREATEDB NOCREATEROLE NOREPLICATION;
-- (only if guest user doesn't yet exist)
-- CREATE ROLE guest LOGIN
-- NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
-- CREATE DATABASE mannahatta2409
--   WITH OWNER = mannahatta
--        ENCODING = 'UTF8'
--        TABLESPACE = pg_default
--        LC_COLLATE = 'en_US.UTF-8'
--        LC_CTYPE = 'en_US.UTF-8'
--        CONNECTION LIMIT = -1;
-- Not necessary but maybe good practice:
-- Switch to newly created mannahatta2409 db as administrative user and run:
-- CREATE extension postgis;
-- CREATE extension postgis_topology;
-- Then switch to newly created mannahatta2409 db as mannahatta user and restore muirweb_prerefactor.backup in this dir.

-- DROP ATTRIBUTES THAT ARE ENTIRELY UNNECESSARY

ALTER TABLE welikia_mw_element
DROP COLUMN mw_path,
DROP COLUMN mw_gridname,
DROP COLUMN externallink,
DROP COLUMN spatialsource,
DROP COLUMN notes,
DROP COLUMN lifetype;

ALTER TABLE welikia_mw_relationship
DROP COLUMN explicit,
DROP COLUMN spatialrelationship,
DROP COLUMN spatialcomment;

ALTER TABLE e_species DROP COLUMN mw_taxontype; -- constraint gets dropped as well

-- ADD COLUMNS WE'LL BE NEEDING IN THE REFACTOR

ALTER TABLE welikia_mw_element ADD COLUMN species_id integer;
ALTER TABLE welikia_mw_element ADD COLUMN subset_rule text;
ALTER TABLE welikia_mw_element ADD COLUMN adjacency_rule integer;
ALTER TABLE welikia_mw_element ADD COLUMN description text NOT NULL DEFAULT '';
-- These two refer to an outmoded Access table of 20 references that we need to integrate into wobsadmin_reference.
-- Leaving these here and clearly marking until we can come back and do that.
ALTER TABLE welikia_mw_element ADD COLUMN access_description_reference_id integer;
ALTER TABLE welikia_mw_element RENAME referencenumber TO access_reference_id;

-- ALTER TABLE e_species ADD COLUMN welikia_mw_element_id integer;
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

-- ADD NEW TABLES

CREATE TABLE e_likelihood
(
  id serial NOT NULL,
  name character varying(100) NOT NULL,
  CONSTRAINT e_likelihood_pkey PRIMARY KEY (id)
);

-- TODO: IMPLEMENT RELATIONSHIP GROUP

-- relationship type: value is a key to welikia_relationshiptype
-- -- these changes can only be made after relationship group is added
-- ALTER TABLE welikia_mw_relationship ADD COLUMN relationship_type integer NOT NULL;


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
