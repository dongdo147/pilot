import serial
import time

def convert_to_decimal(degree_str, direction):
    if not degree_str or direction not in "NSEW":
        return None
    degrees = float(degree_str[:2 if direction in 'NS' else 3])
    minutes = float(degree_str[2 if direction in 'NS' else 3:])
    decimal = degrees + minutes / 60
    if direction in 'SW':
        decimal *= -1
    return round(decimal, 6)

def connect_humminbird(port='/dev/ttyUSB0', baudrate=4800, timeout=1):
    while True:
        try:
            ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
            print(f"✅ Đã kết nối Humminbird tại {port}")
            return ser
        except serial.SerialException:
            print("🔁 Đang chờ kết nối Humminbird...", end='\r')
            time.sleep(2)

def read_nmea(ser):
    try:
        line = ser.readline().decode('ascii', errors='ignore').strip()
        return handle_nmea_line(line)
    except serial.SerialException:
        print("⚠️ Mất kết nối với Humminbird. Đang chờ kết nối lại...")
        ser.close()
        return None

def handle_nmea_line(line):
    if line.startswith('$INRMC'):
        parts = line.split(',')
        if len(parts) >= 10 and parts[2] == 'A':
            return {
                'type': 'GPS',
                'time': parts[1],
                'lat': convert_to_decimal(parts[3], parts[4]),
                'lon': convert_to_decimal(parts[5], parts[6]),
                'speed': float(parts[7]),
                'heading': float(parts[8])
            }
    elif line.startswith('$INDPT'):
        parts = line.split(',')
        if len(parts) >= 2:
            return {
                'type': 'DPT',
                'depth': float(parts[1])
            }
    elif line.startswith('$INMTW'):
        parts = line.split(',')
        if len(parts) >= 2:
            return {
                'type': 'TEMP',
                'temperature': float(parts[1])
            }
    elif line.startswith('$INHDG'):
        parts = line.split(',')
        if len(parts) >= 2 and parts[1] != '':
            return {
                'type': 'HDG',
                'compass': float(parts[1])
            }
    elif line.startswith('$INHDT'):
        parts = line.split(',')
        if len(parts) >= 2 and parts[1] != '':
            return {
                'type': 'HDT',
                'true_heading': float(parts[1])
            }
    elif line.startswith('$INZDA'):
        parts = line.split(',')
        if len(parts) >= 5 and parts[1] != '':
            return {
                'type': 'TIME',
                'date': f"{parts[2]}/{parts[3]}/{parts[4]}",
                'time': f"{parts[1][:2]}:{parts[1][2:4]}:{parts[1][4:6]}"
            }
    return None
