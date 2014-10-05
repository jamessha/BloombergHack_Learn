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


def check_pos_acc(clf, X, y):
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

  acc = num_correct/num_total
  return acc


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
  clf = train(train_X, train_y)
  train_acc = check_acc(clf, train_X, train_y)
  test_acc = check_acc(clf, test_X, test_y)
  print '[total] training accuracy', train_acc
  print '[total] testing accuracy', test_acc

  pos_train_acc = check_pos_acc(clf, train_X, train_y)
  pos_test_acc = check_pos_acc(clf, test_X, test_y)
  print '[positives] training accuracy', pos_train_acc
  print '[positives] testing accuracy', pos_test_acc





if __name__ == '__main__':
  main()
