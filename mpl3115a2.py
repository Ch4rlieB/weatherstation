import time
import psycopg2
import smbus

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

def read_temp_and_presure():
    bus = smbus.SMBus(1)

    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
    time.sleep(1)
    bus.write_byte_data(0x60, 0x26, 0xB9)
    # MPL3115A2 address, 0x60(96)
    # Select data configuration register, 0x13(19)
    #		0x07(07)	Data ready event enabled for altitude, pressure, temperature
    bus.write_byte_data(0x60, 0x13, 0x07)
    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)

    time.sleep(1)

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 6 bytes
    # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 6)

    # Convert the data to 20-bits
    tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    temp = ((data[4] * 256) + (data[5] & 0xF0)) / 16
    altitude = tHeight / 16.0
    cTemp = temp / 16.0
    
    # Negative numbers are in Ones' complement
    if cTemp > 128:
        cTemp = 256 - cTemp
    
    fTemp = cTemp * 1.8 + 32

    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    #		0x39(57)	Active mode, OSR = 128, Barometer mode
    bus.write_byte_data(0x60, 0x26, 0x39)

    time.sleep(1)

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 4 bytes
    # status, pres MSB1, pres MSB, pres LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 4)

    # Convert the data to 20-bits
    pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    pressure = (pres / 4.0) / 100.0
 
    return pressure, altitude, cTemp, fTemp


while True:
    pressure, altitude, cTemp, fTemp = read_temp_and_presure()
    cas = time.strftime("%Y-%m-%d %H:%M:%S")

    logData(conn_string, cTemp, cTemp, 0, pressure, 0, cas, altitude)

    time.sleep(60)
