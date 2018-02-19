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
    mw.frequency_types = client.get('%smw_frequency_types/' % s.API, **headers).json()
    # groups = client.get('%smw_groups/' % s.API, **headers).json()
    # interaction_types = client.get('%smw_interaction_types/' % s.API, **headers).json()
    # probabilities = client.get('%smw_probabilities/' % s.API, **headers).json()
    # relationship_types = client.get('%smw_relationship_types/' % s.API, **headers).json()
    # states = client.get('%smw_states/' % s.API, **headers).json()
    # strength_types = client.get('%smw_strength_types/' % s.API, **headers).json()
    # taxon_types = client.get('%smw_taxon_types/' % s.API, **headers).json()

    # testing data:
    test_elements = [
        {
            "id": 300,
            "elementid": '225.00',
            "name": "Test combo element",
            "subset_rule": None,
            "adjacency_rule": None,
            "description": "",
            "access_description_reference_id": 0,
            "access_reference_id": 0,
            "elementclass": 0,
            "automap": True,
            "mw_definition": 1,
            "mw_class": 2,
            "mw_taxontype": 0,
            "species": None,
            "probability": 0,
            "aggregationtype": 0,
            "frequencytype": 99
        },
        {
            "id": 301,
            "elementid": '100.0',
            "name": "Test combo dependency element",
            "subset_rule": None,
            "adjacency_rule": None,
            "description": "",
            "access_description_reference_id": 0,
            "access_reference_id": 0,
            "elementclass": 0,
            "automap": True,
            "mw_definition": 1,
            "mw_class": 2,
            "mw_taxontype": 0,
            "species": None,
            "probability": 0,
            "aggregationtype": 0,
            "frequencytype": 99
        },
        {
            "id": 302,
            "elementid": '101.10',
            "name": "Test combo dependency element 2",
            "subset_rule": None,
            "adjacency_rule": None,
            "description": "",
            "access_description_reference_id": 0,
            "access_reference_id": 0,
            "elementclass": 0,
            "automap": True,
            "mw_definition": 1,
            "mw_class": 2,
            "mw_taxontype": 0,
            "species": None,
            "probability": 0,
            "aggregationtype": 0,
            "frequencytype": 99
        },
        {
            "id": 303,
            "elementid": '101.20',
            "name": "Test combo dependency element 3",
            "subset_rule": None,
            "adjacency_rule": None,
            "description": "",
            "access_description_reference_id": 0,
            "access_reference_id": 0,
            "elementclass": 0,
            "automap": True,
            "mw_definition": 1,
            "mw_class": 2,
            "mw_taxontype": 0,
            "species": None,
            "probability": 0,
            "aggregationtype": 0,
            "frequencytype": 99
        },
        {
            "id": 231,
            "elementid": "122.10",
            "name": "Near rocky crevice (near = 1000 m)",
            "subset_rule": None,
            "adjacency_rule": 400,
            "description": "400",
            "access_description_reference_id": 0,
            "access_reference_id": 0,
            "elementclass": 8,
            "automap": True,
            "mw_definition": 3,
            "mw_class": 30,
            "mw_taxontype": 1,
            "species": None,
            "probability": 0,
            "aggregationtype": 6,
            "frequencytype": 99
        },
        {
            "id": 230,
            "elementid": "122.00",
            "name": "Rocky crevice",
            "subset_rule": None,
            "adjacency_rule": None,
            "description": "rock crevices will be found where the ground is rocky and the rocks are large",
            "access_description_reference_id": 0,
            "access_reference_id": 0,
            "elementclass": 0,
            "automap": True,
            "mw_definition": 1,
            "mw_class": 1,  #
            "mw_taxontype": 1,
            "species": None,
            "probability": 0,  #
            "aggregationtype": 0,  #
            "frequencytype": 99
        },
    ]

    test_relationships = [
        {
            "id": 5211,
            "notes": "",
            "id_subject": '225.00',
            "id_object": '100.0',
            "strengthtype": 1,
            "state": 503,
            "group": 885,
            "interactiontype": 1
        },
        {
            "id": 5212,
            "notes": "",
            "id_subject": '225.00',
            "id_object": '101.10',
            "strengthtype": 1,
            "state": 503,
            "group": 886,
            "interactiontype": 1
        },
        {
            "id": 5213,
            "notes": "",
            "id_subject": '225.00',
            "id_object": '101.20',
            "strengthtype": 1,
            "state": 504,
            "group": 887,
            "interactiontype": 1
        },
        {
            "id": 9279,
            "id_subject": "122.10",
            "id_object": "122.00",
            "notes": "",
            "strengthtype": 3,
            "state": 2050,
            "group": 3574,
            "interactiontype": 1
        },
    ]

    mw.relationships = test_relationships
    mw.elements = {e['elementid']: mw.Element(e) for e in test_elements}

    # mw.relationships = client.get('%smw_relationships/' % s.API, **headers).json()
    # mw.elements = {e['elementid']: mw.Element(e) for e in client.get('%smw_elements/' % s.API, **headers).json()}

    # TODO: See if ordering mw.elements would decrease the # of required runs
    def map_muirweb(run, initally_mapped):
        print('Starting run %s through elements' % run)
        mapped = list(initally_mapped)
        for elementid in mw.elements:
            if mw.elements[elementid].automap is True and mw.elements[elementid].status is False:
                print('attempting to map %s' % elementid)
                mw.elements[elementid].show_relationships()
                if mw.calc_grid(elementid):
                    mapped.append(elementid)
        if len(mapped) != len(initally_mapped):
            print('Mapped: %s' % list(set(mapped) - set(initally_mapped)))
            map_muirweb(run + 1, mapped)
        else:
            print('No additional elements mapped.')

    map_muirweb(1, [])
