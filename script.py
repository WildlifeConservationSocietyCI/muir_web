import requests
import pprint as pp
import mw_settings as s
import muirweb as mw


client = requests.session()
headers = mw.api_headers(client)

if headers:
    # aggregation_types = client.get('%smw_aggregation_types/' % s.API, **headers).json()
    # classes = client.get('%smw_classes/' % s.API, **headers).json()
    # definition_types = client.get('%smw_definition_types/' % s.API, **headers).json()
    # frequency_types = client.get('%smw_frequency_types/' % s.API, **headers).json()
    # groups = client.get('%smw_groups/' % s.API, **headers).json()
    # interaction_types = client.get('%smw_interaction_types/' % s.API, **headers).json()
    # probabilities = client.get('%smw_probabilities/' % s.API, **headers).json()
    # relationship_types = client.get('%smw_relationship_types/' % s.API, **headers).json()
    # states = client.get('%smw_states/' % s.API, **headers).json()
    # strength_types = client.get('%smw_strength_types/' % s.API, **headers).json()
    # taxon_types = client.get('%smw_taxon_types/' % s.API, **headers).json()

    mw.relationships = client.get('%smw_relationships/' % s.API, **headers).json()
    mw.elements = {e['elementid']: mw.Element(e) for e in client.get('%smw_elements/' % s.API, **headers).json()}

    pp.pprint(mw.elements[670.00].__dict__)

    # See if ordering mw.elements would decrease the # of required runs
    def map_muirweb(run, initally_mapped):
        print('Starting run %s through elements' % run)
        mapped = list(initally_mapped)
        for elementid in mw.elements:
            if mw.elements[elementid].automap is True and mw.elements[elementid].status is False:
                mw.elements[elementid].show_relationships()
                if mw.calc_grid(elementid):
                    mapped.append(elementid)
        if len(mapped) != initally_mapped:
            print('Mapped: %s' % list(set(mapped) - set(initally_mapped)))
            map_muirweb(run + 1, mapped)
        else:
            print('No additional elements mapped.')

    map_muirweb(1, [])
