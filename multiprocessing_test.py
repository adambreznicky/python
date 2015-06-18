__date__ = '8/1/2014'
__author__ = 'ABREZNIC'
import arcpy, multiprocessing

txdotroads = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
txdotsubs = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"

check1 = "true"
check2 = "true"

def routes():
    cursor = arcpy.SearchCursor(txdotroads)
    for row in cursor:
        print row.RTE_ID
    del cursor
    del row
    return

def subfile():
    counter = 0
    cursor = arcpy.SearchCursor(txdotsubs)
    for row in cursor:
        counter += 1
        thousand = counter/1000
        if isinstance(thousand, int):
            print str(counter)
    del cursor
    del row
    return

if __name__ == '__main__':
    jobs = []
    procs = []
    if check1 == "true":
        jobs.append(routes)
    if check2 == "true":
        jobs.append(subfile)

    for i in jobs:
        p = multiprocessing.Process(target=i)
        p.start()
        procs.append(p)
    for n in procs:
        # p = multiprocessing.Process(target=n)
        n.join()


    print "that's all folks!"