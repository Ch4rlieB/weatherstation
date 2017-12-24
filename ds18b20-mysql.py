import os
import glob
import time
import mysql.connector

conn_string = "host='ip_adresa_serveru' dbname='db_nazev' user='db_user' password='db_password'"

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

time.sleep(20)

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def logData(conn_string, t, tp, th, p, h, dt, cput):
    try:
        conn = mysql.connector.connect(user='db_user_name', password='db_password',
                              host='ip_adresa_serveru',
                              database='db_nazev')
	cur = conn.cursor()
        cur.execute("INSERT INTO weather(temperature, temperature_pressure, temperature_humidity, pressure, humidity, date_time, cpu_temp) VALUES (%s, %s, %s, %s, %s, %s, %s)", (t, tp, th, p, h, dt,cput))
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as err:
        print("Network Unreachable.")

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        cas = time.strftime("%Y-%m-%d %H:%M:%S")
        logData(conn_string, temp_c, temp_c, temp_f, 0, 0, cas, 0)
        return temp_c, temp_f, cas

while True:
 print(read_temp()) 
 time.sleep(60)
