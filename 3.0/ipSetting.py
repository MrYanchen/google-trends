'''
Author: MrYanc
Version: 3.5
Date: 11/20/2017
'''
import winreg
import urllib
from bs4 import BeautifulSoup

# internet settings for proxy server setttings
INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 0, winreg.KEY_ALL_ACCESS)
# browser header settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36";

'''
scrape proxy from proxy website
input: none
output: proxy server address list
exception: connection abortion
'''
def proxyList():
	# proxy website url
	proxy_url = "https://www.us-proxy.org/";

	# set browser header
	header = {};
	header['User-Agent'] = USER_AGENT;

	# request
	try:
		request = urllib.request.Request(proxy_url, headers=header);
	except Exception as e:
		raise e;
	else:
		page = urllib.request.urlopen(request).read();
		soup = BeautifulSoup(page, "lxml");
		table = soup.find("tbody");
		proxy = table.find_all("tr");
		# list all the proxy
		ips = [];
		for idx in range(1, len(proxy)):
			ip = proxy[idx];
			tds = ip.findAll("td");
			if(tds[4].contents[0] == 'transparent'):
				temp = tds[0].contents[0]+":"+tds[1].contents[0];
				ips.append(temp);
				pass;
		return ips;

'''
set proxy server setting key
input: name: string, value: string
output: none
exception:
'''	
def set_key(name, value):
	_, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name);
	winreg.SetValueEx(INTERNET_SETTINGS, name, 0, reg_type, value);
	pass;

'''
change proxy server setting
input: address: string
output: none
exception:
'''
def changeIpSetting(address):
	set_key('ProxyEnable', 1);
	set_key('ProxyServer', address);
	pass;