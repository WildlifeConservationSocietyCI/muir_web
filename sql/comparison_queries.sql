-- COMPARE e_species likelihood and mw_probability
SELECT es.mw_elementid,
       mwe.elementid,
       es.name_scientific,
       es.name_common,
       es.mw_likelihood,
       l.name AS e_likelihood,
       mwp.name AS mw_probability
       FROM e_species AS es
            INNER JOIN e_likelihood AS l 
                    ON (es.historical_likelihood = l.id)
            FULL OUTER JOIN welikia_mw_element AS mwe 
                         ON (es.mw_elementid = mwe.elementid)
            FULL OUTER JOIN welikia_mw_probability as mwp
		         ON (mwe.probability = mwp.id);

-- This yielded only 3 discrepancies between mw_taxontypes, and the mw_element version was better in all cases
SELECT ide_species, name_common, mw_commonname, s.mw_taxontype, e.mw_taxontype
FROM e_species s
INNER JOIN welikia_mw_element e ON (s.mw_elementid = e.elementid)
WHERE s.mw_taxontype != e.mw_taxontype
ORDER BY ide_species;

-- Only 8/20 references in Access are actually used; this seems inconsistent and/or incomplete.
SELECT DISTINCT(reference_id), COUNT(id)
  FROM welikia_mw_element_description
  GROUP BY reference_id
  ORDER BY reference_id;
-- TODO: go through all records in welikia_mw_element and properly attribute a record in wobsadmin_reference,
-- entering things like old spreadsheets as sources in zotero when necessary

-- To compare writtendefinition and description
SELECT e.id, mw_definition, e.writtendefinition, e.notes, description, reference_id
FROM welikia_mw_element e
LEFT JOIN welikia_mw_element_description ed ON (e.description_id = ed.id)
WHERE
writtendefinition != '' AND
writtendefinition != description
ORDER BY mw_definition;

-- compare elementids
SELECT ide_species, name_scientific, name_common, s.mw_elementid, e.elementid
FROM e_species s
FULL JOIN welikia_mw_element e ON (s.mw_elementid = e.elementid)
--ORDER BY s.mw_elementid;
ORDER BY e.elementid, s.mw_elementid;

-- Where did values for s.mw_elementid < 10000 that don't match MW elements come from? Should they match MW elements?
-- Can we set s.mw_elementid = NULL for vals > 100000? These were temporary ids.
-- Regardless, the species lists task will involve going through all the species that aren't yet MW elements.

-- the effort to consolidate mw element names, and put taxonomic info into species
SELECT id, elementid, mw_scientificname, mw_commonname--, name_scientific, name_common
FROM welikia_mw_element
--LEFT JOIN e_species ON (welikia_mw_element.elementid = e_species.mw_elementid)
WHERE lower(mw_scientificname) != lower(mw_commonname)
--AND lower(mw_scientificname) != lower(name_scientific)
ORDER BY elementid;

-- find all foreign keys that reference a particular table, in this case wobsadmin_taxon
-- Note: wobsadmin_taxon is being removed as part of the VM species branch
SELECT conname,
  pg_catalog.pg_get_constraintdef(r.oid, true) as condef
FROM pg_catalog.pg_constraint r
WHERE r.confrelid = 'public.wobsadmin_taxon'::regclass
AND r.contype = 'f';

