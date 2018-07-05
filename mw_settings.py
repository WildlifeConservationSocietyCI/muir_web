ROOT_DIR = r'D:\_data\Welikia\muirweb'
# ROOT_DIR = r'\\walrus\GIS1\Cities_and_Conservation_data\Welikia\MuirWeb'
GRID_DIR = r'%s\grids' % ROOT_DIR
API = 'https://visionmaker.us/api/v2/'
CELL_SIZE = 5
LOG_DIR = ''
RASTER_DRIVER = 'GTiff'
# NODATA_INT16 = -32768
# NODATA_FLOAT32 = -3.40282346639e+038
# NODATA_FLOAT32 = -3.4028235e+38
# NODATA_FLOAT32 = -3.40282306074e+038

STOP = 0
COMBINATION = 1
SUBSET = 2
ADJACENCY = 3

REQUIRED = 1
ENHANCING = 2
ATTENUATING = 3

params = {'format': 'json'}
# http_auth = ('mannahattadev', 'mannahattadev')
