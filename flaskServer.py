from flask import Flask, render_template
import sqlite3
import time
from grovepi import *

app = Flask(__name__)

# Connect the DHT11 sensor to port D4
dht_sensor_port = 4
dht_sensor_type = 0  # DHT11

# Create and connect to the SQLite database
conn = sqlite3.connect('dht11_data.db', check_same_thread=False)
cursor = conn.cursor()

# Create the 'data' table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS data
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,formatted_timestamp TEXT, temperature REAL, humidity REAL)''')
conn.commit()

@app.route('/')
def index():
    # Query the last 10 data points from the database
    cursor.execute('SELECT * FROM data ORDER BY formatted_timestamp DESC')
    data = cursor.fetchall()

    # Convert epoch time to formatted string
    formatted_data = []
    for row in data:
        formatted_time = time.strftime("%Y-%m-%d %A %H:%M:%S", time.localtime(float(row[1])))
        formatted_data.append((row[0], formatted_time, row[2], row[3] , row[4]))

    # Render the data in an HTML template
    return render_template('index.html', data=formatted_data)

def read_sensor_data():
    lock = threading.Lock()
    while True:
        try:
            # Read data from the DHT11 sensor
            [formatted_timestamp,temperature, humidity] = dht(dht_sensor_port, dht_sensor_type)
            lock.acquire(True)
            # Insert the data into the SQLite database
            cursor.execute('INSERT INTO data (formatted_timestamp, temperature, humidity) VALUES (?, ?, ?)',
                           (int(time.time()), temp, humidity))
            conn.commit()

            # Wait for 1 second before reading the data again
            time.sleep(1)

        except IOError:
            lock.release()
            print("Error")

if __name__ == '__main__':
    # Start reading sensor data in a separate thread
    from threading import Thread
    sensor_thread = Thread(target=read_sensor_data)
    sensor_thread.daemon = True
    sensor_thread.start()

    # Start the Flask server
    app.run(debug=True)