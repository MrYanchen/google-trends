import threading
from pytrends.request import TrendReq
import pandas as pd
import datetime
import time
import requests

result = [];
finished = [];
result_lock = threading.Lock();
request_lock = threading.Lock();

class myThread (threading.Thread):

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

        interest = self.download(keyword_list);
        # global result
        global result;
        try:
            result_lock.acquire();
            # add interest to result list
            result.append(interest);
            print("Thread "+str(self.count)+" "+self.timeframe+" is finished.");
        finally:
            result_lock.release();

    def download(self, keyword_list):
        try:
            # call google trend api
            self.pytrend.build_payload(kw_list=keyword_list, cat=0, timeframe=self.timeframe, geo='', gprop='');

        except (Exception, OSError, requests.ConnectionError) as e:
            print("Thread "+str(self.count)+" "+self.timeframe+" goes wrong.");
            print(e);
            print("Retry downloading "+"Thread "+str(self.count)+" "+self.timeframe);
            try:
                request_lock.acquire();
                time.sleep(10);
                interest = self.download(keyword_list);
                return interest;
            finally:
                request_lock.release();
        else:
            # get the dataframe of interest
            interest = self.pytrend.interest_over_time();
            return interest;
        finally:
            pass;

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

def main(filename, file, directory):
    for index, row in file.iterrows():
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

if __name__ == "__main__":
    filename = "D:/Symbol.xlsx";
    file = pd.read_excel(filename);
    directory = 'D:/Stock';
    
    # test
    # test(directory);

    # main
    main(filename, file, directory);  
    