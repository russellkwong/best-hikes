# Add new styles

aprx_stylx = r'C:\Users\kwong\Desktop\best-hikes\styles'
newStyles = ['Forestry_en.stylx',
             'Government.stylx',
             'US_Shields.stylx']

styleItemList = aprx.styles

for stylx in newStyles:
    if not stylx in styleItemList:
        styleItemList.append(os.path.join(aprx_stylx, stylx))
aprx.updateStyles(styleItemList)


# Create Style Guide
# lyt = aprx.createLayout(8.5, 11, 'INCH', 'StyleGuide')
# mf = lyt.createMapFrame(MakeRec_LL(0.50, 0.50, 0.50, 0.50), m, 'Map 1')

# txt_title = aprx.createTextElement(lyt, MakeRec_LL(0.75, 10.0, 5.0, 0.25), 'POLYGON',
#                                    'ArcGIS Pro Symbols', 16, 'Arial', 'Bold', name='Title')

leg_poi = lyt.createMapSurroundElement(geometry=arcpy.Point(0.75, 9.5),
                                     mapsurround_type='LEGEND',
                                     mapframe=mf,
                                     style_item=None,
                                     name='Legend POI')

# print(help(lyt.createMapSurroundElement))


lyr = lyr_obj(m, 'POI_hikes')
lyr_cim = lyr.getDefinition('V3')

for grp in lyr_cim.renderer.groups:
    grp.heading = 'ArcGIS Pro Symbols'
    
lyr.setDefinition(lyr_cim)

lyt_cim = lyt.getDefinition('V3')
for elm in lyt_cim.elements:
    if elm.name == 'Legend POI':
        for itm in reversed(elm.items):
            itm.showLayerName = False
            if itm.name == 'POI_hikes':
                itm.labelSymbol.symbol.fontFamilyName = 'Arial'
                itm.headingSymbol.symbol.fontFamilyName = 'Arial'
lyt.setDefinition(lyt_cim)

lyr_rename(lyr_obj(m, 'POI_hikes'), 'arcgis-pro-symb')


# ap.management.XYTableToPoint(
#     in_table = os.path.join(aprx_dir, r'POI_hikes_18Jan25.csv'),
#     out_feature_class = os.path.join(aprx_gdb, r'POI_hikes_govt'),
#     x_field="longitude",
#     y_field="latitude",
#     z_field=None,
#     coordinate_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
# )

poi_symbols = {'Bus stop': 'Bus Stop',
              'Geology': 'Climbing', 
              'Historic': 'Museum',
              'Lean-to': 'Shelter',
              'Parking': 'Parking',
              'Trailhead': 'Trailhead',
              'Viewpoint': 'Wildlife Viewing',
              'Waterfall': 'Waterfall'}

lyr = lyr_obj(m, 'POI_hikes_govt')
sym = lyr.symbology

sym.updateRenderer('UniqueValueRenderer')
sym.renderer.fields = ['type']
for grp in sym.renderer.groups:
    for itm in grp.items:
        print('type:', (itm.label))
        symb_list = itm.symbol.listSymbolsFromGallery(poi_symbols[itm.values[0][0]])
        for symb in symb_list:
            itm.symbol = symb
        # itm.symbol.color = {'RGB': [32, 32, 32, 100]}
        itm.symbol.size = 12
lyr.symbology = sym
