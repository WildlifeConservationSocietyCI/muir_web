import requests
import logging
import time
from os.path import join
from collections import OrderedDict
import mw_settings as s
import muirweb as mw

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
            "id": 30,
            "elementid": "30.00",
            "name": "Elevation",
            "spatially_explicit": True,
            "mapped_manually": True,
            "native_units": True,
            "subset_rule": "",
            "adjacency_rule": None,
            "description": "elevation is a function of topography",
            "last_modified": "2018-07-08T23:17:56.597733-04:00",
            "species": None,
            "mw_definition": 1,
            "mw_taxontype": 1,
            "mw_class": 1,
            "aggregationtype": 0,
            "frequencytype": 30,
            "references": []
        },
        {
            "id": 108,
            "elementid": "70.30",
            "name": "Mean tide to mean high water",
            "spatially_explicit": True,
            "mapped_manually": False,
            "native_units": False,
            "subset_rule": "logical_and([30.00] > -1, [30.00] < 5)",
            "adjacency_rule": None,
            "description": "Mean tide to mean high water",
            "last_modified": None,
            "species": None,
            "mw_definition": 2,
            "mw_taxontype": 1,
            "mw_class": 1,
            "aggregationtype": 2,
            "frequencytype": 31,
            "references": []
        }
    ]

    test_relationships = [
        {
            "id": 9139,
            "id_subject": "70.30",
            "id_object": "30.00",
            "notes": "",
            "state": 14,
            "relationshiptype": 22,
            "strengthtype": 3,
            "interactiontype": 1
        }
    ]

    # mw.relationships = test_relationships
    # mw.elements = {e['elementid']: mw.Element(e) for e in test_elements}

    raw_elements = client.get('%smw_elements/' % s.API, **headers).json()
    sorted_elements = sorted(raw_elements, key=lambda k: float(k['elementid']))
    mw.elements = OrderedDict([(e['elementid'], mw.Element(e)) for e in sorted_elements])
    mw.relationships = client.get('%smw_relationships/' % s.API, **headers).json()


    def map_muirweb(run, initally_mapped):
        logging.info('Starting run %s through elements' % run)
        mapped = list(initally_mapped)
        for elementid in mw.elements:
            if (mw.elements[elementid].spatially_explicit is True and
                    mw.elements[elementid].mapped_manually is False and
                    mw.elements[elementid].status is False):
                if mw.calc_grid(elementid):
                    logging.info('mapped %s' % elementid)
                    mapped.append(elementid)
        if len(mapped) != len(initally_mapped):
            logging.info('Mapped: %s' % list(set(mapped) - set(initally_mapped)))
            map_muirweb(run + 1, mapped)
        else:
            logging.warning('No additional elements mapped.')
            elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
            logging.info('Execution time: {}'.format(elapsed))

    start_time = time.time()
    # Uncomment to clear out everything not mapped by hand before beginning runs
    # mw.clear_automapped()
    map_muirweb(1, [])
