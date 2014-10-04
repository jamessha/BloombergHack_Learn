import pickle
import urllib2
import random
import numpy as np
from bs4 import BeautifulSoup
from textblob import TextBlob


def parseDatetimeString(s):
  toks = s.split('T')
  date = toks[0]
  time = toks[1]

  return date


def moving_average(a, n=3) :
  ret = np.cumsum(a, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return ret[n - 1:] / n


def main():
  f = open('data/ticker_data.pickle')
  data = pickle.load(f)
  f.close()

  # X is nxd
  train_X = []
  train_y = []
  test_X = []
  test_y = []
  for idx, (ticker, datum) in enumerate(data['tickers'].items()):
    print '{0}/{1}'.format(idx+1, len(data['tickers'].keys()))
    n = 3
    vals = []
    dates = []
    for i in xrange(len(datum)):
      date, val = datum[i]
      vals.append(val)
      dates.append(date)
    vals = np.array(vals)
    vals = moving_average(vals, n=n)
    dates = dates[:-(n-1)]

    for i in xrange(1, len(dates)-1):
      r = random.random()
      X = train_X
      y = train_y
      if r < 0.1:
        X = test_X
        y = test_y
      prev_val = vals[i-1]
      next_val = vals[i+1]
      val = vals[i]
      date = dates[i]
      delta = (next_val - val)/val
      thresh = 0.01
      if delta < -thresh:
        label = 0.0
      elif delta > thresh:
        label = 1.0
      else:
        label = (delta + thresh)/2/thresh


      year, month, day = date
      url = 'http://finance.yahoo.com/q/h?s={0}&t={1}-{2}-{3}'.format(ticker, year, month, day)
      soup = BeautifulSoup(urllib2.urlopen(url).read())
      table = soup.find(id='yfncsumtab')
      items = table.find_all('a')
      avg_sent = 0
      # 4 useless things at the end
      if len(items) > 4:
        for item in items[:-4]:
          text = item.get_text(strip=True)
          blob = TextBlob(text)
          sent = blob.sentiment.polarity
          avg_sent += sent
        avg_sent /= (len(items) - 4)

      X.append([avg_sent, val, prev_val])
      y.append(label)

      print (next_val-val)/val, avg_sent

  train_X = np.array(train_X)
  train_y = np.array(train_y)

  test_X = np.array(test_X)
  test_y = np.array(test_y)

  np.save('data/train_X.npy', train_X)
  np.save('data/train_y.npy', train_y)
  np.save('data/test_X.npy', test_X)
  np.save('data/test_y.npy', test_y)

if __name__ == '__main__':
  main()
