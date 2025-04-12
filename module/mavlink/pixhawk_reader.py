# module/pixhawk_reader.py

from pymavlink import mavutil
import time

def connect_pixhawk(device='/dev/serial0', baudrate=57600, timeout=10):
    print("⏳ Đang kết nối tới Pixhawk...")
    master = mavutil.mavlink_connection(device, baud=baudrate)

    # Chờ HEARTBEAT trong tối đa `timeout` giây
    start_time = time.time()
    while True:
        try:
            master.wait_heartbeat(timeout=1)
            break
        except:
            elapsed = time.time() - start_time
            print("❌ Chưa kết nối được với Pixhawk... đang chờ...", end='\r')
            if elapsed > timeout:
                print("\n⚠️ Không tìm thấy Pixhawk sau", timeout, "giây.")
                return None
            time.sleep(1)

    print("✅ Nhận HEARTBEAT rồi nè!")
    print(f"  System ID: {master.target_system}, Component ID: {master.target_component}")
    return master


def read_data(master):
    if master is None:
        return None

    msg = master.recv_match(blocking=True)
    if not msg:
        return None

    msg_type = msg.get_type()
    data = msg.to_dict()

    if msg_type == "GPS_RAW_INT":
        return {
            "type": "gps",
            "lat2": data["lat"] / 1e7,
            "lon2": data["lon"] / 1e7,
            "alt2": data["alt"] / 1000.0
        }

    elif msg_type == "ATTITUDE":
        return {
            "type": "attitude",
            "roll": data["roll"],
            "pitch": data["pitch"],
            "yaw": data["yaw"]
        }

    elif msg_type == "SYS_STATUS":
        return {
            "type": "battery",
            "voltage": data["voltage_battery"] / 1000.0,
            "current": data["current_battery"] / 100.0
        }

    elif msg_type == "STATUSTEXT":
        return {
            "type": "text",
            "text": data["text"]
        }


    return None
