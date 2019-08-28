#!/usr/bin/python

import sys
import pickle
import pprint
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.model_selection import cross_val_score

sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from data_scrubber import scrub_data

from sklearn.model_selection import train_test_split

# Load Raw dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 1: Select what features you'll use.
# features determined from data exploration
features_list = ['poi', 'exercised_stock_options', 'bonus', 'expenses', 'salary']

# Save features_list
with open("my_feature_list.pkl", "w") as data_file:
    pickle.dump(features_list, data_file)

### Task 2: Remove outliers
### Task 3: Create new feature(s)
# Scrub dataset
_, my_dataset = scrub_data(data_dict, features_list)

# Pickle scrubbed_data
with open("my_dataset.pkl", "w") as data_file:
    pickle.dump(my_dataset, data_file)

### Task 4: Try a variety of classifiers
# Dataset loading, scaling has been moved to pipelines
data = featureFormat(my_dataset, features_list)
labels, features = targetFeatureSplit(data)
features_train, features_test, labels_train, labels_test = train_test_split(features, labels, test_size=0.3, random_state=42)

##
## K-NN
##
clf_knn = make_pipeline(StandardScaler(), KNeighborsClassifier())
clf_knn.fit(features_train, labels_train)
knn_score_0 = clf_knn.score(features_test, labels_test)
print("Stock configuration K-NN mean accuracy: {}".format(knn_score_0))

##
## SVM
##
clf_svm = make_pipeline(StandardScaler(), SVC())
clf_svm.fit(features_train, labels_train)
svm_score_0 = clf_svm.score(features_test, labels_test)
svm_score_0 = clf_svm.score(features_test, labels_test)
print("Stock configuration SVM mean accuracy: {}".format(svm_score_0))

##
## Linear Regression
##
clf_lr = make_pipeline(StandardScaler(), LinearRegression())
clf_lr.fit(features_train, labels_train)
lr_score_0 = clf_lr.score(features_test, labels_test)
print("Stock configuration linear coefficient of determination: {}".format(lr_score_0))

clf_pca_lr = make_pipeline(StandardScaler(), PCA(n_components=2), LinearRegression())
clf_pca_lr.fit(features_train, labels_train)
lr_pca_score_0 = clf_lr.score(features_test, labels_test)
print("Stock configuration linear coefficient of determination with PCA(2): {}".format(lr_pca_score_0))

##
## Cross Validation
##
clf_knn = make_pipeline(StandardScaler(), KNeighborsClassifier())
knn_cv_scores = cross_val_score(clf_knn, features, labels, cv=10)
print("stock knn cross validation scores")
print(knn_cv_scores)
print("stock knn accuracy: {:.2f} (+/- {:.2f})".format(knn_cv_scores.mean(), knn_cv_scores.std()*2))

clf_svm = make_pipeline(StandardScaler(), SVC())
svm_cv_scores = cross_val_score(clf_svm, features, labels, cv=10)
print("stock svm cross validation scores")
print(svm_cv_scores)
print("stock svm accuracy: {:.2f} (+/- {:.2f})".format(svm_cv_scores.mean(), svm_cv_scores.std()*2))



### Task 5: Tune your classifier to achieve better than .3 precision 
### Task 6: Dump your classifier, dataset, and features_list 
