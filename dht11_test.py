from datetime import datetime
import sqlite3
from grovepi import *

# Connect the DHT11 sensor to port D4
dht_sensor_port = 4
dht_sensor_type = 0  # Use 0 for DHT11 sensor

#connect the capacitive moisture snsor to port A0 
moisture_sensor_port=0



#connection to SQLite database
conn = sqlite3.connect('dht11_data.db')
cursor = conn.cursor()

#cursor.execute('ALTER TABLE data ADD COLUMN moisture INTEGER')

while True:
    try:
        [temperature, humidity] = dht(dht_sensor_port, dht_sensor_type)
        moisture = analogRead(moisture_sensor_port)
        dt = datetime.fromtimestamp(time.time())
        formatted_timestamp = dt.strftime("%Y-%m-%d %A %H:%M:%S")
        cursor.execute('INSERT INTO data (formatted_timestamp, temperature, humidity,moisture) VALUES (?, ?, ?,?)', (int(time.time()), temperature, humidity,moisture))
        conn.commit() 
        print("Timestamp:", formatted_timestamp,"Temperature:", temperature, "Humidity:", humidity, "Moisture:", moisture)
        time.sleep(300)
    except IOError as e:
        print("Error:", str(e))

#close the db connection
conn.close()
