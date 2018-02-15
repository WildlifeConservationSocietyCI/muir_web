-- Keep unique constraint: elementid must exist in e_species AND be unique within welikia_mw_element
ALTER TABLE e_species DROP CONSTRAINT wobsadmin_species_mw_elementid_key;
ALTER TABLE e_species DROP COLUMN mw_elementid;
-- FK to species but field can be null
ALTER TABLE welikia_mw_element ADD CONSTRAINT welikia_mw_element_e_species_fkey FOREIGN KEY (species_id)
  REFERENCES e_species (ide_species) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE welikia_mw_element ADD CONSTRAINT welikia_mw_element_species_id_key UNIQUE (species_id);
-- ALTER TABLE e_species ADD CONSTRAINT e_species_elementid_key UNIQUE (welikia_mw_element_id);
-- ALTER TABLE e_species ADD CONSTRAINT e_species_mw_elementid_fk_welikia_mw_element_elementid
--   FOREIGN KEY (welikia_mw_element_id) REFERENCES welikia_mw_element (elementid) ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE e_species
  ADD CONSTRAINT e_species_historical_likelihood_fkey FOREIGN KEY (historical_likelihood)
  REFERENCES e_likelihood (id) MATCH SIMPLE;

-- Need to remove references to obsolete e_species fields before we can drop them
CREATE OR REPLACE VIEW public.noncanonicalvals AS
 SELECT DISTINCT 'p_climate'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_climate.name AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_climate p1
     LEFT JOIN p_climate p2 ON p1.ide_param = p2.ide_param AND p1.ide_climate = p2.ide_climate AND p2.canonical = true
     JOIN e_climate ON p1.ide_climate = e_climate.ide_climate
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_distance'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_distance.name AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_distance p1
     LEFT JOIN p_distance p2 ON p1.ide_param = p2.ide_param AND p1.ide_distance = p2.ide_distance AND p2.canonical = true
     JOIN e_distance ON p1.ide_distance = e_distance.ide_distance
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_distance_transportmode_lifestyle'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_distance.name AS entity1,
    e_transportmode.name AS entity2,
    e_lifestyle.name AS entity3
   FROM p_distance_transportmode_lifestyle p1
     LEFT JOIN p_distance_transportmode_lifestyle p2 ON p1.ide_param = p2.ide_param AND p1.ide_distance = p2.ide_distance AND p1.ide_transportmode = p2.ide_transportmode AND p1.ide_lifestyle = p2.ide_lifestyle AND p2.canonical = true
     JOIN e_distance ON p1.ide_distance = e_distance.ide_distance
     JOIN e_transportmode ON p1.ide_transportmode = e_transportmode.ide_transportmode
     JOIN e_lifestyle ON p1.ide_lifestyle = e_lifestyle.ide_lifestyle
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_ecosystem'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_ecosystem.name AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_ecosystem p1
     LEFT JOIN p_ecosystem p2 ON p1.ide_param = p2.ide_param AND p1.ide_ecosystem = p2.ide_ecosystem AND p2.canonical = true
     JOIN e_ecosystem ON p1.ide_ecosystem = e_ecosystem.ide_ecosystem
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_ecosystem_fuel'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_ecosystem.name AS entity1,
    e_fuel.name AS entity2,
    NULL::text AS entity3
   FROM p_ecosystem_fuel p1
     LEFT JOIN p_ecosystem_fuel p2 ON p1.ide_param = p2.ide_param AND p1.ide_ecosystem = p2.ide_ecosystem AND p1.ide_fuel = p2.ide_fuel AND p2.canonical = true
     JOIN e_ecosystem ON p1.ide_ecosystem = e_ecosystem.ide_ecosystem
     JOIN e_fuel ON p1.ide_fuel = e_fuel.ide_fuel
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_freightmode_ecosystem'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_freightmode.name AS entity1,
    e_ecosystem.name AS entity2,
    NULL::text AS entity3
   FROM p_freightmode_ecosystem p1
     LEFT JOIN p_freightmode_ecosystem p2 ON p1.ide_param = p2.ide_param AND p1.ide_ecosystem = p2.ide_ecosystem AND p1.ide_freightmode = p2.ide_freightmode AND p2.canonical = true
     JOIN e_ecosystem ON p1.ide_ecosystem = e_ecosystem.ide_ecosystem
     JOIN e_freightmode ON p1.ide_freightmode = e_freightmode.ide_freightmode
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_freightmode_fuel'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_freightmode.name AS entity1,
    e_fuel.name AS entity2,
    NULL::text AS entity3
   FROM p_freightmode_fuel p1
     LEFT JOIN p_freightmode_fuel p2 ON p1.ide_param = p2.ide_param AND p1.ide_fuel = p2.ide_fuel AND p1.ide_freightmode = p2.ide_freightmode AND p2.canonical = true
     JOIN e_fuel ON p1.ide_fuel = e_fuel.ide_fuel
     JOIN e_freightmode ON p1.ide_freightmode = e_freightmode.ide_freightmode
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_freightmode_lifestyle'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_freightmode.name AS entity1,
    e_lifestyle.name AS entity2,
    NULL::text AS entity3
   FROM p_freightmode_lifestyle p1
     LEFT JOIN p_freightmode_lifestyle p2 ON p1.ide_param = p2.ide_param AND p1.ide_lifestyle = p2.ide_lifestyle AND p1.ide_freightmode = p2.ide_freightmode AND p2.canonical = true
     JOIN e_lifestyle ON p1.ide_lifestyle = e_lifestyle.ide_lifestyle
     JOIN e_freightmode ON p1.ide_freightmode = e_freightmode.ide_freightmode
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_fuel'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_fuel.name AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_fuel p1
     LEFT JOIN p_fuel p2 ON p1.ide_param = p2.ide_param AND p1.ide_fuel = p2.ide_fuel AND p2.canonical = true
     JOIN e_fuel ON p1.ide_fuel = e_fuel.ide_fuel
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_fuel_lifestyle'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_fuel.name AS entity1,
    e_lifestyle.name AS entity2,
    NULL::text AS entity3
   FROM p_fuel_lifestyle p1
     LEFT JOIN p_fuel_lifestyle p2 ON p1.ide_param = p2.ide_param AND p1.ide_lifestyle = p2.ide_lifestyle AND p1.ide_fuel = p2.ide_fuel AND p2.canonical = true
     JOIN e_lifestyle ON p1.ide_lifestyle = e_lifestyle.ide_lifestyle
     JOIN e_fuel ON p1.ide_fuel = e_fuel.ide_fuel
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_fuel_transportmode'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_fuel.name AS entity1,
    e_transportmode.name AS entity2,
    NULL::text AS entity3
   FROM p_fuel_transportmode p1
     LEFT JOIN p_fuel_transportmode p2 ON p1.ide_param = p2.ide_param AND p1.ide_transportmode = p2.ide_transportmode AND p1.ide_fuel = p2.ide_fuel AND p2.canonical = true
     JOIN e_transportmode ON p1.ide_transportmode = e_transportmode.ide_transportmode
     JOIN e_fuel ON p1.ide_fuel = e_fuel.ide_fuel
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_global'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_global.name AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_global p1
     LEFT JOIN p_global p2 ON p1.ide_param = p2.ide_param AND p1.ide_global = p2.ide_global AND p2.canonical = true
     JOIN e_global ON p1.ide_global = e_global.ide_global
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_habitat_ecosystem'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_habitat.name AS entity1,
    e_ecosystem.name AS entity2,
    NULL::text AS entity3
   FROM p_habitat_ecosystem p1
     LEFT JOIN p_habitat_ecosystem p2 ON p1.ide_param = p2.ide_param AND p1.ide_ecosystem = p2.ide_ecosystem AND p1.ide_habitat = p2.ide_habitat AND p2.canonical = true
     JOIN e_ecosystem ON p1.ide_ecosystem = e_ecosystem.ide_ecosystem
     JOIN e_habitat ON p1.ide_habitat = e_habitat.ide_habitat
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_lifestyle'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_lifestyle.name AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_lifestyle p1
     LEFT JOIN p_lifestyle p2 ON p1.ide_param = p2.ide_param AND p1.ide_lifestyle = p2.ide_lifestyle AND p2.canonical = true
     JOIN e_lifestyle ON p1.ide_lifestyle = e_lifestyle.ide_lifestyle
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_month_climate'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_month.name AS entity1,
    e_climate.name AS entity2,
    NULL::text AS entity3
   FROM p_month_climate p1
     LEFT JOIN p_month_climate p2 ON p1.ide_param = p2.ide_param AND p1.ide_climate = p2.ide_climate AND p1.ide_month = p2.ide_month AND p2.canonical = true
     JOIN e_climate ON p1.ide_climate = e_climate.ide_climate
     JOIN e_month ON p1.ide_month = e_month.ide_month
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_month_precipevent_climate'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_month.name AS entity1,
    e_precipevent.name AS entity2,
    e_climate.name AS entity3
   FROM p_month_precipevent_climate p1
     LEFT JOIN p_month_precipevent_climate p2 ON p1.ide_param = p2.ide_param AND p1.ide_month = p2.ide_month AND p1.ide_precipevent = p2.ide_precipevent AND p1.ide_climate = p2.ide_climate AND p2.canonical = true
     JOIN e_month ON p1.ide_month = e_month.ide_month
     JOIN e_precipevent ON p1.ide_precipevent = e_precipevent.ide_precipevent
     JOIN e_climate ON p1.ide_climate = p2.ide_climate
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_species'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    array_to_string(ARRAY[e_species.name_genus, ' '::character varying, e_species.name_species, ' ['::character varying, e_species.name_common, ']'::character varying], ''::text) AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_species p1
     LEFT JOIN p_species p2 ON p1.ide_param = p2.ide_param AND p1.ide_species = p2.ide_species AND p2.canonical = true
     JOIN e_species ON p1.ide_species = e_species.ide_species
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_species_habitat'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    array_to_string(ARRAY[e_species.name_genus, ' '::character varying, e_species.name_species, ' ['::character varying, e_species.name_common, ']'::character varying], ''::text) AS entity1,
    e_habitat.name AS entity2,
    NULL::text AS entity3
   FROM p_species_habitat p1
     LEFT JOIN p_species_habitat p2 ON p1.ide_param = p2.ide_param AND p1.ide_habitat = p2.ide_habitat AND p1.ide_species = p2.ide_species AND p2.canonical = true
     JOIN e_habitat ON p1.ide_habitat = e_habitat.ide_habitat
     JOIN e_species ON p1.ide_species = e_species.ide_species
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_taxon'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_taxon.name AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_taxon p1
     LEFT JOIN p_taxon p2 ON p1.ide_param = p2.ide_param AND p1.ide_taxon = p2.ide_taxon AND p2.canonical = true
     JOIN e_taxon ON p1.ide_taxon = e_taxon.ide_taxon
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_transportmode_ecosystem'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_transportmode.name AS entity1,
    e_ecosystem.name AS entity2,
    NULL::text AS entity3
   FROM p_transportmode_ecosystem p1
     LEFT JOIN p_transportmode_ecosystem p2 ON p1.ide_param = p2.ide_param AND p1.ide_ecosystem = p2.ide_ecosystem AND p1.ide_transportmode = p2.ide_transportmode AND p2.canonical = true
     JOIN e_ecosystem ON p1.ide_ecosystem = e_ecosystem.ide_ecosystem
     JOIN e_transportmode ON p1.ide_transportmode = e_transportmode.ide_transportmode
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_transportmode_lifestyle'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_transportmode.name AS entity1,
    e_lifestyle.name AS entity2,
    NULL::text AS entity3
   FROM p_transportmode_lifestyle p1
     LEFT JOIN p_transportmode_lifestyle p2 ON p1.ide_param = p2.ide_param AND p1.ide_lifestyle = p2.ide_lifestyle AND p1.ide_transportmode = p2.ide_transportmode AND p2.canonical = true
     JOIN e_lifestyle ON p1.ide_lifestyle = e_lifestyle.ide_lifestyle
     JOIN e_transportmode ON p1.ide_transportmode = e_transportmode.ide_transportmode
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_use'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_use.name AS entity1,
    NULL::text AS entity2,
    NULL::text AS entity3
   FROM p_use p1
     LEFT JOIN p_use p2 ON p1.ide_param = p2.ide_param AND p1.ide_use = p2.ide_use AND p2.canonical = true
     JOIN e_use ON p1.ide_use = e_use.ide_use
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_use_ecosystem'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_use.name AS entity1,
    e_ecosystem.name AS entity2,
    NULL::text AS entity3
   FROM p_use_ecosystem p1
     LEFT JOIN p_use_ecosystem p2 ON p1.ide_param = p2.ide_param AND p1.ide_ecosystem = p2.ide_ecosystem AND p1.ide_use = p2.ide_use AND p2.canonical = true
     JOIN e_ecosystem ON p1.ide_ecosystem = e_ecosystem.ide_ecosystem
     JOIN e_use ON p1.ide_use = e_use.ide_use
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
UNION
 SELECT DISTINCT 'p_use_lifestyle'::text AS tablename,
    p1.ide_param,
    e_param.name AS param,
    e_use.name AS entity1,
    e_lifestyle.name AS entity2,
    NULL::text AS entity3
   FROM p_use_lifestyle p1
     LEFT JOIN p_use_lifestyle p2 ON p1.ide_param = p2.ide_param AND p1.ide_lifestyle = p2.ide_lifestyle AND p1.ide_use = p2.ide_use AND p2.canonical = true
     JOIN e_lifestyle ON p1.ide_lifestyle = e_lifestyle.ide_lifestyle
     JOIN e_use ON p1.ide_use = e_use.ide_use
     JOIN e_param ON p1.ide_param = e_param.ide_param
  WHERE p2.ide_param IS NULL
  ORDER BY 1, 3, 4, 5, 6;

ALTER TABLE public.noncanonicalvals
    OWNER TO mannahatta;


ALTER TABLE e_species DROP COLUMN name_scientific;
ALTER TABLE e_species DROP COLUMN mw_likelihood;
ALTER TABLE e_species DROP COLUMN description;  -- used in only one species

-- Do some django updating to work with these changes
UPDATE django_content_type SET app_label = 'mannahatta2409' WHERE model LIKE 'species';
SELECT setval('public.django_migrations_id_seq', 24, true);
SELECT setval('public.django_content_type_id_seq', 131, true);
SELECT setval('public.auth_permission_id_seq', 393, true);
DROP TABLE mailchimp_reciever;
DROP TABLE mailchimp_campaign;
DROP TABLE mailchimp_queue;
DELETE FROM django_migrations WHERE app='mannahatta2409';
DELETE FROM django_migrations WHERE app = 'wobsadmin';


-- Remove description from FTS trigger
DROP TRIGGER searchtext_index_update ON e_species;
CREATE TRIGGER searchtext_index_update
  BEFORE INSERT OR UPDATE
  ON e_species
  FOR EACH ROW
  EXECUTE PROCEDURE tsvector_update_trigger('searchtext_index', 'pg_catalog.english', 'name_family', 'name_scientific', 'name_common');

ALTER TABLE welikia_mw_element DROP COLUMN mw_commonname;
ALTER TABLE welikia_mw_element RENAME mw_scientificname TO name;
ALTER TABLE welikia_mw_element DROP COLUMN description_id;
ALTER TABLE welikia_mw_element DROP COLUMN writtendefinition;
DROP TABLE welikia_mw_element_description;

DROP TABLE welikia_mw_habitatstate;

-- welikia_mw_relationship clean up
ALTER TABLE welikia_mw_relationship DROP COLUMN habitatstate_id;
ALTER TABLE welikia_mw_relationship DROP COLUMN relationshiptype_id;

-- add constraints to welikia_mw_relationship
ALTER TABLE welikia_mw_relationship
ADD CONSTRAINT welikia_mw_relationship_mw_state_fkey FOREIGN KEY (state_id)
REFERENCES welikia_mw_state (id) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE welikia_mw_relationship
ADD CONSTRAINT welikia_mw_relationship_mw_group_fkey FOREIGN KEY (group_id)
REFERENCES welikia_mw_group (id) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE welikia_mw_relationship
ADD CONSTRAINT welikia_mw_relationship_mw_interactiontype_fkey FOREIGN KEY (interactiontype_id)
REFERENCES welikia_mw_interactiontype (id) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION;


-- What follows is for the model inheritance approach we've abandoned for the time being.

-- Make e_species and welikia_mw_element inherit from / point to welikia_element.
-- TODO wobsadmin, Visionmaker, Welikia, welikia.net: alter queries to
-- - get common name and description from ancestor
-- - do create/update/delete with reference to joins

-- ALTER TABLE e_species ADD CONSTRAINT
--   e_species_pkey PRIMARY KEY (welikia_element_ptr_id);

-- constraint fk_p_species_e_species1 on table p_species depends on table e_species column ide_species
-- constraint fk_p_species_habitat_e_species1 on table p_species_habitat depends on table e_species column ide_species
-- constraint welikia_block_species_species_id_fkey on table welikia_block_species depends on table e_species column ide_species
-- constraint wobsadmin_record_species_id_fkey on table wobsadmin_record depends on table e_species column ide_species

-- ALTER TABLE e_species DROP COLUMN ide_species;
-- DROP SEQUENCE wobsadmin_species_id_seq;

-- ALTER TABLE e_species ADD CONSTRAINT
--   ide_species_fk_welikia_element_id FOREIGN KEY (welikia_element_ptr_id)
--   REFERENCES welikia_element (id) MATCH SIMPLE
--       ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ALTER TABLE welikia_mw_element ADD CONSTRAINT
--   welikia_mw_element_pkey PRIMARY KEY (welikia_mw_element_ptr_id);
-- ALTER TABLE welikia_mw_element DROP COLUMN id;
-- DROP SEQUENCE welikia_mw_element_id_seq;
--
-- ALTER TABLE welikia_mw_element ADD CONSTRAINT
--   id_fk_welikia_element_id FOREIGN KEY (id)
--   REFERENCES welikia_element (id) MATCH SIMPLE
--       ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
