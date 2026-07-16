import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import sqlite3

db_path = r'C:\Projects\FOLDER1\PY1\IMDB2.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT  No_of_Votes, Gross, Released_Year, Meta_score, IMDB_Rating FROM movies')
rows = cursor.fetchall()
conn.close()

X = np.array([[row[0], row[1], row[2], row[3]] for row in rows])
y = np.array([1 if row[4] >= 8.2 else 0 for row in rows])

print("X shape:", X.shape)
print("y distribution:", np.bincount(y))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(class_weight= 'balanced', random_state=42)
model.fit(X_train, y_train)

predictions = model.predict(X_test)

print(f"\nAccuracy: {accuracy_score(y_test, predictions):.2f}")
print(classification_report(y_test, predictions))

feature_names = ['No_of_Votes', 'Gross', 'Released_Year', 'Meta_score']
importances = model.feature_importances_

for name, importance in zip(feature_names, importances):
    print(f"{name:<15}: {importance:.3f}")