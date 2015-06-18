__file__ = 'test2'
__date__ = '12/16/2014'
__author__ = 'ABREZNIC'
import tpp, os
workspace = "C:\\TxDOT\\Projects\\IRI_dan\\test\\Wrkg2014_12_16.gdb"
rhino_lines = workspace + os.sep + "rhinolines"
tpp.rte_order(rhino_lines, "ROUTE_ID", "FRM_DFO")
print "that's all folks!"