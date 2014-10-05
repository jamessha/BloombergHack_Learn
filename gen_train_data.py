import pickle
import urllib2
import random
import numpy as np
from bs4 import BeautifulSoup
from textblob import TextBlob


MONTHS = {'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10}


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
      citations = table.find_all('cite')
      item_dates = []
      for item in citations:
        item_date = item.find('span')
        text = item_date.get_text(strip=True)
        toks = text.split()
        item_dates.append((MONTHS[toks[-2]], int(toks[-1][:-1])))

      avg_sent = 0
      num_items = 0
      # 4 useless things at the end
      if len(items) > 4:
        for item_date, item in zip(item_dates, items[:-4]):
          if item_date[0] != month or item_date[1] != day:
            break
          text = item.get_text(strip=True)
          blob = TextBlob(text)
          sent = blob.sentiment.polarity
          avg_sent += sent
          num_items += 1
        if num_items != 0:
          avg_sent /= num_items
      print delta, avg_sent
      X.append([avg_sent, val, prev_val])
      y.append(label)

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
