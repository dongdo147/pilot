from pymavlink import mavutil
import time
import json
import os
pixhawk_master = None
def log_data(data, filename="log/gps_log.txt"):
    if data.get("type") == "gps":
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "a") as f:
                json.dump(data, f)
                f.write(",\n")
                f.flush()  # Ensure each object is on a new line
        except Exception as e:
            print(f"Error logging data: {e}")

def connect_pixhawk(device='/dev/serial0', baudrate=57600, timeout=10, retries=3):
    print("⏳ Đang kết nối tới Pixhawk...")
    for attempt in range(retries):
        try:
            master = mavutil.mavlink_connection(device, baud=baudrate)
            break
        except Exception as e:
            print(f"❌ Lỗi khi mở cổng (thử {attempt+1}/{retries}): {e}")
            if attempt == retries - 1:
                print("⚠️ Không thể kết nối sau nhiều lần thử!")
                return None
            time.sleep(2)  # Chờ 2 giây trước khi thử lại

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
    global pixhawk_master
    pixhawk_master=master
    msg = master.recv_match(blocking=True)
    if not msg:
        return None

    msg_type = msg.get_type()
    data = msg.to_dict()

    if msg_type == "GPS_RAW_INT":
        gps_data = {
            "type": "gps",
            "lat2": data["lat"] / 1e7,
            "lon2": data["lon"] / 1e7,
            "alt2": data["alt"] / 1000.0,
            "satellites": data["satellites_visible"],
            "fix_type": data["fix_type"],
            "timestamp": time.time()
        }
        # log_data(gps_data)
        return gps_data

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
            "current": data["current_battery"] / 100.0,
            "remaining": data.get("battery_remaining")  # tránh KeyError nếu không có
        }

    elif msg_type == "STATUSTEXT":
        return {
            "type": "text",
            "text": data["text"]
        }
    elif msg_type == "SERVO_OUTPUT_RAW":
        pwm_dict = {}
        for i in range(1, 17):
            field = f"servo{i}_raw"
            if field in data and data[field] > 0:
                pwm_dict[f"ch{i}"] = data[field]

        # Gửi toàn bộ pwm vào pixhawk_sending
        from module.mavlink import pixhawk_sending
        pixhawk_sending.set_pwm_channels(pwm_dict)

        return {
            "type": "pwm",
            "pwm_outputs": pwm_dict
        }
    elif msg_type == "HEARTBEAT":
    # Kiểm tra xem drone đã được armed chưa
        is_armed = (data["base_mode"] & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
        
        return {
            "type": "heartbeat",
            "armed": is_armed,
            "mode": data["custom_mode"]
        }

    return None
def readMission():
    global pixhawk_master
    if pixhawk_master is None:
        print("❌ Chưa có kết nối Pixhawk")
        return False, "Chưa có kết nối Pixhawk"

    print("📥 Đang tải mission từ Pixhawk...")
    mission_items = []

    try:
        pixhawk_master.waypoint_request_list_send()
        n_missions = None

        # Nhận số lượng mission
        while True:
            msg = pixhawk_master.recv_match(type='MISSION_COUNT', blocking=True, timeout=5)
            if msg:
                n_missions = msg.count
                break

        # Lấy từng mission item
        for i in range(n_missions):
            pixhawk_master.waypoint_request_send(i)
            msg = pixhawk_master.recv_match(type='MISSION_ITEM', blocking=True, timeout=5)
            if msg:
                mission_items.append(msg.to_dict())

        print("✅ Đã tải xong mission!")
        return True, mission_items

    except Exception as e:
        print(f"❌ Lỗi khi đọc mission: {e}")
        return False, str(e)
