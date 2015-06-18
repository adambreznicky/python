from haufe.sharepoint import Connector
url = r'https://txdot.sharepoint.com/sites/division-tpp/MAD/_layouts/viewlsts.aspx?BaseType=0'
username = r'Adam.Breznicky@txdot.gov'
password = ""
list_id = r'0AEF97F0-027F-4D1C-A58C-A0784CE141C5'
service = Connector(url, username, password, list_id)

fields = service.model
print fields