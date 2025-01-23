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
# lyt = aprx.createLayout(6, 9, 'INCH', 'Layout')
# mf = lyt.createMapFrame(MakeRec_LL(0.25, 5.0, 5.5, 3.75), m, 'Map 1')

## Adding GPX files
# aprx_dir = r'C:\Users\lib-pac-rsch\Desktop\best-hikes\SpatialFiles'
# aprx_gdb = r'C:\Users\lib-pac-rsch\Desktop\best-hikes\MyProject.gdb'

# arcpy.conversion.GPXtoFeatures(
#     Input_GPX_File = os.path.join(aprx_dir, 'best-hikes-all-routes-22Jan25.gpx'),
#     Output_Feature_class = os.path.join(aprx_gdb, 'hike_routes_points'),
#     Output_Type = 'POINTS'
# )

# arcpy.management.PointsToLine(
#     Input_Features = 'hike_routes_points',
#     Output_Feature_Class = os.path.join(aprx_gdb, 'hike_routes_tracks'),
#     Line_Field = "Name",
#     Sort_Field = None,
#     Close_Line = "NO_CLOSE",
#     Line_Construction_Method = "CONTINUOUS",
#     Attribute_Source = "NONE",
#     Transfer_Fields = None
# )
