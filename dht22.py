import subprocess
import re
import time
import psycopg2

# number of gpio pin with connected dht-22
gpio = "7"

conn_string = "host='ip_adresa_serveru' dbname='db_nazev' user='db_user' password='db_password'"

def logData(conn_string, t, tp, th, p, h, dt, cput):
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        cur.execute("insert into weather(temperature, temperature_pressure, temperature_humidity, pressure, humidity, date_time, cpu_temp) values(%s, %s, %s, %s, %s, %s, %s)", (t, tp, th, p, h, dt,cput))
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.OperationalError:
        print("Network Unreachable.")

def read_temp_and_humidity(gpio):
    # https://github.com/adafruit/Adafruit_Python_DHT
    #adafruit = "/home/pi/Adafruit_Python_DHT/examples/AdafruitDHT.py"
    adafruit = "path to AdafruitDHT.py located in examples"

    sensorReadings = subprocess.check_output(['sudo','python',adafruit,"22",gpio])

    try:
        # try to read neagtive numbers
        temperature = re.findall(b"Temp=(-\d+.\d+)", sensorReadings)[0]
    except: 
        # if negative numbers caused exception, they are supposed to be positive
        try:
            temperature = re.findall(b"Temp=(\d+.\d+)", sensorReadings)[0]
        except:
            pass
    humidity = re.findall(b"Humidity=(\d+.\d+)", sensorReadings)[0]
    intTemp = float(temperature)
    intHumidity = float(humidity)

    return intTemp, intHumidity


while True:
    temperature, humidity = read_temp_and_humidity(gpio))
    cas = time.strftime("%Y-%m-%d %H:%M:%S")
    logData(conn_string, temperature, 0, temperature, 0, humidity, cas, 0) 

    time.sleep(60)
