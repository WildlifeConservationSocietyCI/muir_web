import requests
import logging
import mw_settings as s
import muirweb as mw
from os.path import join

logfile = join(s.ROOT_DIR, 'muirweb.log')
logging.basicConfig(filename=logfile,
                    filemode='w',
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')
client = requests.session()
headers = mw.api_headers(client)

if headers:
    definition_types = client.get('%smw_definition_types/' % s.API, **headers).json()
    mw.frequency_types = client.get('%smw_frequency_types/' % s.API, **headers).json()
    # states = client.get('%smw_states/' % s.API, **headers).json()
    # groups = client.get('%smw_groups/' % s.API, **headers).json()
    interaction_types = client.get('%smw_interaction_types/' % s.API, **headers).json()
    mw.strength_types = client.get('%smw_strength_types/' % s.API, **headers).json()

    # testing data:
    test_elements = [
        {
            "id": 1934,
            "elementid": "669.10",
            "name": "Uplands",
            "automap": True,
            "native_units": False,
            "subset_rule": "[30.00] > [30.10]",
            "adjacency_rule": None,
            "description": "test of calculating uplands as DEM > HAT (subset)",
            "species": None,
            "mw_definition": 2,
            "mw_taxontype": 3,
            "mw_class": 2,
            "aggregationtype": 2,
            "frequencytype": 6
        },
        {
            "id": 1935,
            "elementid": "30.10",
            "name": "HAT test",
            "automap": False,
            "native_units": True,
            "subset_rule": "",
            "adjacency_rule": None,
            "description": "",
            "species": None,
            "mw_definition": 0,
            "mw_taxontype": 1,
            "mw_class": 10,
            "aggregationtype": 0,
            "frequencytype": 0
        },
        {
            "id": 30,
            "elementid": "30.00",
            "name": "Elevation",
            "automap": False,
            "native_units": False,
            "subset_rule": "",
            "adjacency_rule": None,
            "description": "elevation is a function of topography",
            "species": None,
            "mw_definition": 1,
            "mw_taxontype": 1,
            "mw_class": 1,
            "aggregationtype": 0,
            "frequencytype": 30
        },
        {
            "id": 416,
            "elementid": "665.50",
            "name": "Freshwater wetland communities - test with new soil flow definition",
            "automap": True,
            "native_units": False,
            "subset_rule": "",
            "adjacency_rule": None,
            "description": "wetland * upland",
            "species": None,
            "mw_definition": 1,
            "mw_taxontype": 3,
            "mw_class": 2,
            "aggregationtype": 1,
            "frequencytype": 99
        },
        {
            "id": 423,
            "elementid": "670.00",
            "name": "Wetland communities",
            "automap": True,
            "native_units": False,
            "subset_rule": "",
            "adjacency_rule": None,
            "description": "all the palustrine communities",
            "species": None,
            "mw_definition": 0,
            "mw_taxontype": 3,
            "mw_class": 2,
            "aggregationtype": 1,
            "frequencytype": 99
        },
        {
            "id": 417,
            "elementid": "665.20",
            "name": "Freshwater wetland edges (areas near wetlands, near = 10 m)",
            "automap": True,
            "native_units": False,
            "subset_rule": "",
            "adjacency_rule": 10,
            "description": "10",
            "species": None,
            "mw_definition": 3,
            "mw_taxontype": 0,
            "mw_class": 30,
            "aggregationtype": 6,
            "frequencytype": 99
        },
    ]

    test_relationships = [
        {
            "id": 1,
            "id_subject": "669.10",
            "id_object": "30.00",
            "notes": "",
            "state": 2123,
            "relationshiptype": 3651,
            "strengthtype": 3,
            "interactiontype": 1
        },
        {
            "id": 3,
            "id_subject": "669.10",
            "id_object": "30.10",
            "notes": "",
            "state": 2123,
            "relationshiptype": 3651,
            "strengthtype": 3,
            "interactiontype": 1
        },
        {
            "id": 5211,
            "notes": "",
            "id_subject": '665.50',
            "id_object": '669.10',
            "strengthtype": 3,
            "state": 503,
            "relationshiptype": 885,
            "interactiontype": 1
        },
        {
            "id": 5212,
            "notes": "",
            "id_subject": '665.50',
            "id_object": '670.00',
            "strengthtype": 3,
            "state": 503,
            "relationshiptype": 886,  # causes combination multiplication; may be different from conceptual frame
            "interactiontype": 1
        },
        {
            "id": 5213,
            "notes": "",
            "id_subject": '665.20',
            "id_object": '665.50',
            "strengthtype": 3,
            "state": 504,
            "relationshiptype": 887,
            "interactiontype": 1
        },
    ]

    # mw.relationships = test_relationships
    # mw.elements = {e['elementid']: mw.Element(e) for e in test_elements}
    mw.relationships = client.get('%smw_relationships/' % s.API, **headers).json()
    mw.elements = {e['elementid']: mw.Element(e) for e in client.get('%smw_elements/' % s.API, **headers).json()}

    # TODO: See if ordering mw.elements would decrease the # of required runs
    def map_muirweb(run, initally_mapped):
        logging.info('Starting run %s through elements' % run)
        mapped = list(initally_mapped)
        for elementid in mw.elements:
            if mw.elements[elementid].automap is True and mw.elements[elementid].status is False:
                logging.info('attempting to map %s' % elementid)
                mw.elements[elementid].show_relationships()
                if mw.calc_grid(elementid):
                    mapped.append(elementid)
        if len(mapped) != len(initally_mapped):
            logging.info('Mapped: %s' % list(set(mapped) - set(initally_mapped)))
            map_muirweb(run + 1, mapped)
        else:
            logging.warning('No additional elements mapped.')

    map_muirweb(1, [])
