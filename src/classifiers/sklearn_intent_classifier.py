import logging

import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC


class SklearnIntentClassifier(object):
    """Intent classifier using the sklearn framework"""

    def __init__(self, uses_probabilities=True):
        """Construct a new intent classifier using the sklearn framework.

        :param uses_probabilities: defines if the model should be trained
                                           to be able to predict label probabilities
        :type uses_probabilities: bool"""

        self.le = LabelEncoder()
        self.uses_probabilities = uses_probabilities
        self.tuned_parameters = [{'C': [1, 2, 5, 10, 20, 100], 'kernel': ['linear']}]
        self.score = 'f1'
        self.clf = GridSearchCV(SVC(C=1, probability=uses_probabilities),
                                self.tuned_parameters, cv=2, scoring='%s_weighted' % self.score)

    def transform_labels_str2num(self, labels):
        """Transforms a list of strings into numeric label representation.

        :param labels: List of labels to convert to numeric representation
        :type labels: list of str"""

        y = self.le.fit_transform(labels)
        return y

    def transform_labels_num2str(self, y):
        """Transforms a list of strings into numeric label representation.

        :param labels: List of labels to convert to numeric representation
        :type labels: list of str"""

        labels = self.le.inverse_transform(y)
        return labels

    def train(self, X, y):
        """Train the intent classifier on a data set.

        :param X: Train data set
        :param y: Train labels (numeric)"""

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.1, random_state=0)
        self.clf.fit(X_train, y_train)

        # Test the trained model
        logging.info("Score of intent model on test data: %s " % self.clf.score(X_test, y_test))

    def predict_prob(self, X):
        """Given a bow vector of an input text, predict the intent label. Returns probabilites for all labels.

        :param X: bow of input text
        :return: tuple of first, the vector of labels (eother numeric or string) and second vector of probabilities"""

        if hasattr(self, 'uses_probabilities') and self.uses_probabilities:
            return self.clf.predict_proba(X)
        else:
            y_pred = self.clf.predict(X)
            return y_pred, np.full(y_pred.shape, 1.0 / len(y_pred))

    def predict(self, X):
        """Given a bow vector of an input text, predict most probable label. Returns only the most likely label.

        :param X: bow of input text
        :return: tuple of first, the most probable label and second, its probability"""

        pred_result = self.predict_prob(X)
        max_indicies = np.argmax(pred_result, axis=1)
        # retrieve the index of the intent with the highest probability
        max_values = pred_result[:, max_indicies].flatten()
        return max_indicies, max_values
