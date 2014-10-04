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
    r = random.random()
    X = train_X
    y = train_y
    if r < 0.1:
      X = test_X
      y = test_y
    for i in xrange(1, len(datum)):
      _, prev_val = datum[i-1]
      date, val = datum[i]
      delta = (val - prev_val)/prev_val
      thresh = 0.01
      if delta < thresh:
        label = 1
      elif delta > thresh:
        label = 2
      else:
        label = 0


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

      X.append([avg_sent, prev_val, val])
      y.append(label)

  train_X = np.array(train_X)
  train_y = np.array(train_y)

  test_X = np.array(test_X)
  test_y = np.array(test_y)

  np.save('data/train_X.npy', train_X)
  np.save('data/train_y.npy', train_y)
  np.save('data/test_X.npy', test_X)
  np.save('data/test_y.npy', test_y)

  # Calvin examples
  #rss_url = 'http://finance.yahoo.com/rss/headline?s=%s' % ticker
  #feed = feedparser.parse(rss_url)
  #for item in feed['items']:
  #  item['title']


if __name__ == '__main__':
  main()
