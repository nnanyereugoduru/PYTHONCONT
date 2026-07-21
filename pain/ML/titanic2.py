import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import sqlite3
from sklearn.ensemble import RandomForestClassifier
import csv

db_path = r'C:\Projects\FOLDER1\PY1\titanix.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT Sex, Pclass, Age, Fare , Survived FROM train ')
rows = cursor.fetchall()

X_train = np.array([ [row[0], row[1], row[2] if row[2] else 29.7, row[3]] for row in rows])
y_train= np.array([row[4] for row in rows] )

print('x shape', X_train.shape )
print('bincount', np.bincount(y_train))

#X_train, X_test, y_train, y_train = train_test_split(X, y, random_state=42)

model = RandomForestClassifier(class_weight= 'balanced',n_estimators = 100, random_state=42)
model.fit(X_train, y_train)

#predictions = model.predict(X_test)


#print(classification_report(y_test, predictions))

cursor.execute('SELECT PassengerId, Sex, Pclass, Age, Fare FROM test')
test_rows = cursor.fetchall()

test_ids = [row[0] for row in test_rows]
X_test_kaggle = np.array([
    [row[1], row[2],
     row[3] if row[3] else 29.7,
     row[4] if row[4] else 32.2]
    for row in test_rows
])

kaggle_predictions = model.predict(X_test_kaggle)
print(f"predictions made: {len(kaggle_predictions)}")
print(f"predicted survived: {sum(kaggle_predictions)}")
print(f"predicted died: {len(kaggle_predictions) - sum(kaggle_predictions)}")

feature_names = ['Sex', 'Pclass', 'Age', 'Fare']
importances = model.feature_importances_

for name, importance in zip(feature_names, importances):
    print(f"{name:<15}: {importance:.3f}")

conn.close()

with open(r'C:\Projects\FOLDER1\PY1\submission.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Passengerid', 'Survived'])
    for a, b in zip(test_ids, kaggle_predictions):
        writer.writerow([a,b])
print('done')   