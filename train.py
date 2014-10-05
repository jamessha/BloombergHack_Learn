import pickle
import numpy as np
from sklearn import svm, preprocessing


def formatRes(z):
  thresh = 1
  for i in xrange(z.shape[0]):
    if z[i] <= -thresh:
      z[i] = -1
    elif z[i] >= thresh:
      z[i] = 1
    else:
      z[i] = 0


def check_acc(clf, X, y):
  z = clf.predict(X)
  #print X
  formatRes(z)
  formatRes(y)
  #print y
  #print z

  diff = np.equal(z, y)
  correct = float(abs(diff).sum())
  acc = correct/X.shape[0]
  return acc


def check_recall(clf, X, y):
  z = clf.predict(X)
  formatRes(z)
  formatRes(y)
  num_correct = 0.0
  num_total = 0.0
  for i in xrange(y.shape[0]):
    if y[i] == 0:
      continue
    num_total += 1
    #if z[i] != 0:
    if y[i] == z[i]:
      num_correct += 1

  return num_correct/num_total


def check_precision(clf, X, y):
  z = clf.predict(X)
  formatRes(z)
  formatRes(y)
  num_correct = 0.0
  num_total = 0.0
  for i in xrange(y.shape[0]):
    if z[i] == 0:
      continue
    num_total += 1
    if y[i] == z[i]:
      num_correct += 1

  return num_correct/num_total


def train(X, y):
  clf = svm.SVR(kernel='rbf', C=1e3, gamma=0.1)
  #print X
  #print y
  clf.fit(X, y)
  return clf


def preprocess(X):
  #preprocessing.scale(X, copy=False)
  pass

def main():
  train_X = np.load('data/train_X.npy')[:, :]
  train_y = np.load('data/train_y.npy')
  test_X = np.load('data/test_X.npy')[:, :]
  test_y = np.load('data/test_y.npy')
  print 'Training examples:', train_X.shape[0]
  print 'Testing examples:', test_X.shape[0]

  preprocess(train_X)
  preprocess(test_X)

  #print train_y
  print 'Training...'
  clf = train(train_X, train_y)

  print 'Saving...'
  f = open('data/model.pickle', 'w+')
  pickle.dump(clf, f)
  f.close()

  print 'Testing'
  print '============================='
  # correct/total
  train_acc = check_acc(clf, train_X, train_y)
  test_acc = check_acc(clf, test_X, test_y)
  print 'training accuracy', train_acc
  print 'testing accuracy', test_acc
  print

  # correct activations/actual activations
  train_precision = check_precision(clf, train_X, train_y)
  test_precision = check_precision(clf, test_X, test_y)
  print 'training precision', train_precision
  print 'testing precision', test_precision
  print

  # correct activations/should activations
  train_recall = check_recall(clf, train_X, train_y)
  test_recall = check_recall(clf, test_X, test_y)
  print 'training recall', train_recall
  print 'testing recall', test_recall


if __name__ == '__main__':
  main()
