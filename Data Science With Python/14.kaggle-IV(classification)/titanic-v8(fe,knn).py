import os
import pandas as pd
from sklearn import neighbors
from sklearn import preprocessing
from sklearn import model_selection
from sklearn_pandas import DataFrameMapper

#returns current working directory
os.getcwd()
#changes working directory
os.chdir("C:\\Users\\Algorithmica\\Downloads")

titanic_train = pd.read_csv("train.csv")
titanic_train.shape
titanic_train.info()

titanic_test = pd.read_csv("test.csv")
titanic_test.shape
titanic_test.info()

#merge train and test data
titanic_all = pd.concat([titanic_train, titanic_test], axis=0)
titanic_all.shape
titanic_all.info()

#explore missing data
titanic_all.apply(lambda x : sum(x.isnull()))

#pre-process Embarked
titanic_all.Embarked[titanic_all['Embarked'].isnull()] = 'S'

#pre-process Age
age_imputer = preprocessing.Imputer()
titanic_all[['Age']] = age_imputer.fit_transform(titanic_all[['Age']])

#create family size feature
def size_to_type(x):
    if(x == 1): 
        return 'Single'
    elif(x >= 2 and x <= 4): 
        return 'Small'
    else: 
        return 'Large'
    
titanic_all['FamilySize'] = titanic_all.SibSp + titanic_all.Parch + 1
titanic_all['FamilyType'] = titanic_all['FamilySize'].map(size_to_type)

#process names of passengers
title_Dictionary = {
                        "Capt":       "Officer", "Col":        "Officer",
                        "Major":      "Officer", "Jonkheer":   "Royalty",
                        "Don":        "Royalty", "Sir" :       "Royalty",
                        "Dr":         "Officer", "Rev":        "Officer",
                        "the Countess":"Royalty","Dona":       "Royalty",
                        "Mme":        "Mrs", "Mlle":       "Miss",
                        "Ms":         "Mrs", "Mr" :        "Mr",
                        "Mrs" :       "Mrs", "Miss" :      "Miss",
                        "Master" :    "Master", "Lady" :      "Royalty"
}

def extract_title(name):
    return name.split(',')[1].split('.')[0].strip()

titanic_all['Title'] = titanic_all['Name'].map(extract_title)
titanic_all['Title'] = titanic_all['Title'].map(title_Dictionary)
    
#process ticket feature
def extract_id(ticket):        
        id = ticket.replace('.','').replace('/','').split()[0]
        if not id.isdigit() and len(id) > 0:
            return id.upper()
        else: 
            return 'X'

titanic_all['TicketId'] = titanic_all['Ticket'].map(extract_id)

#process fare column
fare_imputer = preprocessing.Imputer(strategy="median")
titanic_all[['Fare']] = fare_imputer.fit_transform(titanic_all[['Fare']])

titanic_all1 = pd.get_dummies(titanic_all, columns=['Pclass', 'FamilyType', 'Embarked', 'Sex','Title','TicketId'])
type(titanic_all1)
titanic_all1.shape
titanic_all1.info()
titanic_all1.drop(['PassengerId','Name','FamilySize','SibSp','Parch','Ticket','Cabin','Survived'], axis=1, inplace=True)

#scale all the columns with z-scores
mapper = DataFrameMapper([(titanic_all1.columns, preprocessing.StandardScaler())])
scaled_features = mapper.fit_transform(titanic_all1)
type(scaled_features)
titanic_all2 = pd.DataFrame(scaled_features, columns=titanic_all1.columns)

#split titanic data as train and test
X_train = titanic_all2.iloc[0:891]
X_train.shape
X_train.info()
y_train = titanic_all['Survived'].iloc[0:891]

parameter_grid = dict(n_neighbors=[3,4,5,6,7],
                      weights=['uniform','distance'])
knn_estimator = neighbors.KNeighborsClassifier()
knn_grid_estimator = model_selection.GridSearchCV(estimator=knn_estimator, param_grid=parameter_grid, cv=10, verbose=1, n_jobs=10)
knn_grid_estimator.fit(X_train,y_train)
knn_grid_estimator.grid_scores_

X_test = titanic_all2.iloc[891:1309]
#number of features in test data mismatches with train data
titanic_test['Survived'] =knn_grid_estimator.predict(X_test)
titanic_test['Survived'] = titanic_test['Survived'].map(lambda x:int(x))
titanic_test.to_csv("submission.csv", columns=['PassengerId','Survived'], index=False)
