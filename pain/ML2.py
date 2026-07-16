import pandas as pd
import sqlite3

df = pd.read_csv(r'C:\Projects\FOLDER1\PY1\imdb_top_1000.csv')

df = df.drop(columns = ['Poster_Link', 'Overview', 'Certificate' ])

df['Runtime'] = df['Runtime'].str.replace("min",'').astype(int)
df['Gross'] = df['Gross'].str.replace(',','').astype(float)
df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
df= df.dropna()

print(f"rows after cleaning: {len(df)}")


conn = sqlite3.connect(r'C:\Projects\FOLDER1\PY1\IMDB2.db')
df.to_sql('MOVIES', conn, if_exists='replace', index=False)
conn.commit()
conn.close()
#print(f"done - {len(df)} rows loaded")
#print(df.shape)
#print(df.columns.tolist())
#print(df.head(2))
#print(df.dtypes)


