-- COMPARE e_species likelihood and mw_probability
SELECT es.mw_elementid,
       mwe.elementid,
       es.name_scientific,
       es.name_common,
       l.name AS e_likelihood,
       mwp.name AS mw_probability
       FROM e_species AS es
            INNER JOIN e_likelihood AS l 
                    ON (es.historical_likelihood = l.id)
            FULL OUTER JOIN welikia_mw_element AS mwe 
                         ON (es.mw_elementid = mwe.elementid)
            FULL OUTER JOIN welikia_mw_probability as mwp
		         ON (mwe.probability = mwp.id);