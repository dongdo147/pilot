from pymavlink import mavutil
import time
pixhawk_master = None
pwm_channels = {}  # lưu toàn bộ pwm kênh 1-16
servo_function_map = {
    0: "Disabled",
    1: "RCPassThru",
    33: "Motor1",
    34: "Motor2",
    51: "RCIN1",
    52: "RCIN2",
    70: "Gripper",
    73: "Camera Trigger",
    80: "Landing Gear",
    120: "Relay1"
}

def set_master(master):
    global pixhawk_master
    pixhawk_master = master
def set_pwm_channels(pwm_dict):
    global pwm_channels
    pwm_channels = pwm_dict
   
def get_pwm_channel(ch):
    return pwm_channels.get(f"ch{ch}")
    
def get_all_pwm():
    return pwm_channels
def set_param_value(param_id: str, value: int):
    global pixhawk_master
    if pixhawk_master is None:
        print("❌ Chưa có kết nối Pixhawk")
        return False, "Chưa có kết nối Pixhawk"
    
    try:
        # Gửi lệnh đặt tham số
        pixhawk_master.mav.param_set_send(
            pixhawk_master.target_system,
            pixhawk_master.target_component,
            param_id.encode('utf-8'),
            value,
            mavutil.mavlink.MAV_PARAM_TYPE_INT32
        )
        print(f"Đã gửi lệnh đặt {param_id} = {value}")
        time.sleep(1)  # Chờ Pixhawk xử lý
        
        # Đọc lại tham số
        param_value = read_parameter(param_id)
        if param_value is not None:
            param_value = int(param_value)
         
            if param_value == value:
                return True
            else:
                return False
        else:
            return False, f"Không thể đọc giá trị {param_id}"
    except Exception as e:
        print(f"Lỗi khi đặt tham số {param_id}: {str(e)}")
        return False, f"Lỗi khi đặt tham số {param_id}: {str(e)}"

def read_parameter(param_id: str):
    global pixhawk_master
    if pixhawk_master is None:
        print("❌ Chưa có kết nối Pixhawk")
        return None
    
    for attempt in range(3):  # Thử 3 lần
        try:
            pixhawk_master.mav.param_request_read_send(
                pixhawk_master.target_system,
                pixhawk_master.target_component,
                param_id.encode('utf-8'),
                -1
            )
            timeout = time.time() + 10  # Tăng timeout
            while time.time() < timeout:
                msg = pixhawk_master.recv_match(type='PARAM_VALUE', blocking=True, timeout=1)
                if msg and msg.param_id == param_id:
                    return msg.param_value
                time.sleep(0.1)
            print(f"Lỗi: Timeout khi đọc {param_id} (lần {attempt + 1})")
        except Exception as e:
            print(f"Lỗi khi đọc tham số {param_id} (lần {attempt + 1}): {str(e)}")
        time.sleep(1)  # Chờ trước khi thử lại
    return None


def send_pwm(channel, pwm_value, step=10, delay=50):
    global pixhawk_master
    if pixhawk_master is None:
        print("❌ Chưa có kết nối Pixhawk để gửi PWM")
        return False

    if not (800 <= pwm_value <= 2200):
        print(f"❌ PWM {pwm_value} ngoài giới hạn an toàn (900–2100µs)")
        return False

    current_pwm = get_pwm_channel(channel)

    if current_pwm is None:
        print(f"⚠️ Không có giá trị PWM hiện tại cho kênh {channel}, dùng mặc định 1500")
        current_pwm = 1500

    if step <= 0 or delay <= 0 or abs(current_pwm - pwm_value) <= step:
        print(f"📤 Gửi PWM trực tiếp {pwm_value} µs tới kênh {channel}")
        pixhawk_master.mav.command_long_send(
            pixhawk_master.target_system,
            pixhawk_master.target_component,
            183, 0, channel, pwm_value, 0, 0, 0, 0, 0
        )
        return True

    while current_pwm != pwm_value:
        if pwm_value > current_pwm:
            current_pwm = min(current_pwm + step, pwm_value)
            
        else:
            current_pwm = max(current_pwm - step, pwm_value)

        try:
            pixhawk_master.mav.command_long_send(
            pixhawk_master.target_system,
            pixhawk_master.target_component,
            183, 0, channel, current_pwm, 0, 0, 0, 0, 0   )
        except Exception as e:
            print(f"❌ Lỗi khi gửi PWM: {e}")
            return False
        time.sleep(delay / 1000.0)

    print(f"✅ Gửi PWM {pwm_value} µs thành công tới kênh {channel}")
    return True

def send_custom_command(command_id, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0):
    global pixhawk_master

    if pixhawk_master is None:
        print("❌ Pixhawk chưa kết nối, không gửi được lệnh.")
        return False

    # Debug: In ra các giá trị tham số được nhận
    print(f"🌟 Gửi lệnh: command_id={command_id}, param1={param1}, param2={param2}, param3={param3}, param4={param4}, param5={param5}, param6={param6}, param7={param7}")

    try:
        # Gửi lệnh yêu cầu reboot
        pixhawk_master.mav.command_long_send(
            pixhawk_master.target_system,
            pixhawk_master.target_component,
            command_id,
            1,  # Confirmation yêu cầu xác nhận
            param1,
            param2,
            param3,
            param4,
            param5,
            param6,
            param7
        )

      
        return True
      
    except Exception as e:
        # Debug: In ra lỗi nếu có
        print(f"❌ Lỗi khi gửi lệnh: {e}")
        return False

def send_arm_command():
    global pixhawk_master
    if pixhawk_master is None:
        print("❌ Chưa có kết nối Pixhawk để gửi lệnh")
        return False

    # Chuyển sang chế độ MANUAL trước khi arm 
    mode = 'MANUAL'
    try:
        mode_id = pixhawk_master.mode_mapping()[mode]
    except Exception as e:
        print(f"❌ Không lấy được mode_id cho {mode}: {e}")
        return False

    pixhawk_master.mav.set_mode_send(
        pixhawk_master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

    # Gửi lệnh ARM
    pixhawk_master.mav.command_long_send(
        pixhawk_master.target_system, pixhawk_master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,  # confirmation
        1, 0, 0, 0, 0, 0, 0  # 1 = arm, 0 = disarm
    )

    # Đợi phản hồi ACK
    ack = pixhawk_master.recv_match(type='COMMAND_ACK', blocking=True)
    print("✅ ARM ACK:", ack)
    return True
def send_mission(waypoints):
    global pixhawk_master
    if pixhawk_master is None:
        return False, "Chưa kết nối Pixhawk"

    try:
        # Clear old mission
        pixhawk_master.mav.mission_clear_all_send(
            pixhawk_master.target_system,
            pixhawk_master.target_component
        )
        time.sleep(1)

        # Gửi số lượng mission
        pixhawk_master.mav.mission_count_send(
            pixhawk_master.target_system,
            pixhawk_master.target_component,
            len(waypoints)
        )

        for wp in waypoints:
            pixhawk_master.mav.mission_item_send(
                pixhawk_master.target_system,
                pixhawk_master.target_component,
                wp.seq,
                wp.frame,
                wp.command,
                wp.current,
                wp.autocontinue,
                wp.param1,
                wp.param2,
                wp.param3,
                wp.param4,
                wp.x,
                wp.y,
                wp.z
            )
            time.sleep(0.2)

        # Chờ nhận mission ack
        ack = pixhawk_master.recv_match(type='MISSION_ACK', blocking=True, timeout=5)
        if ack:
            return True, [wp.dict() for wp in waypoints]
        else:
            return False, "Không nhận được MISSION_ACK"

    except Exception as e:
        return False, str(e)

def start_mission():
    global pixhawk_master
    if pixhawk_master is None:
        print("❌ Pixhawk chưa kết nối.")
        return False

    # Chuyển sang chế độ AUTO
    mode = 'AUTO'
    try:
        mode_id = pixhawk_master.mode_mapping()[mode]
    except Exception as e:
        print(f"❌ Không lấy được mode_id cho {mode}: {e}")
        return False

    pixhawk_master.mav.set_mode_send(
        pixhawk_master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )

    print("🚀 Đã chuyển sang chế độ AUTO. Mission sẽ tự động bắt đầu.")
    return True
