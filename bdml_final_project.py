# -*- coding: utf-8 -*-
"""BDML Final Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zfiuczQvR9lI1B0ghC-5W80e2eZwwaA5
"""

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns

from imblearn.over_sampling import SMOTE

"""# Data Loading"""

from google.colab import drive
drive.mount('/content/drive')

# read the data

# note: use your path
!ls /content/drive/'My Drive'/'Big Data Machine Learning'/'complete_data.csv'
df = pd.read_csv("/content/drive/My Drive/Big Data Machine Learning/complete_data.csv")
df

# changing the gender label into binary
# 1 if male, 0 if female
import numpy as np

mapping = {label: idx for idx, label in enumerate(np.unique(df['label']))}
df['label'] = df['label'].map(mapping)
df = df.drop(df[df['label'] == 2].index)
df = df.reset_index().iloc[:,1:23]
df

"""# SMOTE OverSampling"""

# split data
from sklearn.model_selection import train_test_split

X, y = df.iloc[:, :-1].values, df.iloc[:, -1].values

# The classes are heavily skewed we need to solve this issue later.
print('Female', pd.Series(y).value_counts()[0], 'of the dataset')
print('Male', pd.Series(y).value_counts()[1], 'of the dataset')

colors = ["#0101DF", "#DF0101"]

sns.countplot(y, palette=colors)
plt.title('Click Distributions \n (0: Female || 1: Male)', fontsize=14)

sm = SMOTE(ratio='minority', random_state=42)
Xsm, ysm = sm.fit_sample(X, y)

colors = ["#0101DF", "#DF0101"]

sns.countplot(ysm, palette=colors)
plt.title('Click Distributions \n (0: Female || 1: Male)', fontsize=14)

Xsm_train, Xsm_test, ysm_train, y_test = train_test_split(Xsm, ysm, test_size=0.3, random_state=42, stratify=ysm)

# scale data
from sklearn.preprocessing import StandardScaler

sc = StandardScaler()
X_train_std = sc.fit_transform(Xsm_train)
X_test_std = sc.transform(Xsm_test)

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.patches as mpatches

"""# Dimension Reduction and Data Observation"""

# T-SNE Implementation
X_reduced_tsne = TSNE(n_components=2, random_state=42).fit_transform(X_train_std)

# PCA Implementation
X_reduced_pca = PCA(n_components=2, random_state=42).fit_transform(X_train_std)

f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,6))
# labels = ['Male', 'Female']
f.suptitle('Clusters using Dimensionality Reduction', fontsize=14)


blue_patch = mpatches.Patch(color='#0101DF', label='Female')
red_patch = mpatches.Patch(color='#DF0101', label='Male')


# t-SNE scatter plot
ax1.scatter(X_reduced_tsne[:,0], X_reduced_tsne[:,1], c=(ysm_train == 0), cmap='coolwarm', label='Female', linewidths=0.01)
ax1.scatter(X_reduced_tsne[:,0], X_reduced_tsne[:,1], c=(ysm_train == 1), cmap='coolwarm', label='Male', linewidths=0.01)
ax1.set_title('t-SNE', fontsize=14)

ax1.grid(True)

ax1.legend(handles=[blue_patch, red_patch])


# PCA scatter plot
ax2.scatter(X_reduced_pca[:,0], X_reduced_pca[:,1], c=(ysm_train == 0), cmap='coolwarm', label='Female', linewidths=0.01)
ax2.scatter(X_reduced_pca[:,0], X_reduced_pca[:,1], c=(ysm_train == 1), cmap='coolwarm', label='Male', linewidths=0.01)
ax2.set_title('PCA', fontsize=14)

ax2.grid(True)

ax2.legend(handles=[blue_patch, red_patch])

plt.show()

"""# GridSearch and ROC Curve"""

from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.model_selection import cross_val_score

# Implement classifiers

classifiers = {
    "LogisiticRegression": LogisticRegression(),
    "Support Vector Classifier": SVC(),
    "DecisionTreeClassifier": DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier(),
    "KNearest": KNeighborsClassifier()
}

for key, classifier in classifiers.items():
    classifier.fit(X_train_std, ysm_train)
    training_score = cross_val_score(classifier, X_train_std, ysm_train, cv=5)
    print("Classifiers: ", classifier.__class__.__name__, "Has a training score of", round(training_score.mean(), 2) * 100, "% accuracy score")

# Logistic Regression 
log_reg_params = {"penalty": ['l1', 'l2'], 'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}

grid_log_reg = GridSearchCV(LogisticRegression(), log_reg_params)
grid_log_reg.fit(X_train_std, ysm_train)
# Logistic regression with the best parameters
log_reg = grid_log_reg.best_estimator_
grid_log_reg.best_estimator_

# Support Vector Classifier
svc_params = {'C': [0.5, 0.7, 0.9, 1], 'kernel': ['rbf', 'poly', 'sigmoid', 'linear']}
grid_svc = GridSearchCV(SVC(), svc_params)
grid_svc.fit(X_train_std, ysm_train)

# SVC best estimator
svc = grid_svc.best_estimator_
grid_svc.best_estimator_

# DecisionTree Classifier
tree_params = {"criterion": ["gini", "entropy"], "max_depth": list(range(2,4,1)), 
              "min_samples_leaf": list(range(5,7,1))}
grid_tree = GridSearchCV(DecisionTreeClassifier(), tree_params)
grid_tree.fit(X_train_std, ysm_train)

# DecisionTree best estimator
tree_clf = grid_tree.best_estimator_
grid_tree.best_estimator_

# Random Forest
forest_params = {'n_estimators': [200, 500], 'max_features': ['auto', 'sqrt', 'log2'],
                "max_depth": list(range(2,4,1)), 'criterion' :['gini', 'entropy']}
grid_forest = GridSearchCV(RandomForestClassifier(), forest_params)
grid_forest.fit(X_train_std, ysm_train)

# Random Forest best estimator
random_forest = grid_forest.best_estimator_
grid_forest.best_estimator_

# KNearest
knears_params = {"n_neighbors": list(range(2,5,1)), 'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute']}

grid_knears = GridSearchCV(KNeighborsClassifier(), knears_params)
grid_knears.fit(X_train_std, ysm_train)
# KNears best estimator
knears_neighbors = grid_knears.best_estimator_
grid_knears.best_estimator_

# Fitting use the best estimators

log_reg_score = cross_val_score(log_reg, X_train_std, ysm_train, cv=5)
print('Logistic Regression Cross Validation Score: ', round(log_reg_score.mean() * 100, 2).astype(str) + '%')

svc_score = cross_val_score(svc, X_train_std, ysm_train, cv=5)
print('Support Vector Classifier Cross Validation Score', round(svc_score.mean() * 100, 2).astype(str) + '%')

tree_score = cross_val_score(tree_clf, X_train_std, ysm_train, cv=5)
print('DecisionTree Classifier Cross Validation Score', round(tree_score.mean() * 100, 2).astype(str) + '%')

forest_score = cross_val_score(random_forest, X_train_std, ysm_train, cv=5)
print('Random Forest Classifier Cross Validation Score', round(forest_score.mean() * 100, 2).astype(str) + '%')

knears_score = cross_val_score(knears_neighbors, X_train_std, ysm_train, cv=5)
print('Knears Neighbors Cross Validation Score', round(knears_score.mean() * 100, 2).astype(str) + '%')

from sklearn.metrics import roc_curve
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import roc_auc_score

# Create a DataFrame with all the scores and the classifiers names.

log_reg_pred = cross_val_predict(log_reg, X_train_std, ysm_train, cv=5, method="decision_function")

svc_pred = cross_val_predict(svc, X_train_std, ysm_train, cv=5, method="decision_function")

tree_pred = cross_val_predict(tree_clf, X_train_std, ysm_train, cv=5)

forest_pred = cross_val_predict(random_forest, X_train_std, ysm_train, cv=5)

knears_pred = cross_val_predict(knears_neighbors, X_train_std, ysm_train, cv=5)

log_fpr, log_tpr, log_thresold = roc_curve(ysm_train, log_reg_pred)
svc_fpr, svc_tpr, svc_threshold = roc_curve(ysm_train, svc_pred)
tree_fpr, tree_tpr, tree_threshold = roc_curve(ysm_train, tree_pred)
forest_fpr, forest_tpr, forest_threshold = roc_curve(ysm_train, forest_pred)
knear_fpr, knear_tpr, knear_threshold = roc_curve(ysm_train, knears_pred)


def graph_roc_curve_multiple(log_fpr, log_tpr, svc_fpr, svc_tpr, tree_fpr, tree_tpr, forest_fpr, forest_tpr, knear_fpr, knear_tpr):
    plt.figure(figsize=(16,8))
    plt.title('ROC Curve \n Top 5 Classifiers', fontsize=18)
    plt.plot(log_fpr, log_tpr, label='Logistic Regression Classifier Score: {:.4f}'.format(roc_auc_score(ysm_train, log_reg_pred)))
    plt.plot(svc_fpr, svc_tpr, label='Support Vector Classifier Score: {:.4f}'.format(roc_auc_score(ysm_train, svc_pred)))
    plt.plot(tree_fpr, tree_tpr, label='Decision Tree Classifier Score: {:.4f}'.format(roc_auc_score(ysm_train, tree_pred)))
    plt.plot(forest_fpr, forest_tpr, label='Random Forest Classifier Score: {:.4f}'.format(roc_auc_score(ysm_train, forest_pred)))
    plt.plot(knear_fpr, knear_tpr, label='KNears Neighbors Classifier Score: {:.4f}'.format(roc_auc_score(ysm_train, knears_pred)))
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([-0.01, 1, 0, 1])
    plt.xlabel('False Positive Rate', fontsize=16)
    plt.ylabel('True Positive Rate', fontsize=16)
    plt.annotate('Minimum ROC Score of 50% \n (This is the minimum score to get)', xy=(0.5, 0.5), xytext=(0.6, 0.3),
                arrowprops=dict(facecolor='#6E726D', shrink=0.05),
                )
    plt.legend()
    
graph_roc_curve_multiple(log_fpr, log_tpr, svc_fpr, svc_tpr, tree_fpr, tree_tpr, forest_fpr, forest_tpr, knear_fpr, knear_tpr)
plt.show()

"""#Models

###Logistic regression
"""

from sklearn.linear_model import LogisticRegression

# define the logisticRegression parametersn according to GridSearch result
lr = LogisticRegression(C=0.01, class_weight=None, dual=False, 
             fit_intercept=True, intercept_scaling=1, 
             l1_ratio=None, max_iter=100, multi_class='auto', 
             n_jobs=None, penalty='l2', random_state=None, 
             solver='lbfgs', tol=0.0001, verbose=0,
             warm_start=False)
# omit default parameters
# lr = LogisticRegression(C=0.01)

# fit the logistic regression on our scale data
lr.fit(X_train_std, ysm_train)

# predict testing y_lr_predict using X_test, which is the original data before scaling
y_lr_pred = lr.predict(X_test_std)

# draw confusion matrix and compute accuracy rate
from sklearn.metrics import confusion_matrix 
CM_lr = confusion_matrix(y_lr_pred, y_test)   
print ("Confusion Matrix : \n", CM_lr)

from sklearn.metrics import accuracy_score 
print ("Accuracy : ", accuracy_score(y_lr_pred, y_test))

"""###SVC"""

from sklearn.svm import SVC
# define SVC parameters according to GridSearch result
svc_model = SVC(C=1, break_ties=False, cache_size=200, 
       class_weight=None, coef0=0.0, decision_function_shape='ovr', 
       degree=3, gamma='scale', kernel='rbf', max_iter=-1, 
       probability=False, random_state=None,
       shrinking=True, tol=0.001, verbose=False)

# omit default parameters
# svc_model = SVC(cache_size=200)

svc_model.fit(X_train_std, ysm_train)

# predict y_svc_pred usnig the new model 
y_svc_pred = svc_model.predict(X_test_std)

# draw confusion matrix and compute accuracy rate
from sklearn.metrics import confusion_matrix 
CM_svc = confusion_matrix(y_svc_pred, y_test)   
print ("Confusion Matrix : \n", CM_svc)

print ("Accuracy : ", accuracy_score(y_svc_pred, y_test))

"""Reference code: https://www.geeksforgeeks.org/ml-logistic-regression-using-python/

###Decision Tree
"""

# train decision tree model
from sklearn.tree import DecisionTreeClassifier

tree = DecisionTreeClassifier(ccp_alpha=0.0, class_weight=None, criterion='gini',
                       max_depth=3, max_features=None, max_leaf_nodes=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=5, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, presort='deprecated',
                       random_state=None, splitter='best')

tree.fit(X_train_std,ysm_train)

y_pred_tree = tree.predict(X_test_std)

# show Tree confusion matrix and accuracy
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score  

tree_cm = confusion_matrix(y_pred_tree, y_test)
print ("Confusion Matrix : \n", tree_cm)
print ("Accuracy : ", accuracy_score(y_pred_tree, y_test))

"""###Random Forest"""

# train random forest model

from sklearn.ensemble import RandomForestClassifier

forest = RandomForestClassifier(bootstrap=True, ccp_alpha=0.0, class_weight=None,
                       criterion='entropy', max_depth=3, max_features='log2',
                       max_leaf_nodes=None, max_samples=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=1, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, n_estimators=200,
                       n_jobs=None, oob_score=False, random_state=None,
                       verbose=0, warm_start=False)

forest.fit(X_train_std, ysm_train)

y_pred_forest = forest.predict(X_test_std)

# show forest confusion matrix and accuracy
forest_cm = confusion_matrix(y_pred_forest, y_test)
print ("Confusion Matrix : \n", forest_cm)
print ("Accuracy : ", accuracy_score(y_pred_forest, y_test))

"""###KNN"""

from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
                     metric_params=None, n_jobs=None, n_neighbors=3, p=2,
                     weights='uniform') 
knn.fit(X_train_std, ysm_train)
y_knn_pred = knn.predict(X_test_std)

from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
CM_knn = confusion_matrix(y_knn_pred, y_test)   
print ("Confusion Matrix : \n", CM_knn)
print ("Accuracy : ", accuracy_score(y_knn_pred, y_test))

"""###DNN"""

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from keras import regularizers
from keras.regularizers import l2

# first try a single layer network, which should give us a linear model
model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(units=1, input_shape=(20,), 
                                activation='sigmoid'))
###output and input dimensions are 1,21
model.compile(optimizer=tf.keras.optimizers.SGD(),
              loss=tf.keras.losses.BinaryCrossentropy(),
              metrics=[tf.keras.metrics.BinaryAccuracy()])

hist = model.fit(X_train_std, ysm_train, 
                 validation_data=(X_test_std, y_test), 
                 epochs=10, batch_size=20, verbose=1)

from mlxtend.plotting import plot_decision_regions

history = hist.history

fig = plt.figure(figsize=(10, 4))

plt.plot(history['binary_accuracy'], lw=2)
plt.plot(history['val_binary_accuracy'], lw=2)
plt.legend(['Train Acc.', 'Validation Acc.'], fontsize=15)

plt.show()

#adding more layers


model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(units=32, input_shape=(20,), activation='relu'))
model.add(tf.keras.layers.Dense(32, kernel_regularizer=l2(0.01)))
model.add(tf.keras.layers.Dense(units=16, activation='relu'))
model.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))
model.summary()
## compile:
model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate = 0.01), #we tried lr = 0.1, 0.01, 0.005, 0.002, 0.001
              loss=tf.keras.losses.BinaryCrossentropy(),
              metrics=[tf.keras.metrics.BinaryAccuracy()])
## train:
hist = model.fit(X_train_std, ysm_train, 
                 validation_data=(X_test_std, y_test), 
                 epochs=50, batch_size=10, verbose=1) # we tried batch size = 50, 32, 16, 10
## we continue increasing the epochs, there will be a larger difference of  
## training and validation accuracy or loss
history = hist.history

fig = plt.figure(figsize=(10, 4))
ax = fig.add_subplot(1, 2, 1)
plt.plot(history['loss'], lw=4)
plt.plot(history['val_loss'], lw=4)
plt.legend(['Train loss', 'Validation loss'], fontsize=15)
ax.set_xlabel('Epochs', size=15)

ax = fig.add_subplot(1, 2, 2)
plt.plot(history['binary_accuracy'], lw=4)
plt.plot(history['val_binary_accuracy'], lw=4)
plt.legend(['Train Acc.', 'Validation Acc.'], fontsize=15)
ax.set_xlabel('Epochs', size=15)

plt.show()

DNN_Pred= model.predict(X_test_std)
DNN_Pred[DNN_Pred>=0.5] = 1
DNN_Pred[DNN_Pred<0.5] = 0
CM_DNN = confusion_matrix(DNN_Pred, y_test)   
print ("Confusion Matrix : \n", CM_DNN)
print ("Accuracy : ", accuracy_score(DNN_Pred, y_test))

"""###ROC Space"""

log_fpr, log_tpr, log_thresold = roc_curve(y_test, y_lr_pred)
svc_fpr, svc_tpr, svc_threshold = roc_curve(y_test, y_svc_pred)
tree_fpr, tree_tpr, tree_threshold = roc_curve(y_test, y_pred_tree)
forest_fpr, forest_tpr, forest_threshold = roc_curve(y_test, y_pred_forest)
knear_fpr, knear_tpr, knear_threshold = roc_curve(y_test, y_knn_pred)
dnn_fpr, dnn_tpr, dnn_threshold = roc_curve(y_test, DNN_Pred)


def graph_roc_curve_multiple(log_fpr, log_tpr, svc_fpr, svc_tpr, tree_fpr, tree_tpr, forest_fpr, forest_tpr, knear_fpr, knear_tpr, dnn_fpr, dnn_tpr):
    plt.figure(figsize=(16,8))
    plt.title('ROC Sapce \n Top 6 Classifiers', fontsize=18)
    plt.scatter(log_fpr[1], log_tpr[1], label='Logistic Regression Classifier Score: {:.4f}'.format(roc_auc_score(y_test, y_lr_pred)))
    plt.scatter(svc_fpr[1], svc_tpr[1], label='Support Vector Classifier Score: {:.4f}'.format(roc_auc_score(y_test, y_svc_pred)))
    plt.scatter(tree_fpr[1], tree_tpr[1], label='Decision Tree Classifier Score: {:.4f}'.format(roc_auc_score(y_test, y_pred_tree)))
    plt.scatter(forest_fpr[1], forest_tpr[1], label='Random Forest Classifier Score: {:.4f}'.format(roc_auc_score(y_test, y_pred_forest)))
    plt.scatter(knear_fpr[1], knear_tpr[1], label='KNears Neighbors Classifier Score: {:.4f}'.format(roc_auc_score(y_test, y_knn_pred)))
    plt.scatter(dnn_fpr[1], dnn_tpr[1], label='Deep Neuron Network: {:.4f}'.format(roc_auc_score(y_test, DNN_Pred)))
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([-0.01, 1, 0, 1])
    plt.xlabel('False Positive Rate', fontsize=16)
    plt.ylabel('True Positive Rate', fontsize=16)
    plt.annotate('Minimum ROC Score of 50% \n (This is the minimum score to get)', xy=(0.5, 0.5), xytext=(0.6, 0.3),
                arrowprops=dict(facecolor='#6E726D', shrink=0.05),
                )
    plt.legend()
    
graph_roc_curve_multiple(log_fpr, log_tpr, svc_fpr, svc_tpr, tree_fpr, tree_tpr, forest_fpr, forest_tpr, knear_fpr, knear_tpr, dnn_fpr, dnn_tpr)
plt.show()

"""#Our Own Voices"""

ours = pd.read_csv("/content/drive/My Drive/Big Data Machine Learning/our_voices_data.csv")
ours

our_X, our_y = ours.iloc[:, :-1].values, ours.iloc[:, -1].values
our_knn = knn.predict(our_X)
our_dnn = model.predict(our_X)
our_dnn[our_dnn>=0.5] = 1
our_dnn[our_dnn<0.5] = 0

print('True Gender')
print(our_y)
print('KNN Prediction')
print(our_knn)
print('DNN Prediction')
print(our_dnn)

