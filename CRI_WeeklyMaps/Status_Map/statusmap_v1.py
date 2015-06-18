from sharepoint import SharePointSite, basic_auth_opener
server_url = r'https://txdot.sharepoint.com/'
site_url = server_url + r'sites/division-tpp/MAD/SitePages/Home.aspx'

opener = basic_auth_opener(server_url, "adam.breznicky@txdot.gov", "")
site = SharePointSite(site_url, opener)
print "we're in"
for sp_list in site.lists:
	print sp_list.id, sp_list.meta['Title']
	print site.lists
	
print "boobs"
