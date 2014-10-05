import pickle
import urllib2
import random
import numpy as np
from bs4 import BeautifulSoup
from textblob import TextBlob
#from multiprocessing import Process, Lock, Pool
from threading import Thread, Lock


MONTHS = {'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10}


def parseDatetimeString(s):
  toks = s.split('T')
  date = toks[0]
  time = toks[1]

  return date


def moving_average(a, n=3):
  retval = []
  for i in xrange(n-1, len(a)):
    retval.append(0.0)
    for j in xrange(n):
      retval[-1] += a[i-j]
    retval[-1] /= n
  return retval


def processTicker(ticker, datum, l, train_X, train_y, test_X, test_y):
  print 'Started', ticker
  n = 3
  vals = []
  dates = []
  for i in xrange(len(datum)):
    date, val = datum[i]
    vals.append(val)
    dates.append(date)
  vals = moving_average(vals, n=n)
  dates = dates[:-(n-1)]

  ntail = 4
  for i in xrange(ntail, len(dates)-1):
    r = random.random()
    X = train_X
    y = train_y
    if r < 0.1:
      X = test_X
      y = test_y
    prev_deltas = []
    for j in xrange(ntail):
      prev_deltas.append((vals[i-j]-vals[i-j-1])/vals[i-j-1])
    next_val = vals[i+1]
    val = vals[i]
    date = dates[i]
    delta = (next_val - val)/val
    label = delta*100

    year, month, day = date
    url = 'http://finance.yahoo.com/q/h?s={0}&t={1}-{2}-{3}'.format(ticker, year, month, day)
    try:
      txt = urllib2.urlopen(url, timeout=10).read()
      soup = BeautifulSoup(txt)
    except:
      pass
    if not soup:
      continue
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
    l.acquire()
    X.append([avg_sent] + prev_deltas)
    y.append(label)
    l.release()
  print 'Completed', ticker


def main():
  f = open('data/bak/ticker_data.pickle')
  data = pickle.load(f)
  f.close()

  # X is nxd
  train_X = []
  train_y = []
  test_X = []
  test_y = []
  lock = Lock()
  threads = []
  for idx, (ticker, datum) in enumerate(data['tickers'].items()):
    t = Thread(target=processTicker, args=(ticker, datum, lock, train_X, train_y, test_X, test_y))
    t.start()
    threads.append(t)

  for t in threads:
    t.join()

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
