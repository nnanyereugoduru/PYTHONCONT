import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import sqlite3

db_path = r'C:\Projects\FOLDER1\PY1\pain\movies.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT year, box_office_million, rating FROM movies')
rows = cursor.fetchall()
conn.close()

# build X and y
X = np.array([[row[0], row[1]] for row in rows])  # year, box office
y = np.array([1 if row[2] >= 8 else 0 for row in rows])  # 1 = highly rated

# split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# train
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

# predict
predictions = model.predict(X_test)

# evaluate
print(f"\nAccuracy: {accuracy_score(y_test, predictions):.2f}")
print(classification_report(y_test, predictions))

print("X shape:", X.shape)
print("y distribution:", np.bincount(y))
print(f"Highly rated: {sum(y)} out of {len(y)} movies")
