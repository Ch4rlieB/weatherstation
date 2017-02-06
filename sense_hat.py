import os
import psycopg2
import time
from sense_hat import SenseHat

def get_cpu_temperature():
  res = os.popen('vcgencmd measure_temp').readline()
  return(res.replace("temp=","").replace("'C\n",""))

def log_data(t, tp, th, p, h, cput, dt):
  try:
    conn = psycopg2.connect("host='ip_adresa_serveru' dbname='db_nazev' user='db_user' password='db_password'")
    cur = conn.cursor()
    cur.execute("insert into weather(sense_hat_temperature, sense_hat_temperature_pressure, sense_hat_temperature_humidity, sense_hat_pressure, sense_hat_humidity, sense_hat_cputemp, date_time) values(%s, %s, %s, %s, %s, %s, %s)", (t, tp, th, p, h, cput, dt))
    conn.commit()
    cur.close()
    conn.close()
  except psycopg2.OperationalError:
    print("Network Unreachable.")


sense = SenseHat()

while True:
  sense.clear()

# temperature must be corrected
# https://www.raspberrypi.org/forums/viewtopic.php?f=104&t=111457
  t = sense.get_temperature()
  cpu = get_cpu_temperature()
  cpu_int = int(float(cpu))
  tc = t - ((cpu_int - t)/ 1.5)

  h = sense.get_humidity()
  hc = h * (2.5 - 0.029 * tc)

  tp = sense.get_temperature_from_pressure()
  th = sense.get_temperature_from_humidity()
  p = sense.get_pressure()

  cas = time.strftime("%Y-%m-%d %H:%M:%S")
  
  log_data(tc, tp, th, p, h, cpu, cas)

  msg = "Temperature = %s, TempPressure = %s, TempHumidity = %s, Pressure = %s, Humidity = %s" % (tc,tp,th,p,hc)  
  sense.show_message(msg, scroll_speed=0.05)

