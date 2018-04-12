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
        }
        # {
        #     "id": 300,
        #     "elementid": '225.00',
        #     "name": "Test combo element",
        #     "subset_rule": None,
        #     "adjacency_rule": None,
        #     "description": "",
        #     "access_description_reference_id": 0,
        #     "access_reference_id": 0,
        #     "access_elementclass": 0,
        #     "automap": True,
        #     "mw_definition": 1,
        #     "mw_class": 2,
        #     "mw_taxontype": 0,
        #     "species": None,
        #     "probability": 0,
        #     "aggregationtype": 0,
        #     "frequencytype": 99
        # },
        # {
        #     "id": 301,
        #     "elementid": '100.0',
        #     "name": "Test combo dependency element",
        #     "subset_rule": None,
        #     "adjacency_rule": None,
        #     "description": "",
        #     "access_description_reference_id": 0,
        #     "access_reference_id": 0,
        #     "access_elementclass": 0,
        #     "automap": True,
        #     "mw_definition": 1,
        #     "mw_class": 2,
        #     "mw_taxontype": 0,
        #     "species": None,
        #     "probability": 0,
        #     "aggregationtype": 0,
        #     "frequencytype": 99
        # },
        # {
        #     "id": 302,
        #     "elementid": '101.10',
        #     "name": "Test combo dependency element 2",
        #     "subset_rule": None,
        #     "adjacency_rule": None,
        #     "description": "",
        #     "access_description_reference_id": 0,
        #     "access_reference_id": 0,
        #     "access_elementclass": 0,
        #     "automap": True,
        #     "mw_definition": 1,
        #     "mw_class": 2,
        #     "mw_taxontype": 0,
        #     "species": None,
        #     "probability": 0,
        #     "aggregationtype": 0,
        #     "frequencytype": 99
        # },
        # {
        #     "id": 303,
        #     "elementid": '101.20',
        #     "name": "Test combo dependency element 3",
        #     "subset_rule": None,
        #     "adjacency_rule": None,
        #     "description": "",
        #     "access_description_reference_id": 0,
        #     "access_reference_id": 0,
        #     "access_elementclass": 0,
        #     "automap": True,
        #     "mw_definition": 1,
        #     "mw_class": 2,
        #     "mw_taxontype": 0,
        #     "species": None,
        #     "probability": 0,
        #     "aggregationtype": 0,
        #     "frequencytype": 99
        # },
        # {
        #     "id": 231,
        #     "elementid": "122.10",
        #     "name": "Near rocky crevice (near = 1000 m)",
        #     "subset_rule": None,
        #     "adjacency_rule": 400,
        #     "description": "400",
        #     "access_description_reference_id": 0,
        #     "access_reference_id": 0,
        #     "access_elementclass": 8,
        #     "automap": True,
        #     "mw_definition": 3,
        #     "mw_class": 30,
        #     "mw_taxontype": 1,
        #     "species": None,
        #     "probability": 0,
        #     "aggregationtype": 6,
        #     "frequencytype": 99
        # },
        # {
        #     "id": 230,
        #     "elementid": "122.00",
        #     "name": "Rocky crevice",
        #     "subset_rule": None,
        #     "adjacency_rule": None,
        #     "description": "rock crevices will be found where the ground is rocky and the rocks are large",
        #     "access_description_reference_id": 0,
        #     "access_reference_id": 0,
        #     "access_elementclass": 0,
        #     "automap": True,
        #     "mw_definition": 1,
        #     "mw_class": 1,  #
        #     "mw_taxontype": 1,
        #     "species": None,
        #     "probability": 0,  #
        #     "aggregationtype": 0,  #
        #     "frequencytype": 99
        # },
        # {
        #     "id": 32,
        #     "elementid": "31.10",
        #     "name": "Gently sloping slopes",
        #     "subset_rule": "logical_and([31.00] >= 2, [31.00] <= 5)",
        #     # "subset_rule": "con([Grid] >= 2 and [Grid] <= 5,MaxProb,0)",
        #     "adjacency_rule": None,
        #     "description": "gently sloping",
        #     "access_description_reference_id": 0,
        #     "access_reference_id": 0,
        #     "access_elementclass": 7,
        #     "automap": True,
        #     "mw_definition": 2,
        #     "mw_class": 1,
        #     "mw_taxontype": 1,
        #     "species": None,
        #     "probability": 0,
        #     "aggregationtype": 2,
        #     "frequencytype": 30
        # },
        # {
        #     "id": 31,
        #     "elementid": "31.00",
        #     "name": "Slope (Flux in elevation)",
        #     "subset_rule": None,
        #     "adjacency_rule": None,
        #     "description": "slope is a function of elevation (literally the change in elevation)",
        #     "access_description_reference_id": 0,
        #     "access_reference_id": 0,
        #     "access_elementclass": 6,
        #     "automap": False,
        #     "mw_definition": 1,
        #     "mw_class": 1,
        #     "mw_taxontype": 1,
        #     "species": None,
        #     "probability": 0,
        #     "aggregationtype": 0,
        #     "frequencytype": 30
        # },
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
            "strengthtype": 0,
            "interactiontype": 1
        },
        # {
        #     "id": 5211,
        #     "notes": "",
        #     "id_subject": '225.00',
        #     "id_object": '100.0',
        #     "strengthtype": 3,
        #     "state": 503,
        #     "group": 885,
        #     "interactiontype": 1
        # },
        # {
        #     "id": 5212,
        #     "notes": "",
        #     "id_subject": '225.00',
        #     "id_object": '101.10',
        #     "strengthtype": 2,
        #     "state": 503,
        #     "group": 886,
        #     "interactiontype": 2
        # },
        # {
        #     "id": 5213,
        #     "notes": "",
        #     "id_subject": '225.00',
        #     "id_object": '101.20',
        #     "strengthtype": 1,
        #     "state": 504,
        #     "group": 887,
        #     "interactiontype": 3
        # },
        # {
        #     "id": 9279,
        #     "id_subject": "122.10",
        #     "id_object": "122.00",
        #     "notes": "",
        #     "strengthtype": 3,
        #     "state": 2050,
        #     "group": 3574,
        #     "interactiontype": 1
        # },
        # {
        #     "id": 9091,
        #     "id_subject": '31.10',
        #     "id_object": '31.00',
        #     "notes": "",
        #     "strengthtype": 3,
        #     "state": 2051,
        #     "group": 3575,
        #     "interactiontype": 1,
        # },
    ]

    mw.relationships = test_relationships
    mw.elements = {e['elementid']: mw.Element(e) for e in test_elements}
    # mw.relationships = client.get('%smw_relationships/' % s.API, **headers).json()
    # mw.elements = {e['elementid']: mw.Element(e) for e in client.get('%smw_elements/' % s.API, **headers).json()}

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
