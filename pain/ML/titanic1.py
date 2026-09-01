import pandas as pd
import sqlite3
import numpy as np

df = pd.read_csv(r'C:\Projects\FOLDER1\PY1\train.csv')
df1 = pd.read_csv(r'C:\Projects\FOLDER1\PY1\gender_submission.csv')
df2 = pd.read_csv(r'C:\Projects\FOLDER1\PY1\test.csv')

conn = sqlite3.connect(r'C:\Projects\FOLDER1\PY1\titanix.db')
df['Sex'] = np.where(df['Sex'] == 'female', 1, 0)
df2['Sex'] = np.where(df2['Sex'] == 'female', 1, 0)

df['Embarked'] = df["Embarked"].map({"S":1, "Q": 2, "C": 3})
df2['Embarked'] = df["Embarked"].map({"S":1, "Q": 2, "C": 3})



df.to_sql('train', conn, if_exists='replace', index=False)
df1.to_sql('genderS', conn, if_exists='replace', index=False)
df2.to_sql('test', conn, if_exists='replace', index=False)

conn.commit()
conn.close()

