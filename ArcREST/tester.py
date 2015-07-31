__file__ = 'backup_v1'
__date__ = '5/26/2015'
__author__ = 'ABREZNIC'
from arcrest.security import AGOLTokenSecurityHandler
from arcrest.agol import FeatureLayer
import os
import json
import arcpy, datetime
import mohawk

output = "C:\\TxDOT\\Scripts\\javascript\\Guardrail\\Snake\\BACKUP"

if __name__ == "__main__":
    username = "Adam.Breznicky_TXDOT"
    password = mohawk.hangnail(username)
    url = "http://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/OnSystemRoadways/FeatureServer/0"
    proxy_port = None
    proxy_url = None

    agolSH = AGOLTokenSecurityHandler(username=username,
                                      password=password)

    fl = FeatureLayer(
        url=url,
        securityHandler=agolSH,
        proxy_port=proxy_port,
        proxy_url=proxy_url,
        initialize=True)

    qmin = 0
    qmax = 2000
    count = fl.query(returnIDsOnly=True)
    cList = count["objectIds"]
    cValue = cList[-1]
    listLen = len(cList)
    print listLen

    now = datetime.datetime.now()
    curMonth = now.strftime("%m")
    curDay = now.strftime("%d")
    curYear = now.strftime("%Y")
    # arcpy.CreateFileGDB_management(output, "GET" + curYear + curMonth + curDay)
    werkspace = output + os.sep + "GET" + curYear + curMonth + curDay + ".gdb"

    # sample = "C:\\TxDOT\\Scripts\\javascript\\Guardrail\\Data\\GuardrailPoints.gdb\\GuardrailPoints"
    # sr = arcpy.SpatialReference(3857)
    # arcpy.CreateFeatureclass_management(werkspace, "GuardrailEndTreatments", "POINT", sample, "DISABLED", "DISABLED", sr)
    # fc = werkspace + os.sep + "GuardrailEndTreatments"
    # print "dbase created."
    # flds = ["SHAPE@"]
    # fieldList = arcpy.ListFields(fc)
    # for i in fieldList:
    #     if i.name != "OBJECTID" and i.name != "Shape":
    #         flds.append(i.name)

    counter = 0
    while qmin <= cValue:
        theReturn = fl.query(where="1=1",out_fields='*',returnGeometry=True)
        stringer = str(theReturn)
        print stringer
        d = json.loads(stringer)
        print "dictionary compiled."

        # cursor = arcpy.da.InsertCursor(fc, flds)
        points = d["features"]
        for pt in points:
            geom = pt["geometry"]
            # print geom
            # x = geom["x"]
            # y = geom["y"]
            # array = arcpy.Point(x, y)

            # att = pt["attributes"]
            # tt = att["TreatmentType"]
            # rs = att["RoadbedSide"]
            # ct = att["Comment"]
            # ac = att["AccuracyFeet"]
            # sd = att["Speed"]
            # dv = att["Device"]
            # lt = att["Latitude"]
            # lg = att["Longitude"]
            # dt = att["Date"]

            # cursor.insertRow([array, tt, rs, ct, ac, sd, dv, lt, lg, dt])
            counter += 1
            # print str(counter) + "\\" + str(listLen)
        qmin += 2000
        qmax += 2000

print "that's all folks!"