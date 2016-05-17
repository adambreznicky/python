__file__ = 'FC_Project_ErrorChecks_v1'
__date__ = '10/21/2014'
__author__ = 'ABREZNIC'
import arcpy, xlwt, datetime, os
now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay

comanche = "Connection to Comanche.sde"
roadways = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
subfiles = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
workspace = "C:\\TxDOT\\QC\\FC_Project"
roads = {}
subs = {}

if os.path.exists(workspace + "\\FCerrors_" + today + ".xls"):
    os.remove(workspace + "\\FCerrors_" + today + ".xls")

def dictionary():
    print "Building dictionaries..."
    cursor = arcpy.da.SearchCursor(roadways, ["RTE_ID", "FULL_ST_NM"], """ RTE_CLASS = '3' """)
    for row in cursor:
        roads[row[0]] = row[1]
    del cursor
    del row
    print "Roadways dictionary complete."

    cursor = arcpy.da.SearchCursor(subfiles, ["OBJECTID", "RTE_ID", "CONTROLSEC", "FC", "STREET_NAME", "BEGIN_TERMINI", "END_TERMINI"], """ SUBFILE = 3 """)
    for row in cursor:
        subs[row[0]] = [row[1], row[2], row[3], row[4], row[5], row[6]]
    del cursor
    del row
    print "Subfiles dictionary complete."

def infiltrate():
    print "Commencing infiltration..."
    IDs = []
    controlsections = []
    fcvalue = []
    updateSN = {}
    updateUS = []
    termini = []
    begindict = {}
    enddict ={}
    subfileUpdates = []

    for i in subs.keys():
        oid = i
        values = subs[oid]
        id = values[0]
        cs = values[1]
        fc = values[2]
        sn = values[3]
        bt = values[4]
        et = values[5]

        if id is None or id == "":
            IDs.append([oid, id, "Populate RTE_ID."])

        if cs is None or cs == "":
            controlsections.append([oid, id, cs, "Populate Control Section."])

        classes = range(1, 8)
        if fc not in classes:
            fcvalue.append([oid, id, fc, "Bad FC value. Must be in range 1-7."])

        if bt is None or bt == "" or bt == " ":
            termini.append([oid, id, bt, "Populate BEGIN_TERMINI."])
            bt = "NULL"
        if et is None or et == "" or et == " ":
            termini.append([oid, id, et, "Populate END_TERMINI."])
            et = "NULL"

        if sn is None or sn == "":
            updateSN[oid] = id
            sn = "NULL"
        if "_" in bt or "_" in et or "_" in sn:
            updateUS.append(oid)

        if id not in begindict.keys():
            newlist = []
            newlist.append(bt)
            begindict[id] = newlist
        else:
            current = begindict[id]
            if bt not in current:
                current.append(bt)
                begindict[id] = current
            else:
                termini.append([oid, id, bt, "Duplicate BEGIN_TERMINI."])
        if id not in enddict.keys():
            newlist = []
            newlist.append(et)
            enddict[id] = newlist
        else:
            current = enddict[id]
            if et not in current:
                current.append(et)
                enddict[id] = current
            else:
                termini.append([oid, id, et, "Duplicate END_TERMINI."])

    print "Beginning updates..."
    where = ""
    if len(updateSN) > 0:
        trigger = 0
        for n in updateSN.keys():
            if trigger == 0:
                where = "OBJECTID = " + str(n)
                trigger += 1
            else:
                where += " OR OBJECTID = " + str(n)
        # cursor = arcpy.da.UpdateCursor(subfiles, ["RTE_ID", "STREET_NAME"], where)
        # for row in cursor:
        #     route_id = row[0]
        #     roadway_name = roads[route_id]
        #     row[1] = roadway_name
        #     cursor.updateRow(row)
        # del cursor
        # del row
    else:
        print "Length of updateSN list is funky."
        print len(updateSN)
    subfileUpdates.append(where)
    print "Street name update complete."
    where = ""
    if len(updateUS) > 0:
        trigger = 0
        for n in updateUS:
            if trigger == 0:
                where = "OBJECTID = " + str(n)
                trigger += 1
            else:
                where += " OR OBJECTID = " + str(n)
        # cursor = arcpy.da.UpdateCursor(subfiles, ["STREET_NAME", "BEGIN_TERMINI", "END_TERMINI"], where)
        # for row in cursor:
        #     row[0] = row[0].replace("_", " ")
        #     row[1] = row[1].replace("_", " ")
        #     row[2] = row[2].replace("_", " ")
        #     row[0] = row[0].strip()
        #     row[1] = row[1].strip()
        #     row[2] = row[2].strip()
        #     cursor.updateRow(row)
        # del cursor
        # del row
    else:
        print "Length of updateUS list is funky."
        print len(updateUS)
    subfileUpdates.append(where)
    print "Termini update complete."

    errors = [IDs, controlsections, fcvalue, termini, subfileUpdates]
    return errors

def report():
    dictionary()
    errors = infiltrate()
    book = xlwt.Workbook()
    font = xlwt.Font()  # Create the Font
    font.name = 'Calibri'
    font.height = 240  # =point size you want * 20
    style = xlwt.XFStyle()  # Create the Style
    style.font = font  # Apply the Font to the Style

    IDproblem = errors[0]
    IDsheet = book.add_sheet("RTE_IDs")
    IDline = 0
    IDsheet.write(IDline, 0, "OBJECTID", style=style)
    IDsheet.write(IDline, 1, "RTE_ID", style=style)
    IDsheet.write(IDline, 2, "Description", style=style)
    IDline += 1
    for i in IDproblem:
        IDsheet.write(IDline, 0, i[0], style=style)
        IDsheet.write(IDline, 1, i[1], style=style)
        IDsheet.write(IDline, 2, i[2], style=style)
        IDline += 1

    CSproblem = errors[1]
    CSsheet = book.add_sheet("CONTROLSEC")
    CSline = 0
    CSsheet.write(CSline, 0, "OBJECTID", style=style)
    CSsheet.write(CSline, 1, "RTE_ID", style=style)
    CSsheet.write(CSline, 2, "CONTROLSEC", style=style)
    CSsheet.write(CSline, 3, "Description", style=style)
    CSline += 1
    for i in CSproblem:
        CSsheet.write(CSline, 0, i[0], style=style)
        CSsheet.write(CSline, 1, i[1], style=style)
        CSsheet.write(CSline, 2, i[2], style=style)
        CSsheet.write(CSline, 3, i[3], style=style)
        CSline += 1

    FCproblem = errors[2]
    FCsheet = book.add_sheet("FC")
    FCline = 0
    FCsheet.write(FCline, 0, "OBJECTID", style=style)
    FCsheet.write(FCline, 1, "RTE_ID", style=style)
    FCsheet.write(FCline, 2, "FC", style=style)
    FCsheet.write(FCline, 3, "Description", style=style)
    FCline += 1
    for i in FCproblem:
        FCsheet.write(FCline, 0, i[0], style=style)
        FCsheet.write(FCline, 1, i[1], style=style)
        FCsheet.write(FCline, 2, i[2], style=style)
        FCsheet.write(FCline, 3, i[3], style=style)
        FCline += 1

    Tproblem = errors[3]
    Tsheet = book.add_sheet("TERMINI")
    Tline = 0
    Tsheet.write(Tline, 0, "OBJECTID", style=style)
    Tsheet.write(Tline, 1, "RTE_ID", style=style)
    Tsheet.write(Tline, 2, "TERMINI", style=style)
    Tsheet.write(Tline, 3, "Description", style=style)
    Tline += 1
    for i in Tproblem:
        Tsheet.write(Tline, 0, i[0], style=style)
        Tsheet.write(Tline, 1, i[1], style=style)
        Tsheet.write(Tline, 2, i[2], style=style)
        Tsheet.write(Tline, 3, i[3], style=style)
        Tline += 1

    SUproblem = errors[4]
    SUsheet = book.add_sheet("updated")
    SUsheet.write(0, 0, "STREETNAME", style=style)
    SUsheet.write(1, 0, "TERMINI", style=style)
    SUsheet.write(0, 1, SUproblem[0], style=style)
    SUsheet.write(1, 1, SUproblem[1], style=style)

    book.save(workspace + "\\FCerrors_" + today + ".xls")
    print "Report complete."

report()
print "that's all folks!"