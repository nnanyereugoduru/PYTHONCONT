import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import sqlite3
import csv

db_path = r'C:\Projects\FOLDER1\PY1\IMDB2.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT Runtime, No_of_Votes, Gross, Released_Year, Meta_score, IMDB_Rating FROM movies')
rows = cursor.fetchall()






X = np.array([[row[0], row[1], row[2], row[3], row[4]] for row in rows])
y = np.array([row[5] for row in rows])  # actual rating, not 0/1

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, predictions)

print(f"MAE:  {mae:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"R²:   {r2:.3f}")

feature_names = ['Runtime', 'No_of_Votes', 'Gross', 'Released_Year', 'Meta_score']
importances = model.feature_importances_

for name, importance in zip(feature_names, importances):
    print(f"{name:<15}: {importance:.3f}")


cursor.execute('SELECT Series_Title, IMDB_Rating FROM movies')
titles = [row[0] for row in cursor.fetchall()]

print(f"\n{'Movie':<35} {'Actual':>8} {'Predicted':>10} {'Error':>8}")
print(f"{'':=<65}")
for i in range(15):
    error = abs(y_test[i] - predictions[i])
    idx = list(y_test).index(y_test[i])
    print(f"{str(i):<35} {y_test[i]:>8.1f} {predictions[i]:>10.2f} {error:>8.3f}")

conn.close()

# Runtime, No_of_Votes, Gross, Released_Year, Meta_score
new_movie = np.array([[148, 2067042, 292576195, 2010, 74]])  # Inception's actual stats
predicted_rating = model.predict(new_movie)
print(f"Predicted rating: {predicted_rating[0]:.2f}")
print(f"Actual rating: 8.8")

# Project Hail Mary (2026)
# Runtime, No_of_Votes, Gross, Released_Year, Meta_score
new_movie = np.array([[156, 500000, 675800000, 2026, 85]])
predicted_rating = model.predict(new_movie)
print(f"Predicted rating: {predicted_rating[0]:.2f}")
print(f"Actual IMDB rating: 8.3")