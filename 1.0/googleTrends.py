from pytrends.request import TrendReq
import pandas as pd
import datetime
import time

pytrend = TrendReq();

def download(keyword, timeframe):
	keyword_list = [];
	keyword_list.append(keyword);
	try:
		# call google trend api
		pytrend.build_payload(kw_list=keyword_list, cat=0, timeframe=timeframe, geo='', gprop='');
		# get the dataframe of interest
		interest = pytrend.interest_over_time();
		print('Finished downloading ' + keyword + ' ' + timeframe);
		time.sleep(1);
	except Exception as e:
		print(keyword + timeframe + ' is going wrong!');
		raise e;
	return interest;
   	
def googleTrends(keyword, directory):
	# create time frame
	time_frame = [];
	for i in range(2004, 2017):
		time_frame.append(str(i)+'-01-01 '+str(i)+'-06-30');
		time_frame.append(str(i)+'-07-01 '+str(i)+'-12-31');

	time_frame.append('2017-01-01 2017-06-30');
	time_frame.append('2017-07-01 '+str(datetime.date.today()));

	result = [];
	# create threads
	for f in time_frame:
		interest = download(keyword, f);
		result.append(interest);

	return result;

def saveSymbol(finished, file, filename):
	for f in finished:
		file = file[file.Symbol != f];
		file.to_excel(filename);

if __name__ == "__main__":
	# test
	# googleTrends('IBM', directory);
	
	filename = "D:/Symbol.xlsx";
	file = pd.read_excel(filename);
	directory = 'D:/Stock';
	finished = [];
	
	for index, row in file.iterrows():
		try:
			print('Start downloading ' + row['Symbol']);
			result = googleTrends(row['Symbol'], directory);
		except Exception as e:
			print(e);
			print('Failed downloading ' + row['Symbol']);
			# delete finished symbol in the file
			saveSymbol(finished, file, filename);
			break;
		except KeyboardInterrupt:
			print('Finished symbol count: ' + str(len(finished)));
			# delete finished symbol in the file
			saveSymbol(finished, file, filename);
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
			print('Finished downloading ' + row['Symbol']);
		