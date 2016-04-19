import arcpy
from arcpy import mapping
import os



#Map Parameters

mxd = r"\\Tpp-742166-w\_lrtp\CreateProjectsData.mxd"
print mxd
mxd = arcpy.mapping.MapDocument(mxd)
df = arcpy.mapping.ListDataFrames(mxd)[0]
lyr = arcpy.mapping.ListLayers(mxd)
print lyr



#Environment Variables
arcpy.env.workspace = r"C:\_LRTP\TxDOT_ProjectsData_tests.gdb"
arcpy.env.overwriteOutput = True

#Layers
projects_fc = "TxDOT_Projects\TxDOT_Projects"
out_features = "TxDOT_Projects_NAD83_test"
base_corridors = "TPP_GIS.APP_TPP_GIS_ADMIN.LRTP_Corridors_Combined"
CorList = r"C:\_LRTP\_TxDOT_ProjectsData.gdb\Corridors"

def MapCleanup():
   for lyr in arcpy.mapping.ListLayers(mxd, "*",df):
      if lyr.name == out_features:
         arcpy.mapping.RemoveLayer(df, lyr)

MapCleanup()

#Required Fields
Texas_Trunk = "TRUNK_SYS"
Alternate_Route = "ALT_RTE"
Ntl_Freight = "NATL_FRT"
PrimFrt = "PHFS_FRT"
Tx_Freight_Prim = "PRMRY_FRT"
Tx_Freight_Sec = "SCNDRY_FRT"
Energy_Sector = "ENRGY_SCTR"
Major_Evac = "EVAC_ROUTE"
Evac_Contra_Flow = "EVAC_CNTRA"
Potential_Evac_Lanes = "EVAC_LANE"
Ports_to_Plains = "PRT_TO_PLN"
Key_Corridors = "KEY_COR"
Super2_Current = "SPR_2"
Prop_Super2 = "PROP_SPR_2"


#Project TxDOT_Projects to NAD83
print "Setting Geographic Projection.."
sr = arcpy.SpatialReference("NAD 1983")
# transformation = "WGS_1984_(ITRF00)_To_NAD_1983"
# arcpy.Project_management(projects_fc, out_features, sr, transformation)
arcpy.Project_management(projects_fc, out_features, sr)



#Add All LRTP Fields
print "Adding Required Fields..."

if not arcpy.ListFields(out_features, Texas_Trunk):
        print Texas_Trunk + " field being added...."
        arcpy.AddField_management(out_features, Texas_Trunk, "Text", "3")

if not arcpy.ListFields(out_features, Alternate_Route):
        print Alternate_Route + " field being added...."
        arcpy.AddField_management(out_features, Alternate_Route, "Text", "3")

if not arcpy.ListFields(out_features, Ntl_Freight):
        print Ntl_Freight + " field being added...."
        arcpy.AddField_management(out_features, Ntl_Freight, "Text", "3")

if not arcpy.ListFields(out_features, PrimFrt):
        print PrimFrt + " field being added...."
        arcpy.AddField_management(out_features, PrimFrt, "Text", "3")

if not arcpy.ListFields(out_features, Tx_Freight_Prim):
        print Tx_Freight_Prim + " field being added...."
        arcpy.AddField_management(out_features, Tx_Freight_Prim, "Text", "3")

if not arcpy.ListFields(out_features, Tx_Freight_Sec):
     print Tx_Freight_Sec + " field being added...."
     arcpy.AddField_management(out_features, Tx_Freight_Sec, "Text", "3")

if not arcpy.ListFields(out_features, Energy_Sector):
     print Energy_Sector + " field being added...."
     arcpy.AddField_management(out_features, Energy_Sector, "Text", "3")

if not arcpy.ListFields(out_features, Major_Evac):
     print Major_Evac + " field being added...."
     arcpy.AddField_management(out_features, Major_Evac, "Text", "3")

if not arcpy.ListFields(out_features, Evac_Contra_Flow):
     print Evac_Contra_Flow + " field being added...."
     arcpy.AddField_management(out_features, Evac_Contra_Flow, "Text", "3")

if not arcpy.ListFields(out_features, Potential_Evac_Lanes):
     print Potential_Evac_Lanes + " field being added...."
     arcpy.AddField_management(out_features, Potential_Evac_Lanes, "Text", "3")

if not arcpy.ListFields(out_features, Ports_to_Plains):
     print Ports_to_Plains + " field being added...."
     arcpy.AddField_management(out_features, Ports_to_Plains, "Text", "3")

if not arcpy.ListFields(out_features, Key_Corridors):
     print Key_Corridors + " field being added...."
     arcpy.AddField_management(out_features, Key_Corridors, "Text", "3")

if not arcpy.ListFields(out_features, Super2_Current):
     print Super2_Current + " field being added...."
     arcpy.AddField_management(out_features, Super2_Current, "Text", "3")

if not arcpy.ListFields(out_features, Prop_Super2):
     print Prop_Super2 + " field being added...."
     arcpy.AddField_management(out_features, Prop_Super2, "Text", "3")

print "All Required Fields Sucessfully Added..."

#Set default to'NO'
print "Calculating NO values as default..."

def CalcNoValues():

    columns = ['TRUNK_SYS', 'ALT_RTE', 'NATL_FRT', 'PHFS_FRT', 'PRMRY_FRT', 'SCNDRY_FRT', 'ENRGY_SCTR', 'EVAC_ROUTE', 'EVAC_CNTRA', 'EVAC_LANE', 'PRT_TO_PLN', 'KEY_COR', 'SPR_2', 'PROP_SPR_2']
    noCursor = arcpy.da.UpdateCursor(out_features, columns )


    for noRecord in noCursor:
        for column in columns:
                noRecord[columns.index(column)] = "NO"
                noCursor.updateRow(noRecord)
    del noCursor


CalcNoValues()

#Select Projects by Location Against Corridors

print "Making Selections & Populating LRTP Fields..."
def CreateLRTPflags():
    cursor1 = arcpy.da.SearchCursor(CorList, ["FIELD"])

    for row1 in cursor1:
        for lyr in arcpy.mapping.ListLayers(mxd, "", df):
            if lyr.name == base_corridors:
                lyr.definitionQuery = row1[0] + " = 1"

        arcpy.SelectLayerByLocation_management (out_features, "INTERSECT", base_corridors, "10 feet","NEW_SELECTION" )

        cursor2 = arcpy.da.UpdateCursor(out_features, [row1[0]])

        for record1 in cursor2:
            record1[0] = "YES"
            cursor2.updateRow(record1)
        print record1[0]

    del cursor1
    del cursor2

CreateLRTPflags()


print "LRTP Corridor Values updated..."


