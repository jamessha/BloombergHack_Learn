import blpapi
import datetime
import pickle
from optparse import OptionParser
from threading import Thread, Lock


SESSION_TERMINATED = blpapi.Name("SessionTerminated")
RESPONSE_ERROR = blpapi.Name("responseError")
TICK_DATA = blpapi.Name("tickData")
TIME = blpapi.Name("time")
TYPE = blpapi.Name("type")
VALUE = blpapi.Name("value")
TICK_SIZE = blpapi.Name("size")
COND_CODE = blpapi.Name("conditionCodes")
CATEGORY = blpapi.Name("category")
MESSAGE = blpapi.Name("message")


def parseCmdLine():
  parser = OptionParser(description="Retrieve reference data.")
  parser.add_option("-a",
                    "--ip",
                    dest="host",
                    help="server name or IP (default: %default)",
                    metavar="ipAddress",
                    default="10.8.8.1")
  parser.add_option("-p",
                    dest="port",
                    type="int",
                    help="server port (default: %default)",
                    metavar="tcpPort",
                    default=8194)

  (options, args) = parser.parse_args()

  return options


def printErrorInfo(leadingStr, errorInfo):
  print "%s%s (%s)" % (leadingStr, errorInfo.getElementAsString(CATEGORY),
                       errorInfo.getElementAsString(MESSAGE))


def processMessage(msg):
  data = msg.getElement(TICK_DATA).getElement(TICK_DATA)

  retdata = []
  for item in data.values():
    value = item.getElementAsFloat(VALUE)
    retdata.append(value)
  return retdata


def processResponseEvent(event):
  for msg in event:
    #print msg
    if msg.hasElement(RESPONSE_ERROR):
      printErrorInfo("REQUEST FAILED: ", msg.getElement(RESPONSE_ERROR))
      continue
    return processMessage(msg)


def startSession(session):
  if not session.start():
    print "Failed to connect!"
    return False

  if not session.openService("//blp/refdata"):
    print "Failed to open //blp/refdata"
    session.stop()
    return False

  return True


def sendIntradayTickRequest(session, options):
  refDataService = session.getService("//blp/refdata")
  request = refDataService.createRequest("IntradayTickRequest")

  # only one security/eventType per request
  request.set("security", options['security'])

  # Add fields to request
  request.getElement("eventTypes").appendValue("TRADE")
  request.getElement("eventTypes").appendValue("AT_TRADE")
  request.set("includeConditionCodes", True)

  # All times are in GMT
  request.set("startDateTime", options['startDateTime'])
  request.set("endDateTime", options['endDateTime'])

  print "Sending Request:", request
  session.sendRequest(request)


def eventLoop(session):
  while True:
    # nextEvent() method below is called with a timeout to let
    # the program catch Ctrl-C between arrivals of new events
    event = session.nextEvent(500)
    if event.eventType() == blpapi.Event.PARTIAL_RESPONSE:
      print "Processing Partial Response"
      return processResponseEvent(event)
    elif event.eventType() == blpapi.Event.RESPONSE:
      print "Processing Response"
      return processResponseEvent(event)
    else:
      for msg in event:
        if event.eventType() == blpapi.Event.SESSION_STATUS:
          if msg.messageType() == SESSION_TERMINATED:
            return


def parseTickerList(filepath):
  f = open(filepath, 'r')
  line = f.readline()
  f.close()
  toks = line.split('\r')
  return toks


def queryData(session, year, month, day, hour, ticker, data, lock):
  date = datetime.datetime(year, month, day, hour, 30)
  print 'Querying', ticker, date

  rq_options = {}
  rq_options['startDateTime'] = date
  rq_options['endDateTime'] = date
  rq_options['security'] = '%s US Equity' % ticker

  tick_data = []
  try:
    sendIntradayTickRequest(session, rq_options)
    tick_data = eventLoop(session)
  except Exception as e:
    print 'Exception raised', e
    session.stop()

  if not tick_data:
    return

  avg_val = 0.0
  for val in tick_data:
    avg_val += val
  avg_val /= len(tick_data)

  lock.acquire()
  data['tickers'][ticker].append(((year, month, day, hour), avg_val))
  lock.release()

  print 'Done', ticker, date


def main():
  parseTickerList('ticker_list.txt')
  options = parseCmdLine()

  # Fill SessionOptions
  sessionOptions = blpapi.SessionOptions()
  sessionOptions.setServerHost(options.host)
  sessionOptions.setServerPort(options.port)

  print "Connecting to %s:%d" % (options.host, options.port)

  # Create a Session
  session = blpapi.Session(sessionOptions)

  # Start a Session
  if not session.start():
    print "Failed to start session."
    return

  if not session.openService("//blp/refdata"):
    print "Failed to open //blp/refdata"
    return

  #tickers = ['FB', 'MSFT', 'IBM', 'TWTR', 'AAPL', 'GOOG']
  tickers = parseTickerList('ticker_list.txt')
  data = {}
  data['info'] = 'Provides ticker->[(date, value)]'
  data['tickers'] = {}

  to_query = []
  for ticker in tickers:
    data['tickers'][ticker] = []
    today = datetime.date.today()
    today -= datetime.timedelta(days=1)
    year = 2014
    months = range(8, 10)
    first_weekends = [2, 6]

    ticker_vals = []
    for month, first_weekend in zip(months, first_weekends):
      for day in xrange(1, 31):
        avg_val = 0.0
        nval = 0
        if (day - first_weekend) % 7 == 0 or (day - first_weekend - 1) % 7 == 0:
          continue
        for hour in xrange(13, 20):
          to_query.append((year, month, day, hour, ticker))

  lock = Lock()
  threads = []
  for year, month, day, hour, ticker in to_query:
    t = Thread(target=queryData, args=(session, year, month, day, hour, ticker, data, lock))
    t.start()
    threads.append(t)

  for t in threads():
    t.join()

  #print data
  f = open('data/ticker_data.pickle', 'w+')
  pickle.dump(data, f)
  f.close()

  print 'DONE!'


if __name__ == '__main__':
  main()
