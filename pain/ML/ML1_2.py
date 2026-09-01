import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import sqlite3


db_path = r'C:\Projects\FOLDER1\PY1\pain\movies.db'

c = sqlite3.connect(db_path)
cursor = c.cursor()

cursor.execute('SELECT rating, year, box_office_million FROM movies')
rows = cursor.fetchall()
c.close()

x = np.array([[row[0], row[1]] for row in rows])
y = np.array([1 if row[2] >= 500 else 0 for row in rows])

x_train, x_test, y_train, y_test  = train_test_split(x, y , test_size= 0.2, random_state= 50)

print(f"Training samples; {len(x_train)}")
print(f"Test samples: {len(x_test)}")

model = DecisionTreeClassifier(random_state= 50)
model.fit(x_train, y_train)

pred = model.predict(x_test)

print()

print(f"Accuracy {accuracy_score(y_test, pred)}")
print(classification_report(y_test, pred))

print()