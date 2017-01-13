import os
import arcpy

arcpy.env.overwriteOutput = True

ROOT_DIR = r'F:\_data\Welikia\muir_web\element_grids'
LOG_DIR = ''

DEBUG_MODE = ''

MW_DB = r'F:\_data\Welikia\muir_web\test\muir_web_database_test.json'

ELEMENTS = {}

CELL_SIZE = 5