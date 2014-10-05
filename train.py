import numpy as np
from sklearn import svm, preprocessing


def test(clf, X, y):
  z = clf.predict(X)
  thresh = 1
  for i in xrange(z.shape[0]):
    if z[i] < -thresh:
      z[i] = 0
    elif z[i] > thresh:
      z[i] = 1
    else:
      z[i] = round(z[i])
  diff = np.equal(z, np.round(y))
  correct = float(abs(diff).sum())
  acc = correct/X.shape[0]
  return acc


def train(X, y):
  clf = svm.SVR(kernel='rbf', C=1e3, gamma=0.1)
  clf.fit(X, y)
  return clf


def main():
  train_X = np.load('data/train_X.npy')
  train_y = np.load('data/train_y.npy')
  test_X = np.load('data/test_X.npy')
  test_y = np.load('data/test_y.npy')
  print 'Training examples:', train_X.shape[0]
  print 'Testing examples:', test_X.shape[0]

  preprocessing.scale(train_X, copy=False)
  preprocessing.scale(test_X, copy=False)
  #preprocessing.normalize(X, norm='l2', axis=1, copy=False)

  #print train_y
  clf = train(train_X, train_y)
  train_acc = test(clf, train_X, train_y)
  test_acc = test(clf, test_X, test_y)
  print 'training accuracy', train_acc
  print 'testing accuracy', test_acc



if __name__ == '__main__':
  main()
