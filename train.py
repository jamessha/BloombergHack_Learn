import numpy as np
from sklearn import svm, preprocessing


def test(clf, X, y):
  z = clf.predict(X)
  diff = z - y
  errors = sum(abs(diff))
  acc = 1 - errors/X.shape[0]
  return acc


def train(X, y):
  clf = svm.SVC()
  clf.fit(X, y)
  return clf


def main():
  X = np.load('data/train_X.npy')
  y = np.load('data/train_y.npy')

  preprocessing.scale(X, copy=False)
  #preprocessing.normalize(X, norm='l2', axis=1, copy=False)

  clf = train(X, y)
  acc = test(clf, X, y)
  print 'training accuracy', acc


if __name__ == '__main__':
  main()
