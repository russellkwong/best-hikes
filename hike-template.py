#!/usr/bin/env python

"""hike-template.py: Creates maps for Best Hikes Around Ithaca Book."""

# SETUP

import os
import arcpy as ap

# set ArcGIS project to current project
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

def lyr_remove(m, lyr):
    """
    Attemptes to remove a layer from the Map.

    Parameters:
    m (map object): The map containing the layer.
    lyr (layer object): The layer to be removed.

    Returns:
    None
    """
    try:
        lyrname = lyr.name
        m.removeLayer(lyr)
        print(f'Layer \'{lyrname}\' removed')
    except:
        print('Layer not found')
    pass

color_dict = {'grey10': [25, 25, 25],
              'grey20': [51, 51, 51],
              'grey30': [76, 76, 76],
              'grey40': [102, 102, 102],
              'grey50': [127, 127, 127],
              'grey60': [153, 153, 153],
              'grey70': [178, 178, 178],
              'grey80': [204, 204, 204],
              'grey90': [229, 229, 229],
              'grey100': [255, 255, 255]
             }

trails_dict = {'jms': {'trail_name': 'Dryden Rail Trail - Jim Schug Trail',
                       'topo_ext': '-76.2930 42.4435 -76.2500 42.4740 ',
                       'mf_camx': -76.2716982,
                       'mf_camy': 42.4584028,
                       'mf_camScale': 35000,
                       'roads': 'roads8'},
               'lp': {'trail_name': 'Lindsay-Parsons Preserve',
                      'topo_ext': '-76.5307 42.3005 -76.4988 42.3259 ',
                      'mf_camx': -76.5155907,
                      'mf_camy': 42.3139858,
                      'mf_camScale': 14870,
                      'roads': 'roads7'}}


def color_builder(color, alpha):
    """
    Creates a dictionary for the defined color and transparency.

    Parameters:
    color (str): Name of color in the color dictionary.
    alpha (float): Transparency value.

    Returns:
    Dictionary of the RGBa color.
    """
    color_exp = []
    color_exp = color_dict[color]
    color_exp.append(alpha)
    return {'RGB': color_exp}

# PROJECT CODE
m = map_obj('Map')

## Setting Directories
aprx_dir = r'C:\Users\kwong\Desktop\best-hikes\SpatialFiles'
aprx_gdb = r'C:\Users\kwong\Desktop\best-hikes\MyProject.gdb'

# Turn off basemap
lyr = lyr_obj(m, 'Topographic')
lyr.visible = False

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

sym.renderer.symbol.outlineWidth = 3.4
sym.renderer.symbol.outlineColor = {'RGB': [52, 52, 52, 60]}
lyr.symbology = sym

def gen_flltPreserve():
    """
    Generates layer of FLLT Preserve boundary as polygon.

    Returns: 
    None
    """
    lyr = ap.conversion.JSONToFeatures(
        in_json_file=os.path.join(aprx_dir, r'fllt-preserve-boundaries.geojson'),
        out_features=os.path.join(aprx_gdb, r'flltPreserve'),
        geometry_type="POLYGON"
    )
    lyr = lyr_obj(m, 'flltPreserve')
    
    sym = lyr.symbology
    sym.updateRenderer('SimpleRenderer')
    
    sym.renderer.symbol.applySymbolFromGallery('Extent Transparent Gray')
    # sym.renderer.symbol.outlineWidth = 1.5
    # sym.renderer.symbol.outlineColor = {'RGB': [100, 100, 100, 60]}
    lyr.symbology = sym
    pass

def gen_flltTrails():
    """
    Generates layer of FLLT Trails as polyline.

    Returns:
    None
    """
    lyr = ap.conversion.JSONToFeatures(
        in_json_file=os.path.join(aprx_dir, r'fllt-trails.geojson'),
        out_features=os.path.join(aprx_gdb, r'flltTrails'),
        geometry_type="POLYLINE"
    )
    lyr = lyr_obj(m, 'flltTrails')
    
    sym = lyr.symbology
    sym.updateRenderer('SimpleRenderer')
    
    sym.renderer.symbol.applySymbolFromGallery('Dashed 2:2')
    sym.renderer.symbol.outlineWidth = 0.7
    lyr.symbology = sym
    pass

roads_svc = {'roads4': '4',
                     'roads5': '5',
                     'roads6': '6',
                     'roads7': '7',
                     'roads8': '8',
                     'roads9': '9',
                     'roads10': '10'}

def gen_roads(scale):
    """
    Generates layer of NYS roads as polyline.

    Returns:
    None
    """
    svcpath = r'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Streets/MapServer/'
    
    lyr = m.addDataFromPath(''.join((svcpath, scale)),
                     web_service_type = 'ARCGIS_SERVER_WEB',
                     custom_parameters = {})
    lyr_rename(lyr, 'roads')
    
    lyr = lyr_obj(m, 'roads')
    sym = lyr.symbology 
    sym.updateRenderer('SimpleRenderer')
    
    symb = sym.renderer.symbol.listSymbolsFromGallery('Minor Road')[1]
    sym.renderer.symbol = symb
    lyr.symbology = sym

    gen_roadsLabels(lyr, True)
    pass

def gen_roadsLabels(lyr, labels=True):
    """
    Generates labels for roads.

    Parameters:
    lyr (Layer object): Roads layer to add labels.

    Returns:
    None
    """
    if lyr.supports('SHOWLABELS'):
        lblClass = lyr.listLabelClasses()[3]
        lbl_cim = lblClass.getDefinition('V3')
        lbl_cim.textSymbol.symbol.fontFamilyName = 'Times New Roman'
        lbl_cim.textSymbol.symbol.height = 7
        lbl_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
        lblClass.setDefinition(lbl_cim)
        lyr.showLabels = labels

    for lblClass in lyr.listLabelClasses():
        if lblClass.name == 'Label Class 3':
            hwynum_cim = lblClass.getDefinition('V3')
            hwynum_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
            hwynum_cim.textSymbol.symbol.callout = 'PointSymbol'
            hwynum_cim.visibility = True
            lblClass.setDefinition(hwynum_cim)
        elif lblClass.name == 'Label Class 5':
            hwyname_cim = lblClass.getDefinition('V3')
            hwyname_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
            hwyname_cim.maplexLabelPlacementProperties.linePlacementMethod = 'OffsetCurvedFromLine'
            hwyname_cim.visibility = True
            lblClass.setDefinition(hwyname_cim)
        else:
            lbl_cim = lblClass.getDefinition('V3')
            lbl_cim.visibility = False
            lblClass.setDefinition(lbl_cim)
        pass

def gen_rails():
    """
    Generates layer of railroads as polyline.

    Returns:
    None
    """
    lyr = m.addDataFromPath(r'https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Railroads_1/FeatureServer/0',
                     web_service_type = 'ARCGIS_SERVER_WEB',
                     custom_parameters = {})
    lyr_rename(lyr, 'rails')
    
    sym = lyr.symbology 
    sym.updateRenderer('SimpleRenderer')
    
    sym.renderer.symbol.applySymbolFromGallery('Railroad')
    lyr.symbology = sym
    pass

# notes
# 33 jim schug trail, z = 40,000
# road name lbl class 5, hwy_num class 3

def gen_waterfeatures(topo=False, labels=False):
    """
    Generates layer of water features as polygon.

    Returns:
    None
    """
    lyr = m.addDataFromPath(r'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Hydrography/MapServer/9',
                     web_service_type = 'ARCGIS_SERVER_WEB',
                     custom_parameters = {})
    lyr_rename(lyr, 'hydro')
    
    sym = lyr.symbology
    sym.updateRenderer('SimpleRenderer')

    if topo == False:
        sym.renderer.symbol.color = {'RGB': [204, 204, 204, 100]}
        sym.renderer.symbol.outlineColor = {'RGB': [51, 51, 51, 100]}
    elif topo == True:
        sym.renderer.symbol.color = {'RGB': [158, 158, 158, 100]}
        sym.renderer.symbol.outlineColor = {'RGB': [51, 51, 51, 100]}
    sym.renderer.symbol.outlineWidth = 1
    lyr.symbology = sym

    gen_waterlabels(lyr, labels)
    pass
    

def gen_waterlabels(lyr, labels):
    """
    Generates labels for water features.

    Parameters:
    lyr (Layer object): Layer of water features
    show (bool): Boolean value to display labels

    Returns:
    None
    """
    if lyr.supports('SHOWLABELS'):
        lblClass = lyr.listLabelClasses()[0]
        lbl_cim = lblClass.getDefinition('V3')
        lbl_cim.textSymbol.symbol.fontFamilyName = 'Times New Roman'
        lbl_cim.textSymbol.symbol.height = 7
        lbl_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
        lblClass.setDefinition(lbl_cim)
        lyr.showLabels = labels
    pass

# Need to add labels to water bodies
def gen_streams(topo=False, labels=False):
    """
    Generates stream features as polyline.

    Returns:
    None
    """
    lyr = m.addDataFromPath(r'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Hydrography/MapServer/15',
                     web_service_type = 'ARCGIS_SERVER_WEB',
                     custom_parameters = {})
    lyr_rename(lyr, 'streams')
    
    sym = lyr.symbology
    sym.updateRenderer('SimpleRenderer')
    
    if topo == False:
        sym.renderer.symbol.color = {'RGB': [204, 204, 204, 100]}
    elif topo == True:
        sym.renderer.symbol.color = {'RGB': [158, 158, 158, 100]}
    sym.renderer.symbol.outlineWidth = 2
    lyr.symbology = sym

    gen_streamlabels(lyr, labels)
    pass
        
def gen_streamlabels(lyr, labels):
    """
    Generates labels for stream features.

    Parameters:
    lyr (Layer object): Layer of stream features
    labels (bool): Boolean value to display labels

    Returns:
    None
    """
    if lyr.supports('SHOWLABELS'):
        lblClass = lyr.listLabelClasses()[0]
        lbl_cim = lblClass.getDefinition('V3')
        lbl_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
        lblClass.setDefinition(lbl_cim)
        lyr.showLabels = labels
    pass
# Need to reformat labels

def addTompkinsDEM():
    """
    Adds DEM layer of Tompkins County.

    Returns:
    lyr (Layer object): Tompkins County DEM
    """
    lyr = m.addDataFromPath(r'https://elevation.its.ny.gov/arcgis/rest/services/County_Tompkins2008_2_meter/ImageServer',
                     web_service_type = 'ARCGIS_SERVER_WEB',
                     custom_parameters = {})
    return(lyr)

ocs = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]]'
ext_lp1 = '-76.5271191647879 42.3051024869337 -76.5054331313753 42.3211945965332 '

ext_lp3 = '-76.525825108996 42.3054403361241 -76.5044214385469 42.3202781463147 '

def createHillshade(ocs, ext, gdb):
    with arcpy.EnvManager(extent = (ext + ocs)):
        arcpy.ddd.HillShade(
            in_raster="County_Tompkins2008_2_meter",
            out_raster=os.path.join(gdb, r'HillSha_Coun1'),
            azimuth=315,
            altitude=45,
            model_shadows="NO_SHADOWS",
            z_factor=1
        )
    lyr = lyr_obj(m, 'HillSha_Coun1')
    return(lyr)

def editHillshade(lyr):
    """
    Renames topo layer and sets gamma.

    Returns:
    None
    """
    lyr_rename(lyr, 'topo')
    sym = lyr.symbology
    sym.colorizer.gamma = 2.0
    lyr.symbology = sym
    pass

def gen_fields(trail):
    """
    Generate fields as polygon layer from raster NLCD.

    Parameters:
    trail (str): Name of trail to generate fields.

    Returns:
    None
    """
    
    nlcd = m.addDataFromPath(r'https://www.arcgis.com/home/item.html?id=3ccf118ed80748909eb85c6d262b426f')

    ext_str = trails_dict[trail]['topo_ext'] + ocs
     
    with ap.EnvManager(extent=ext_str):
        lyr = ap.conversion.RasterToPolygon(
            in_raster="USA NLCD Land Cover",
            out_polygon_features=os.path.join(aprx_gdb, r'RasterT_USA_NLC2'),
            simplify="NO_SIMPLIFY",
            raster_field="Value",
            create_multipart_features="MULTIPLE_OUTER_PART",
            max_vertices_per_feature=None
        )
    fields_sym()
    pass

def fields_sym(lyr=False):
    """
    Modifies fields layer symbology.

    Parameters:
    lyr (Layer object): Fields layer to modify [opt]

    Returns:
    None
    """
    if lyr == False:
        lyr = lyr_obj(m, 'RasterT_USA_NLC2')
    lyr_rename(lyr, 'landcov')
    sym = lyr.symbology
    
    sym.updateRenderer('UniqueValueRenderer')
    sym.renderer.fields = ['gridcode']
    
    # apply symbol through symbology
    for grp in sym.renderer.groups:
        for itm in grp.items:
            if itm.values[0][0] in ['71', '81']:
                itm.symbol.applySymbolFromGallery('10% Ordered Stipple')
            else:
                itm.symbol.color = {'RGB': [255, 255, 255, 0]}
            itm.symbol.outlineWidth = 0
    lyr.symbology = sym

    # edit symbol in cim
    lyr_cim = lyr.getDefinition('V3')
    for grp in lyr_cim.renderer.groups:
        for grpclass in grp.classes:
            if grpclass.label in ['71', '81']:
                grpclass.symbol.symbol.symbolLayers[2].color.values = [255, 255, 255, 0]
    lyr.setDefinition(lyr_cim)
    
    pass

def layout_init(trail):
    """
    Creates Layout object for map display with map frame.

    Returns:
    lyt (Layout object): Layout object for map.
    """
    lyt = aprx.createLayout(6, 9, 'INCH', 'Layout')
    mf = lyt.createMapFrame(MakeRec_LL(0.50, 0.50, 5.0, 3.75), m, 'Map 1')
    
    recTxt = aprx.createTextElement(lyt, MakeRec_LL(0.5, 4.5, 5.0, 3.5), 'POLYGON',
                                 trails_dict[trail]['trail_name'], 14, 'Arial', 'Bold', name='TrailName')
    return(lyt)

def set_mf(trail, lyt=False):
    """
    Sets Map Frame extent camera on layout.

    Parameters:
    trail (str): Name of trail to focus camera.
    lyt (Layout object): Layout object for map display, creates object if False.
    
    Returns:
    mf (Map Frame Element): Main map frame on layout.
    """
    trl_attr = trails_dict[trail]

    if lyt == False:
        lyt = layout_init(trail)
    mf = lyt.listElements('MapFrame_Element')[0]
    mf_cim = mf.getDefinition('V3')
    mf_cim.view.camera.x = trl_attr['mf_camx']
    mf_cim.view.camera.y = trl_attr['mf_camy']
    mf_cim.view.camera.scale = trl_attr['mf_camScale']
    mf.setDefinition(mf_cim)
    gen_scale(lyt, mf)
    return(mf)

def gen_scale(lyt, mf):
    '''
    Generates a standard scale bar with 0.5 mi division and 0.25 mi sub.

    Parameters:
    lyt (Layout object): Layout to add scale bar
    mf (Map Frame element): Map frame to link scale bar

    Returns: Scale bar element
    '''
    # generate scale bar
    sbName = 'Scale Line 1'
    sbStyItm = aprx.listStyleItems('ArcGIS 2D', 'SCALE_BAR', sbName)[0]
    sbEnv = MakeRec_LL(3.35, 0.575, 2.0, 0.5)
    sb = lyt.createMapSurroundElement(sbEnv, 'Scale_bar', mf, sbStyItm)

    # formatting scale bar
    sb_cim = sb.getDefinition('V3')
    sb_cim.divisions = 2
    sb_cim.subdivisions = 2
    sb_cim.fittingStrategy = 'AdjustDivisions'
    sb_cim.division = 0.5
    sb_cim.divisionMarkHeight = 5
    sb_cim.subdivisionMarkHeight = 4
    sb_cim.labelSymbol.symbol.fontFamilyName = 'Arial'
    sb_cim.labelSymbol.symbol.height = 7
    sb_cim.unitLabelSymbol.symbol.fontFamilyName = 'Arial'
    sb_cim.unitLabelSymbol.symbol.height = 7
    sb_cim.anchor = 'BottomRightCorner'
    sb.setDefinition(sb_cim)
    
    return(sb)

aprx_styl = r"C:\Users\kwong\Desktop\best-hikes\styles"

def addStyle(styl_path):
    styleItemList = aprx.styles
    if not styl_path in aprx.styles:
        styleItemList.append(styl_path)
        aprx.updateStyles(styleItemList)
    pass

addStyle(os.path.join(aprx_styl, r'Government.stylx'))

def add_POI():
    """
    Generates layer of points of interest as points.

    Returns:
    None
    """
    ap.management.XYTableToPoint(
        in_table = os.path.join(aprx_dir, r'POI_hikes_18Jan25.csv'),
        out_feature_class = os.path.join(aprx_gdb, r'POI_hikes'),
        x_field="longitude",
        y_field="latitude",
        z_field=None,
        coordinate_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
    )
    
    poi_symbols = {'Bus stop': {'icon': 'Mass Transit',
                                'index': 0},
                  'Geology': {'icon': 'Climbing',
                              'index': 0},
                  'Historic': {'icon': 'Museum',
                               'index': 1},
                  'Lean-to': {'icon': 'Shelter',
                              'index': 1},
                  'Parking': {'icon': 'Parking',
                              'index': 4},
                  'Trailhead': {'icon': 'Trailhead',
                                'index': 0},
                  'Viewpoint': {'icon': 'View',
                                'index': 2},
                  'Waterfall': {'icon': 'Waterfall',
                               'index': 0}
                  }
    
    lyr = lyr_obj(m, 'POI_hikes')
    sym = lyr.symbology
    
    sym.updateRenderer('UniqueValueRenderer')
    sym.renderer.fields = ['type']
    for grp in sym.renderer.groups:
        for itm in grp.items:
            symb_name = poi_symbols[itm.values[0][0]]['icon']
            symb_index = poi_symbols[itm.values[0][0]]['index']
            symb = itm.symbol.applySymbolFromGallery(symb_name, symb_index)
            # itm.symbol = symb
            itm.symbol.size = 12
    lyr.symbology = sym
    pass

# -- INIT ABOVE --
# -- SAMPLE CODE --

def gen_trail(trail): 
    gen_waterfeatures(topo = True,
                      labels = True)
    gen_streams(topo = True,
               labels = False)
    gen_roads(roads_svc[trails_dict[trail]['roads']])
    gen_rails()
    addTompkinsDEM()
    topo = createHillshade(ocs, trails_dict[trail]['topo_ext'], aprx_gdb)
    editHillshade(topo)
    set_mf(trail, False)
    gen_fields(trail)
    add_POI()
    gen_flltPreserve()
    gen_flltTrails()
    for lyr in ('hike_routes_points', 'USA NLCD Land Cover'):
        lyr_rmv = lyr_obj(m, lyr)
        lyr_remove(m, lyr_rmv)
    pass

gen_trail('lp')

# -- SAMPLE CODE --
# -- FORMATTING --

lyr = lyr_obj(m, 'roads')

for lblClass in lyr.listLabelClasses():
    if lblClass.name == 'Label Class 3':
        hwynum_cim = lblClass.getDefinition('V3')
        hwynum_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
        hwynum_cim.textSymbol.symbol.callout = 'PointSymbol'
        hwynum_cim.visibility = True
        lblClass.setDefinition(hwynum_cim)
    elif lblClass.name == 'Label Class 5':
        hwyname_cim = lblClass.getDefinition('V3')
        hwyname_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
        hwyname_cim.maplexLabelPlacementProperties.linePlacementMethod = 'OffsetCurvedFromLine'
        hwyname_cim.visibility = True
        lblClass.setDefinition(hwyname_cim)
    else:
        lbl_cim = lblClass.getDefinition('V3')
        lbl_cim.visibility = False
        lblClass.setDefinition(lbl_cim)

# BEST HIKES ROUTES
sym = lyr.symbology

sym.renderer.symbol.outlineWidth = 2.5
sym.renderer.symbol.outlineColor = {'RGB': [52, 52, 52, 60]}
lyr.symbology = sym

m.addDataFromPath(os.path.join(aprx_gdb, r'besthikes_routes'))
lyr = lyr_obj(m, 'besthikes_routes')

sym = lyr.symbology
sym.renderer.symbol.outlineWidth = 4
sym.renderer.symbol.outlineColor = color_builder('grey20', 30)
lyr.symbology = sym

# LAND COVER
def gen_fields():
    
    nlcd = m.addDataFromPath(r'https://www.arcgis.com/home/item.html?id=3ccf118ed80748909eb85c6d262b426f')
    
    temp_buff = ap.analysis.PairwiseBuffer(
        in_features="besthikes_routes",
        out_feature_class=os.path.join(aprx_gdb, r'route_buffer'),
        buffer_distance_or_field="2000 Feet",
        dissolve_option="NONE",
        dissolve_field=None,
        method="PLANAR",
        max_deviation="0 DecimalDegrees"
    )
    
    lyr = lyr_obj(m, 'route_buffer')
    lyr_sel = ap.management.SelectLayerByAttribute(lyr, 'NEW_SELECTION', 
                                                   '"Name" = \'Lindsay-Parsons\'')
    
    mv = aprx.activeView
    lyrExt = mv.getLayerExtent(lyr, True)
    
    lyr = lyr_obj(m, 'route_buffer')
    sr = ap.Describe(lyr).spatialReference
    
    sr_wkt = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]]'

    ext_str = str(lyrExt)[:-11] + sr_wkt
    print(ext_str)
    
    with ap.EnvManager(extent=ext_str):
        ap.conversion.RasterToPolygon(
            in_raster="USA NLCD Land Cover",
            out_polygon_features=os.path.join(aprx_gdb, r'RasterT_USA_NLC2'),
            simplify="NO_SIMPLIFY",
            raster_field="Value",
            create_multipart_features="MULTIPLE_OUTER_PART",
            max_vertices_per_feature=None
        )

gen_fields()
lyr = lyr_obj(m, 'RasterT_USA_NLC2')
lyr_rename(lyr, 'landcov')
sym = lyr.symbology

sym.updateRenderer('UniqueValueRenderer')
sym.renderer.fields = ['gridcode']
for grp in sym.renderer.groups:
    for itm in grp.items:
        if itm.values[0][0] in ['71', '81']:
            itm.symbol.applySymbolFromGallery('10% Ordered Stipple')
            # Need to make shite background transparent
            # itm.symbol.color = {'RGB': [255, 255, 255, 0]}
#         elif itm.values[0][0] in ['11', '90', '95']:
#             itm.symbol.applySymbolFromGallery('10% Simple Hatch')
        else:
            itm.symbol.color = {'RGB': [255, 255, 255, 0]}
        itm.symbol.outlineWidth = 0
lyr.symbology = sym

lyrlist = ['route_buffer',
           'USA NLCD Land Cover']

for lyr_name in lyrlist:
    lyr = lyr_obj(m, lyr_name)
    lyr_remove(m, lyr)

# HILLSHADE
def createHillshade(ocs, ext, gdb, lp):
    if lp is True:
        with arcpy.EnvManager(outputCoordinateSystem = ocs,
                              extent = (ext + ocs)):
            arcpy.ddd.HillShade(
                in_raster="County_Tompkins2008_2_meter",
                out_raster=os.path.join(gdb, r'HillSha_Coun1'),
                azimuth=315,
                altitude=45,
                model_shadows="NO_SHADOWS",
                z_factor=1
            )

# ext_lp1 - close range (extreme hills)
# ext_lp2 - far range (less hills)
# ext_lp3 - med range (med hills)

ocs = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]]'
ext_lp1 = '-76.5271191647879 42.3051024869337 -76.5054331313753 42.3211945965332 '
ext_lp2 = '-76.5306704765596 42.3004776482477 -76.4988311322597 42.3258859175778 '
ext_lp3 = '-76.525825108996 42.3054403361241 -76.5044214385469 42.3202781463147 '

createHillshade(ocs, ext_lp2, aprx_gdb, True)

lyr = lyr_obj(m, 'HillSha_Coun1')
lyr_rename(lyr, 'topo')
sym = lyr.symbology
sym.colorizer.gamma = 2.0
lyr.symbology = sym
lyr.transparency = 10

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
sym.updateRenderer('SimpleRenderer')

sym.renderer.symbol.color = {'RGB': [153, 153, 153, 100]}
sym.renderer.symbol.outlineWidth = 1
sym.renderer.symbol.outlineColor = {'RGB': [51, 51, 51, 100]}
lyr.symbology = sym
# Need to add labels to water bodies

# STREAMS
lyr = m.addDataFromPath(r'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Hydrography/MapServer/15',
                 web_service_type = 'ARCGIS_SERVER_WEB',
                 custom_parameters = {})
lyr_rename(lyr, 'streams')

sym = lyr.symbology
sym.updateRenderer('SimpleRenderer')

sym.renderer.symbol.color = {'RGB': [153, 153, 153, 100]}
sym.renderer.symbol.outlineWidth = 2
lyr.symbology = sym

if lyr.supports('SHOWLABELS'):
    lblClass = lyr.listLabelClasses()[0]
    lbl_cim = lblClass.getDefinition('V3')
    lbl_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
    lblClass.setDefinition(lbl_cim)
# Need to reformat labels


# ROADS
lyr = m.addDataFromPath(r'https://gisservices.its.ny.gov/arcgis/rest/services/NYS_Streets/MapServer/7',
                 web_service_type = 'ARCGIS_SERVER_WEB',
                 custom_parameters = {})
lyr_rename(lyr, 'roads')

lyr = lyr_obj(m, 'roads')
sym = lyr.symbology 
sym.updateRenderer('SimpleRenderer')

symb = sym.renderer.symbol.listSymbolsFromGallery('Minor Road')[1]
sym.renderer.symbol = symb
lyr.symbology = sym

classList = ['Label Class 3', # state highway no
            'Label Class 4',  # county highway lbl
            'Label Class 5', # state highway lbl
            'Label Class 6']  # county route no

# if lyr.supports('SHOWLABELS'):
#     for lblClassName in classList:
#         lblClass = lyr.listLabelClasses(lblClassName)[0]
#         lbl_cim = lblClass.getDefinition('V3')
# #         lbl_cim.textSymbol.symbol.symbol.symbolLayers[0].color.values = [52, 52, 52, 100]
#         if lblClassName == 'Label Class 3':
#              # print(dir(lbl_cim.textSymbol.symbol.callout.pointSymbol.symbolLayers[0]))
# #             print((lbl_cim.textSymbol.symbol.callout.pointSymbol.symbolLayers[0].size))
# #         lblClass.setDefinition(lbl_cim)
# Need to find label and callout class for roads

# POI
aprx_styl = r"C:\Users\kwong\Desktop\best-hikes\styles"

def addStyle(styl_path):
    styleItemList = aprx.styles
    if not styl_path in aprx.styles:
        styleItemList.append(styl_path)
        aprx.updateStyles(styleItemList)
    pass

addStyle(os.path.join(aprx_styl, r'Government.stylx'))

ap.management.XYTableToPoint(
    in_table = os.path.join(aprx_dir, r'POI_hikes_18Jan25.csv'),
    out_feature_class = os.path.join(aprx_gdb, r'POI_hikes'),
    x_field="longitude",
    y_field="latitude",
    z_field=None,
    coordinate_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
)

poi_symbols = {'Bus stop': {'icon': 'Mass Transit',
                            'index': 0},
              'Geology': {'icon': 'Climbing',
                          'index': 0},
              'Historic': {'icon': 'Museum',
                           'index': 1},
              'Lean-to': {'icon': 'Shelter',
                          'index': 1},
              'Parking': {'icon': 'Parking',
                          'index': 4},
              'Trailhead': {'icon': 'Trailhead',
                            'index': 0},
              'Viewpoint': {'icon': 'View',
                            'index': 2},
              'Waterfall': {'icon': 'Waterfall',
                           'index': 0}
              }

lyr = lyr_obj(m, 'POI_hikes')
sym = lyr.symbology

sym.updateRenderer('UniqueValueRenderer')
sym.renderer.fields = ['type']
for grp in sym.renderer.groups:
    for itm in grp.items:
        symb_name = poi_symbols[itm.values[0][0]]['icon']
        symb_index = poi_symbols[itm.values[0][0]]['index']
        symb = itm.symbol.applySymbolFromGallery(symb_name, symb_index)
        # itm.symbol = symb
        itm.symbol.size = 12
lyr.symbology = sym

# RAILS
lyr = m.addDataFromPath(r'https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Railroads_1/FeatureServer/0',
                 web_service_type = 'ARCGIS_SERVER_WEB',
                 custom_parameters = {})
lyr_rename(lyr, 'rails')

sym = lyr.symbology 
sym.updateRenderer('SimpleRenderer')

sym.renderer.symbol.applySymbolFromGallery('Railroad')
lyr.symbology = sym

# FLLT PRESERVES AND TRAILS
lyr = ap.conversion.JSONToFeatures(
    in_json_file=os.path.join(aprx_dir, r'fllt-preserve-boundaries.geojson'),
    out_features=os.path.join(aprx_gdb, r'flltPreserve'),
    geometry_type="POLYGON"
)
lyr = lyr_obj(m, 'flltPreserve')

sym = lyr.symbology
sym.updateRenderer('SimpleRenderer')

sym.renderer.symbol.applySymbolFromGallery('Extent Transparent Gray')
# sym.renderer.symbol.outlineWidth = 1.5
# sym.renderer.symbol.outlineColor = {'RGB': [100, 100, 100, 60]}
lyr.symbology = sym

lyr = ap.conversion.JSONToFeatures(
    in_json_file=os.path.join(aprx_dir, r'fllt-trails.geojson'),
    out_features=os.path.join(aprx_gdb, r'flltTrails'),
    geometry_type="POLYLINE"
)
lyr = lyr_obj(m, 'flltTrails')

sym = lyr.symbology
sym.updateRenderer('SimpleRenderer')

sym.renderer.symbol.applySymbolFromGallery('Dashed 2:2')
sym.renderer.symbol.outlineWidth = 0.7
lyr.symbology = sym


# -- TO BE FORMATTED --
# m.addDataFromPath(r'https://elevation.its.ny.gov/arcgis/rest/services/NYS_Statewide_Hillshade/MapServer/3',
#                  web_service_type = 'ARCGIS_SERVER_WEB',
#                  custom_parameters = {})

lyr = lyr_obj(m, 'hike_routes_tracks')

sym = lyr.symbology

sym.renderer.symbol.outlineWidth = 3.4
sym.renderer.symbol.outlineColor = {'RGB': [52, 52, 52, 60]}
lyr.symbology = sym

aprx_styl = r"C:\Users\kwong\Desktop\best-hikes\styles"

def addStyle(styl_path):
    styleItemList = aprx.styles
    if not styl_path in aprx.styles:
        styleItemList.append(styl_path)
        aprx.updateStyles(styleItemList)
    pass

addStyle(os.path.join(aprx_styl, r'Government.stylx'))

ap.management.XYTableToPoint(
    in_table = os.path.join(aprx_dir, r'POI_hikes_18Jan25.csv'),
    out_feature_class = os.path.join(aprx_gdb, r'POI_hikes'),
    x_field="longitude",
    y_field="latitude",
    z_field=None,
    coordinate_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
)

poi_symbols = {'Bus stop': {'icon': 'Mass Transit',
                            'index': 0},
              'Geology': {'icon': 'Climbing',
                          'index': 0},
              'Historic': {'icon': 'Museum',
                           'index': 1},
              'Lean-to': {'icon': 'Shelter',
                          'index': 1},
              'Parking': {'icon': 'Parking',
                          'index': 4},
              'Trailhead': {'icon': 'Trailhead',
                            'index': 0},
              'Viewpoint': {'icon': 'View',
                            'index': 2},
              'Waterfall': {'icon': 'Waterfall',
                           'index': 0}
              }

lyr = lyr_obj(m, 'POI_hikes')
sym = lyr.symbology

sym.updateRenderer('UniqueValueRenderer')
sym.renderer.fields = ['type']
for grp in sym.renderer.groups:
    for itm in grp.items:
        symb_name = poi_symbols[itm.values[0][0]]['icon']
        symb_index = poi_symbols[itm.values[0][0]]['index']
        symb = itm.symbol.applySymbolFromGallery(symb_name, symb_index)
        # itm.symbol = symb
        itm.symbol.size = 12
lyr.symbology = sym

