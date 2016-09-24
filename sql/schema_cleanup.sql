-- Keep unique constraint: elementid must exist in e_species AND be unique within welikia_mw_element
ALTER TABLE e_species DROP CONSTRAINT wobsadmin_species_mw_elementid_key;
ALTER TABLE e_species DROP COLUMN mw_elementid;
ALTER TABLE welikia_mw_element ADD CONSTRAINT welikia_mw_element_e_species_fkey FOREIGN KEY (species_id)
  REFERENCES e_species (ide_species) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE welikia_mw_element ADD CONSTRAINT welikia_mw_element_species_id_key UNIQUE (species_id);
-- ALTER TABLE e_species ADD CONSTRAINT e_species_elementid_key UNIQUE (welikia_mw_element_id);
-- ALTER TABLE e_species ADD CONSTRAINT e_species_mw_elementid_fk_welikia_mw_element_elementid
--   FOREIGN KEY (welikia_mw_element_id) REFERENCES welikia_mw_element (elementid) ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE e_species
  ADD CONSTRAINT e_species_historical_likelihood_fkey FOREIGN KEY (historical_likelihood)
  REFERENCES e_likelihood (id) MATCH SIMPLE;

ALTER TABLE e_species DROP COLUMN name_scientific;
ALTER TABLE e_species DROP COLUMN mw_likelihood;
ALTER TABLE e_species DROP COLUMN description;
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
