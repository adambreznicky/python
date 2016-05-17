
from __future__ import print_function
from arcrest.security import AGOLTokenSecurityHandler
from arcrest.agol import FeatureService
from arcrest.common.filters import LayerDefinitionFilter

if __name__ == "__main__":
    username = ""
    password = ""
    url = "http://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Projects/FeatureServer"
    proxy_port = None
    proxy_url = None
    agolSH = AGOLTokenSecurityHandler(username=username,
                                      password=password)
    fs = FeatureService(
        url=url,
        securityHandler=agolSH,
        proxy_port=proxy_port,
        proxy_url=proxy_url,
        initialize=True)
    result = fs.createReplica(replicaName='TxDOT_Copy',
                              layers=[0],
                              dataFormat="filegdb",
                              out_path="C:\TxDOT\Data")

print( result)


