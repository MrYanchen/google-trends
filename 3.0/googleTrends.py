'''
Authon: MrYanc
Version: 3.5
Date: 11/17/2017
'''

import threading
from pytrends.request import TrendReq
import pandas as pd
import datetime
import time
import requests
import random
import os
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
			if(tds[4].contents[0] == 'elite proxy'):
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

# result list to store each download dataframe of every stock
result = [];
# the finished list to store finished stock symbol
finished = [];
result_lock = threading.Lock();
sema = threading.Semaphore(5);

class myThread(threading.Thread):

	def __init__(self, keyword, timeframe, count):
		threading.Thread.__init__(self);
		# python google trend tool
		self.pytrend = TrendReq();
		# search keyword
		self.keyword = keyword;
		# start time
		self.timeframe = timeframe;
		# thread count
		self.count = count;
		print("Thread "+str(self.count)+" "+self.timeframe+" is starting.");
		
	def run(self):
		# create keyword list
		keyword_list = [];
		keyword_list.append(self.keyword);
		
		# random select sleep time
		sleep_time = random.randint(5, 10);
		# time sleep between each request
		with sema:
			interest = self.download(keyword_list);
			time.sleep(sleep_time);

		# global result
		global result;
		try:
			result_lock.acquire();
			# add interest to result list
			result.append(interest);
			print("Thread "+str(self.count)+" "+self.timeframe+" is finished.");
		finally:
			result_lock.release();

	'''
	input: search keyword list: string list
	output: interest dataframe
	exception: connection abortion
	'''
	def download(self, keyword_list):
		try:
			# call google trend api
			self.pytrend.build_payload(kw_list=keyword_list, cat=0, timeframe=self.timeframe, geo='', gprop='');

		except (Exception, OSError, requests.ConnectionError) as e:
			print("Thread "+str(self.count)+" "+self.timeframe+" goes wrong.");
			print(e);
			print("Retry downloading "+"Thread "+str(self.count)+" "+self.timeframe);
			# random select sleep time
			sleep_time = random.randint(10, 30);
			time.sleep(sleep_time);
			interest = self.download(keyword_list);
			return interest;
		else:
			# get the dataframe of interest
			interest = self.pytrend.interest_over_time();
			return interest;
		finally:
			pass;

'''
input: search keyword: string; file directory: string
output: dataframe list
exception: connection abortion
'''
def googleTrends(keyword, directory):
	# create time frame
	time_frame = [];
	for i in range(2004, 2017):
		time_frame.append(str(i)+'-01-01 '+str(i)+'-06-30');
		time_frame.append(str(i)+'-07-01 '+str(i)+'-12-31');

	time_frame.append('2017-01-01 2017-06-30');
	time_frame.append('2017-07-01 '+str(datetime.date.today()));
	# create threads list
	threads = [];
	# thread counter
	cnt = 0;

	global result;
	result = [];
	# create threads
	for f in time_frame:
		thread = myThread(keyword, f, cnt);
		threads.append(thread);
		cnt = cnt + 1;

	# start thread
	counter = 1;
	for t in threads:
		if(counter % 5 == 0):
			time.sleep(1);
		counter = counter + 1;
		t.start();

	# finish thread work
	for t in threads:
		t.join();

'''
input: directory: string
output: csv file
exception:
'''
def test(directory):
	name = 'AACE';
	googleTrends(name, directory);
	# convert result list to dataframe
	df = pd.concat(result);
	# sort on date
	df = df.sort_index();
	# save to file directory
	df.to_csv(directory+'/'+name+'.csv');
	print('Finished downloading '+name);
	# googleTrends('AAPL', directory);
	# googleTrends('AMZN', directory);

'''
input: filename: string; file: dataframe; directory: string
output: csv file
exception:
'''
def main(filename, file, directory):
	ips = proxyList();
	print("Proxy server length: "+str(len(ips)));

	# count for file and proxy list
	file_cnt = 1;
	ips_cnt = 0;
	
	for index, row in file.iterrows():
		if(file_cnt % 55 == 0):
			if(ips_cnt >= len(ips)):
				break;
			changeIpSetting(ips[ips_cnt]);
			ips_cnt = ips_cnt + 1;
		try:
			print('Start downloading '+row['Symbol']);
			googleTrends(row['Symbol'], directory);
		except KeyboardInterrupt:
			print('Finished symbol count: '+str(len(finished)));
			# delete finished symbol in the file
			for f in finished:
				file = file[file.Symbol != f];
				file.to_excel(filename);
			break;
		else:
			# convert result list to dataframe
			df = pd.concat(result);
			# sort on date
			df = df.sort_index();
			# save finished keyword to finished list
			finished.append(row['Symbol']);
			# save to file directory
			df.to_csv(directory+'/'+row['Symbol']+'.csv');
			print('Finished downloading '+row['Symbol']);
			file_cnt = file_cnt + 1;

# main thread
if __name__ == "__main__":
	# input file
	filename = "Symbol.xlsx";
	filepath = os.path.join(os.getcwd(), filename);
	file = pd.read_excel(filepath);
	
	# output directory
	directory = os.path.join(os.getcwd(), 'Stock');
	if(not os.path.exists(directory)):
		os.makedirs(directory);
	
	# test
	# test(directory);

	# main
	main(filename, file, directory);  
	