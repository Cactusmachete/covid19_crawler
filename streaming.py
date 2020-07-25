"""
Ahilya Sinha 2016009
Anushika Verma 2016015
BDA Assignment 3
"""
import tweepy
import time
import random
import matplotlib.pyplot as plt

# insert your own keys below.
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""


class MyStreamListener(tweepy.StreamListener):

    def __init__(self, interval_, number_list_):
        super(MyStreamListener, self).__init__()
        self.count = 0
        self.start = time.time()
        self.interval = interval_
        self.buffer = [0]*10000
        self.prev_interval_end = time.time()
        self.surprise_numbers = number_list_
        self.total_tweets_seen = 0

    def on_status(self, status):
        self.total_tweets_seen+=1
        curr_time = time.time() - self.start
        interval_time = time.time() - self.prev_interval_end

        if(interval_time>=self.interval):
            # if 10 minutes have passed, find the surprise number
            self.prev_interval_end = time.time()
            self.surprise_numbers.append(self.AMS(self.buffer))

        if(curr_time>=2400 and len(self.surprise_numbers)==4):
            # stop streaming if 40 minutes are up.
            return False

        elif self.count>=10000:
            # Reservoir Sampling if current buffer is already full
            val = random.randrange(self.count+1)
            if val<10000:
                self.buffer[val] = status.author.statuses_count
                self.count+=1

        else:
            self.buffer[self.count] = status.author.statuses_count
            self.count+=1


    def on_error(self, status):
        print(status)
        if status == 420:
            print("Tried reconnecting too soon :(")
            return False
        sys.exit()


    def AMS(self, stream):
        num_samples = int(len(stream)/10)
        index = []
        for i in range(len(stream)):
            index.append(i)
        random.shuffle(index)
        sample_indexes = sorted(index[:num_samples])

        dic = {}
        for i in range(len(stream)):
            if i in sample_indexes:
                if not dic.get(stream[i]):
                    dic[stream[i]] = 0
                dic[stream[i]] += 1

        return int(len(stream) / float(len(dic)) * sum((2 * v - 1) for v in dic.values()))


def make_graphs(surprise_numbers_list):
    min_10 = [] ; min_20 = [] ; min_30 = [] ; min_40 = []; y = []
    for ls in surprise_numbers_list:
        min_10.append(ls[0])
        min_20.append(ls[1])
        min_30.append(ls[2])
        min_40.append(ls[3])

    for i in range(len(surprise_numbers_list)):
        y.append(i+1)

    plt.plot(y, min_10, label = "10 minute intervals", linestyle='dashed', marker='o')
    plt.plot(y, min_20, label = "20 minute intervals", linestyle='dashed', marker='o')
    plt.plot(y, min_30, label = "30 minute intervals", linestyle='dashed', marker='o')
    plt.plot(y, min_40, label = "40 minute intervals", linestyle='dashed', marker='o')
    plt.ylabel('surprise number')
    plt.xlabel('sample number')
    plt.legend()
    plt.show()

    min_10_avg = sum(min_10)/len(surprise_numbers_list)
    min_20_avg = sum(min_20)/len(surprise_numbers_list)
    min_30_avg = sum(min_30)/len(surprise_numbers_list)
    min_40_avg = sum(min_40)/len(surprise_numbers_list)
    averages = [min_10_avg, min_20_avg, min_30_avg, min_40_avg]
    y_bar = [10, 20, 30, 40]

    plt.plot(y_bar, averages, label = "average surprise number", linestyle='dashed', marker='o')
    plt.ylabel('surprise number')
    plt.xlabel('minutes')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    surprise_numbers_list = []

    for i in range(15):
        done = 0
        while not done:
            try:
                ls = []
                stream_listener = MyStreamListener(600, ls)
                stream = tweepy.Stream(auth = api.auth, listener=stream_listener)
                stream.filter(track=['#covid19', '#coronavirus', '#covid'])
                surprise_numbers_list.append(ls)
                done = 1

            except Exception as e:
                print(e)
                pass

    make_graphs(surprise_numbers_list)
