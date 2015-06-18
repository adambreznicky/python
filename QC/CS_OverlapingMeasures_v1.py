__file__ = 'DuplicateRte_IDs_v1'
__date__ = '3/10/2015'
__author__ = 'ABREZNIC'
import arcpy

subfiles = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
roadways = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
csTable = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.RTE_CONTROL_SECTION"
# locals = ""
# subfiles = "C:\\TxDOT\\Scratch\\scratch.gdb\\overlap"
# roadways = "C:\\TxDOT\\Scratch\\scratch.gdb\\roadz"

def subfilesCS():
    dictionary = {}
    cursor = arcpy.da.SearchCursor(subfiles, ["CONTROLSEC", "BMP", "EMP", "RTE_ID", "COUNTY", "CENSUS_CITY", "SUBFILE"], "SUBFILE <> 2", "", "", (None, "ORDER BY SUBFILE ASC, CONTROLSEC ASC, BMP ASC"))
    last = 0
    for row in cursor:
        if row[6] != last:
            print "Checking SUBFILE: " + str(row[6])
            last = row[6]
            dictionary = {}
        bmp = int(row[1] * 1000)
        emp = int(row[2] * 1000)
        key = row[0] + row[3]
        if key in dictionary.keys():
            current = dictionary[key]
            for record in current:
                if bmp in record:
                    print "Overlap CS: " + row[0] + ", bmp: " + str(bmp) + ", id: " + str(row[3])
                elif emp in record:
                    print "Overlap CS: " + row[0] + ", emp: " + str(emp) + ", id: " + str(row[3])
            ranger = range(bmp, emp)
            current.append(ranger)
            dictionary[key] = current

        else:
            ranger = range(bmp, emp)
            dictionary[key] = [ranger]

    print "Checking SUBFILE: 2"
    counties = range(1, 255)
    for i in counties:
        dictionary = {}
        cursor = arcpy.da.SearchCursor(subfiles, ["CONTROLSEC", "BMP", "EMP", "RTE_ID", "COUNTY", "CENSUS_CITY", "SUBFILE"], "SUBFILE = 2 AND COUNTY = " + str(i), "", "", (None, "ORDER BY SUBFILE ASC, CONTROLSEC ASC, BMP ASC"))
        for row in cursor:
            bmp = int(row[1] * 1000)
            emp = int(row[2] * 1000)
            key = row[0]
            if key in dictionary.keys():
                current = dictionary[key]
                for record in current:
                    if bmp in record:
                        print "Overlap CS: " + row[0] + ", bmp: " + str(bmp) + ", id: " + str(row[3])
                    elif emp in record:
                        print "Overlap CS: " + row[0] + ", emp: " + str(emp) + ", id: " + str(row[3])
                ranger = range(bmp, emp)
                current.append(ranger)
                dictionary[key] = current

            else:
                ranger = range(bmp, emp)
                dictionary[key] = [ranger]

    print "Checking the CS table."
    dictionary = {}
    cursor = arcpy.da.SearchCursor(csTable, ["CNTRL_SEC", "GIS_FROM", "GIS_TO", "RIA_RTE_ID"], "", "", "", (None, "ORDER BY CNTRL_SEC ASC, GIS_FROM ASC"))
    for row in cursor:
        bmp = int(row[1] * 1000)
        emp = int(row[2] * 1000)
        key = row[0] + row[3]
        if key in dictionary.keys():
            current = dictionary[key]
            for record in current:
                if bmp in record:
                    print "Overlap CS: " + row[0] + ", bmp: " + str(bmp) + ", id: " + str(row[3])
                elif emp in record:
                    print "Overlap CS: " + row[0] + ", emp: " + str(emp) + ", id: " + str(row[3])
            ranger = range(bmp, emp)
            current.append(ranger)
            dictionary[key] = current

        else:
            ranger = range(bmp, emp)
            dictionary[key] = [ranger]

def measuresCheck():

    classes = ["1' OR RTE_CLASS = '6", "3' OR RTE_CLASS = '7", 4, 5, 8]
    for i in classes:
        print "RTE_CLASS: " + str(i)
        roadbeds = ["KG", "LG", "RG", "XG", "AG", "MG", "SG", "PG", "TG", "YG", "BG", "CONNECTOR' OR RDBD_TYPE = 'RAMP' OR RDBD_TYPE = 'TURNAROUND' OR RDBD_TYPE = 'CNCTR-GS"]
        for rdbd in roadbeds:
            dictionary = {}
            cursor = arcpy.da.SearchCursor(roadways, ["RTE_ID", "SHAPE@"], "(RTE_CLASS = '" + str(i) + "') AND (RDBD_TYPE = '" + rdbd + "')", "", "", (None, "ORDER BY RTE_ID ASC, RTE_LEN DESC"))
            for row in cursor:
                Bmeas = row[1].extent.MMin
                Emeas = row[1].extent.MMax
                if len(str(Bmeas).split(".")[1]) > 3:
                    print row[0] + ": " + str(Bmeas)
                if len(str(Emeas).split(".")[1]) > 3:
                    print row[0] + ": " + str(Emeas)
                bmp = int(Bmeas * 1000)
                emp = int(Emeas * 1000)
                key = row[0]
                if key in dictionary.keys():
                    current = dictionary[key]
                    for record in current:
                        if bmp in record:
                            print "Overlap Measure: " + row[0] + ", bmp: " + str(bmp)
                        elif emp in record:
                            print "Overlap Measure: " + row[0] + ", emp: " + str(emp)
                    ranger = range((bmp + 1), emp)
                    current.append(ranger)
                    dictionary[key] = current

                else:
                    ranger = range((bmp + 1), emp)
                    dictionary[key] = [ranger]

    counties = range(1, 255)
    for i in counties:
        length = len(str(i))
        if length == 1:
            string = "00" + str(i)
        elif length == 2:
            string = "0" + str(i)
        elif length == 3:
            string = str(i)
        dictionary = {}
        cursor = arcpy.da.SearchCursor(roadways, ["RTE_ID", "SHAPE@"], "RTE_CLASS = '2' AND RTE_ID LIKE '" + string + "%'", "", "", (None, "ORDER BY RTE_ID ASC"))
        for row in cursor:
            Bmeas = row[1].extent.MMin
            Emeas = row[1].extent.MMax
            if len(str(Bmeas).split(".")[1]) > 3:
                print row[0] + ": " + str(Bmeas)
            if len(str(Emeas).split(".")[1]) > 3:
                print row[0] + ": " + str(Emeas)
            bmp = int(Bmeas * 1000)
            emp = int(Emeas * 1000)
            key = row[0]
            if key in dictionary.keys():
                current = dictionary[key]
                for record in current:
                    if bmp in record:
                        print "Overlap Measure: " + row[0] + ", bmp: " + str(bmp)
                    elif emp in record:
                        print "Overlap Measure: " + row[0] + ", emp: " + str(emp)
                ranger = range((bmp + 1), emp)
                current.append(ranger)
                dictionary[key] = current

            else:
                ranger = range((bmp + 1), emp)
                dictionary[key] = [ranger]

def localstreets():
    print "Control Section overlaps."
    dictionary = {}
    cursor = arcpy.da.SearchCursor(locals, ["CONTROLSEC", "BMP", "EMP", "RTE_ID"], "", "", "", (None, "ORDER BY CONTROLSEC ASC, BMP ASC"))
    for row in cursor:
        bmp = int(row[1] * 1000)
        emp = int(row[2] * 1000)
        key = row[0]
        if key in dictionary.keys():
            current = dictionary[key]
            for record in current:
                if bmp in record:
                    print "Overlap CS: " + row[0] + ", bmp: " + str(bmp)
                elif emp in record:
                    print "Overlap CS: " + row[0] + ", emp: " + str(emp)
            ranger = range(bmp, emp)
            current.append(ranger)
            dictionary[key] = current
        else:
            ranger = range(bmp, emp)
            dictionary[key] = [ranger]

    print "Measure overlaps."
    dictionary = {}
    cursor = arcpy.da.SearchCursor(locals, ["RTE_ID", "SHAPE@"], "", "", "", (None, "ORDER BY RTE_ID ASC"))
    for row in cursor:
        Bmeas = row[1].extent.MMin
        Emeas = row[1].extent.MMax
        if len(str(Bmeas).split(".")[1]) > 3:
            print row[0] + ": " + str(Bmeas)
        if len(str(Emeas).split(".")[1]) > 3:
            print row[0] + ": " + str(Emeas)
        bmp = int(Bmeas * 1000)
        emp = int(Emeas * 1000)
        key = row[0]
        if key in dictionary.keys():
            current = dictionary[key]
            for record in current:
                if bmp in record:
                    print "Overlap Measure: " + row[0] + ", bmp: " + str(bmp)
                elif emp in record:
                    print "Overlap Measure: " + row[0] + ", emp: " + str(emp)
            ranger = range((bmp + 1), emp)
            current.append(ranger)
            dictionary[key] = current

        else:
            ranger = range((bmp + 1), emp)
            dictionary[key] = [ranger]

def test():

    dictionary = {}
    cursor = arcpy.da.SearchCursor(roadways, ["RTE_ID", "SHAPE@"], "RTE_ID = 'SL0343-KG'", "", "", (None, "ORDER BY RTE_ID ASC"))
    for row in cursor:
        Bmeas = row[1].extent.MMin
        Emeas = row[1].extent.MMax
        if len(str(Bmeas).split(".")[1]) > 3:
            print row[0] + ": " + str(Bmeas)
        if len(str(Emeas).split(".")[1]) > 3:
            print row[0] + ": " + str(Emeas)
        bmp = int(Bmeas * 1000)
        emp = int(Emeas * 1000)
        key = row[0]
        if key in dictionary.keys():
            current = dictionary[key]
            print key
            print current
            for record in current:
                print bmp
                print emp
                if bmp in record:
                    print "Overlap Measure: " + row[0] + ", bmp: " + str(bmp)
                elif emp in record:
                    print "Overlap Measure: " + row[0] + ", emp: " + str(emp)
            ranger = range((bmp + 1), emp)
            current.append(ranger)
            dictionary[key] = current

        else:
            ranger = range((bmp + 1), emp)
            dictionary[key] = [ranger]


subfilesCS()
measuresCheck()
# localstreets()
# test()
print "that's all folks!"