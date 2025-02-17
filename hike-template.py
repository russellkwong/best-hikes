#!/usr/bin/env python

"""hike-template.py: Creates maps for Best Hikes Around Ithaca Book."""

# SETUP

import os
import arcpy as ap

aprx = ap.mp.ArcGISProject("CURRENT")

# FUNCTIONS

def map_obj(map_name):
    """
    Identifies Map Object by provided name and returns result.

    Parameters:
    map_name (str): The name of a map.

    Returns:
    Map object
    """
    return aprx.listMaps(map_name)[0]

def lyr_obj(map_obj, lyr_name):
    """
    Identifies Layer Object by provided name and returns result.

    Parameters:
    map_obj (Map object): A map in the project.
    lyr_name (str): The name of a layer.

    Returns:
    Layer object
    """
    return map_obj.listLayers(lyr_name)[0]

def lyt_obj(lyt_name):
    """
    Identifies Layout Object by provided name and returns result.

    Parameters:
    lyt_name (str): The name of the layout.

    Returns:
    Layout object
    """
    return aprx.listLayouts(lyt_name)[0]

def lyr_rename(lyr, newName):
    """
    Renames Layer Object in the table of contents.
    
    Parameters:
    lyr (layer object): The layer to be renamed.
    newName (str): The new name of the layer.
    
    Returns:
    None
    """
    oldName = str(lyr.name)
    lyr.name = lyr.name.replace(lyr.name, newName)
    print(f'Layer \'{oldName}\' renamed to: \'{lyr.name}\'')
    pass

def MakeRec_LL(llx, lly, w, h):
    """
    Creates a rectangle Polygon defined by the lower-left corner, width, and height.

    Parameters:
    llx (float): x-coordinate of lower left corner.
    lly (float): y-coordinate of lower left corner.
    w (float): width of rectangle.
    h (float): height of rectangle.

    Returns:
    rec (Polygon): Rectangle object with defined dimensions.
    """
    xyRecList = [[llx, lly], [llx, lly+h], [llx+w, lly+h], [llx+w, lly], [llx, lly]]
    array = ap.Array([ap.Point(*coords) for coords in xyRecList])
    rec = ap.Polygon(array)
    return rec

# PROJECT CODE
m = map_obj('Map')
# lyt = aprx.createLayout(6, 9, 'INCH', 'Layout')
# mf = lyt.createMapFrame(MakeRec_LL(0.25, 5.0, 5.5, 3.75), m, 'Map 1')

## Adding GPX files
aprx_dir = r'C:\Users\AAP_LAB\Desktop\best-hikes\SpatialFiles'
aprx_gdb = r'C:\Users\AAP_LAB\Desktop\best-hikes\MyProject.gdb'

# TRACKS
ap.conversion.GPXtoFeatures(
    Input_GPX_File = os.path.join(aprx_dir, 'best-hikes-all-routes-22Jan25.gpx'),
    Output_Feature_class = os.path.join(aprx_gdb, 'hike_routes_points'),
    Output_Type = 'POINTS'
)

lyr = ap.management.PointsToLine(
    Input_Features = 'hike_routes_points',
    Output_Feature_Class = os.path.join(aprx_gdb, 'hike_routes_tracks'),
    Line_Field = "Name",
    Sort_Field = None,
    Close_Line = "NO_CLOSE",
    Line_Construction_Method = "CONTINUOUS",
    Attribute_Source = "NONE",
    Transfer_Fields = None
)

lyr = lyr_obj(m, 'hike_routes_tracks')

sym = lyr.symbology

sym.renderer.symbol.outlineWidth = 2.5
sym.renderer.symbol.outlineColor = {'RGB': [0, 0, 0, 100]}
lyr.symbology = sym

# LAND COVER
m.addDataFromPath(os.path.join(aprx_dir, r'NLCD_LndCov_2023\Annual_NLCD_LndCov_2023_CU_C1V0_sAzmI4M2YwCTSt5k8oPt.tiff'))
ap.conversion.RasterToPolygon(
    in_raster="Annual_NLCD_LndCov_2023_CU_C1V0_sAzmI4M2YwCTSt5k8oPt.tiff",
    out_polygon_features= os.path.join(aprx_gdb, r'RasterT_Annual_1'),
    simplify="NO_SIMPLIFY",
    raster_field="Value",
    create_multipart_features="MULTIPLE_OUTER_PART",
    max_vertices_per_feature=None
)

lyr = lyr_obj(m, 'RasterT_Annual_1')
lyr_rename(lyr, 'landcov')
sym = lyr.symbology

sym.updateRenderer('UniqueValueRenderer')
sym.renderer.fields = ['gridcode']
for grp in sym.renderer.groups:
    for itm in grp.items:
        if itm.values[0][0] in ['71', '81']:
            itm.symbol.applySymbolFromGallery('10% Ordered Stipple')        
#         elif itm.values[0][0] in ['11', '90', '95']:
#             itm.symbol.applySymbolFromGallery('10% Simple Hatch')
        else:
            itm.symbol.color = {'RGB': [255, 255, 255, 0]}
        itm.symbol.outlineWidth = 0
lyr.symbology = sym

# CONTOURS
lyr = m.addDataFromPath(os.path.join(aprx_dir, r'TompCty_Contours\Tompkins_County_Natural_Resources_Inventory_(OLD).shp'))
lyr_rename(lyr, 'Contours')
contour_symbols = {'1': {'color': {'RGB': [64, 64, 64, 100]},
                        'outlineWidth': 1},
                  '0': {'color': {'RGB': [80, 80, 80, 100]},
                       'outlineWidth': 0.3}}

sym = lyr.symbology

ap.management.CalculateField(
    in_table="Contours",
    field="major",
    expression="!CONTOUR! % 200 == 0",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

sym.updateRenderer('UniqueValueRenderer')
sym.renderer.fields = ["major"]
for grp in sym.renderer.groups:
    for itm in grp.items:
        itm.symbol.color = contour_symbols[itm.values[0][0]]['color']
        itm.symbol.outlineWidth = contour_symbols[itm.values[0][0]]['outlineWidth']
lyr.symbology = sym

# HYDRO
lyr = m.addDataFromPath(r'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Hydrography/MapServer/9',
                 web_service_type = 'ARCGIS_SERVER_WEB',
                 custom_parameters = {})
lyr_rename(lyr, 'hydro')

sym = lyr.symbology

sym.renderer.symbol.applySymbolFromGallery('Water Intermittent')
sym.renderer.symbol.outlineWidth = 0

lyr.symbology = sym

# ROADS
lyr = m.addDataFromPath(r'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Streets/MapServer/7',
                 web_service_type = 'ARCGIS_SERVER_WEB',
                 custom_parameters = {})
lyr_rename(lyr, 'roads')

sym = lyr.symbology 
sym.updateRenderer('SimpleRenderer')

sym.renderer.symbol.applySymbolFromGallery('Minor Road')
lyr.symbology = sym

# POI

ap.management.XYTableToPoint(
    in_table = os.path.join(aprx_dir, r'POI_hikes_18Jan25.csv'),
    out_feature_class = os.path.join(aprx_gdb, r'POI_hikes'),
    x_field="longitude",
    y_field="latitude",
    z_field=None,
    coordinate_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
)

poi_symbols = {'Bus stop': 'Bus',
              'Geology': 'Mountain', 
              'Historic': 'Museum',
              'Lean-to': 'Military Base',
              'Parking': 'Parking',
              'Trailhead': 'Trail',
              'Viewpoint': 'Landmark',
              'Waterfall': 'Cemetery'}

lyr = lyr_obj(m, 'POI_hikes')
sym = lyr.symbology

sym.updateRenderer('UniqueValueRenderer')
sym.renderer.fields = ['type']
for grp in sym.renderer.groups:
    for itm in grp.items:
        symb_list = itm.symbol.listSymbolsFromGallery(poi_symbols[itm.values[0][0]])
        for symb in symb_list:
            if symb.size == 20:
                itm.symbol = symb
        itm.symbol.color = {'RGB': [32, 32, 32, 100]}
        itm.symbol.size = 12
lyr.symbology = sym


# LAYOUT
lyt = aprx.createLayout(6, 9, 'INCH', 'Layout')
mf = lyt.createMapFrame(MakeRec_LL(0.50, 0.50, 5.0, 3.75), m, 'Map 1')

sbName = 'Double Alternating Scale Bar 1 Metric'
sbStyItm = aprx.listStyleItems('ArcGIS 2D', 'SCALE_BAR', sbName)[0]
sbEnv = MakeRec_LL(0.5, 5.5, 2.5, 0.5)
sb = lyt.createMapSurroundElement(sbEnv, 'Scale_bar', mf, sbStyItm)

recTxt = aprx.createTextElement(lyt, MakeRec_LL(0.5, 4.5, 5.0, 3.5), 'POLYGON',
                             'Sample Text', 10, 'Arial', 'Regular', name='SampleText')

# m.addDataFromPath(r'https://elevation.its.ny.gov/arcgis/rest/services/NYS_Statewide_Hillshade/MapServer/3',
#                  web_service_type = 'ARCGIS_SERVER_WEB',
#                  custom_parameters = {})
