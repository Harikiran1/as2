# import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Create a connection to a new SQLite database
conn = sqlite3.connect('earthquake_data.db')

# Load earthquake data into a Pandas DataFrame
df = pd.read_csv('all_month.csv')
df.head(5)

# dataframe info
df.info()

# identify missing values
df.isna().mean()*100

# Replace missing values with median
df = df.fillna(df.median())

df.isna().any()

 # Check for duplicates
duplicates = df[df.duplicated()]
print(len(duplicates))
duplicates.head()

# data statistics
df.describe()

# Write the DataFrame to a new table in the SQLite database
df.to_sql('earthquake_data', conn, if_exists='replace', index=False)

cur = conn.cursor()

cur.execute("SELECT SQLITE_VERSION()")
data = cur.fetchone()
print(f"SQLite version: {data[0]}")

# execute the SQL query
cur.execute("SELECT * FROM earthquake_data WHERE mag > 5.0")

# fetch the results
results = cur.fetchall()

# print the results
for row in results:
    print(row)
    
# pip install Flask

from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from flask import Flask, request


app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Earthquake Search</h1>
    <form method="POST" action="/search">
        <label>Magnitude:</label>
        <input type="number" step="0.1" name="magnitude">
        <button type="submit">Search</button>
    </form>
    <form method="POST" action="/week">
        <label>Magnitude:</label>
        <input type="number" step="0.1" name="magnitude">
        <label>Start Date:</label>
        <input type="date" name="start_date">
        <button type="submit">Search</button>
    </form>
    <form method="POST" action="/location">
        <label>Latitude:</label>
        <input type="number" step="0.0001" name="latitude">
        <label>Longitude:</label>
        <input type="number" step="0.0001" name="longitude">
        <label>Distance (km):</label>
        <input type="number" name="distance">
        <button type="submit">Search</button>
    </form>
    <form method="POST" action="/clusters">
        <label>Cluster Size:</label>
        <input type="number" name="cluster_size">
        <button type="submit">Search</button>
    </form>
    <form method="POST" action="/night">
        <label>Start Date:</label>
        <input type="date" name="start_date">
        <button type="submit">Search</button>
    </form>
    '''

@app.route('/search', methods=['POST'])
def search():
    conn = sqlite3.connect('earthquake_data.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM earthquake_data WHERE mag > 5.0")
    count = c.fetchone()[0]
    conn.close()
    return f'<h2>Earthquakes with a magnitude greater than 5.0:</h2><p>{count}</p>'

@app.route('/week', methods=['POST'])
def week():
    magnitude = request.form['magnitude']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = start_date + timedelta(days=7)
    conn = sqlite3.connect('earthquake_data.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM earthquake_data WHERE mag >= ? AND time >= ? AND time < ?", (magnitude, start_date, end_date))
    count = c.fetchone()[0]
    conn.close()
    return f'<h2>Earthquakes with a magnitude of {magnitude} or greater in the week starting on {start_date.date()}:</h2><p>{count}</p>'

@app.route('/location', methods=['POST'])
def location():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    distance = request.form['distance']
    conn = sqlite3.connect('earthquake_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM earthquake_data")
    data = c.fetchall()
    conn.close()
    count = 0
    for row in data:
        lat1, lon1, mag, time = row[1], row[2], row[4], row[0]
        lat2, lon2 = float(latitude), float(longitude)
        R = 6371.0 # approximate radius of the earth in km
        lat1_rad, lat2_rad = radians(lat1), radians(lat2)
        dlat = lat2_rad - lat1_rad
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance_km = R * c
        if distance_km <= float(distance):
            count += 1
    return f'<h2>Earthquakes within {distance} km of ({latitude}, {longitude}):</h2><p>{count}</p>' 


@app.route('/range', methods=['POST'])
def date_range():
    magnitude = request.form['magnitude']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
    conn = sqlite3.connect('earthquake.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM earthquake_data WHERE mag >= ? AND time >= ? AND time <= ?", (magnitude, start_date, end_date))
    count = c.fetchone()[0]
    conn.close()
    return f'<h2>Earthquakes with a magnitude of {magnitude} or greater between {start_date.date()} and {end_date.date()}:</h2><p>{count}</p>'

if __name__ == '__main__':
    app.run()
