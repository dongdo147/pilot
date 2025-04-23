from pymavlink import mavutil
import time
pixhawk_master = None
pwm_channels = {}  # lưu toàn bộ pwm kênh 1-16

def set_master(master):
    global pixhawk_master
    pixhawk_master = master
def set_pwm_channels(pwm_dict):
    global pwm_channels
    pwm_channels = pwm_dict
    print(pwm_channels)
def get_pwm_channel(ch):
 
    return pwm_channels.get(f"ch{ch}")

def get_all_pwm():
    return pwm_channels

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

  
        pixhawk_master.mav.command_long_send(
            pixhawk_master.target_system,
            pixhawk_master.target_component,
            183, 0, channel, current_pwm, 0, 0, 0, 0, 0
        )
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

async def send_arm_command():
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
async def set_param(param_id: str, param_value: float):
    global pixhawk_master
    if pixhawk_master is None:
        print("❌ Chưa có kết nối Pixhawk để gửi lệnh")
        return False

    print(f"📤 Gửi PARAM_SET: {param_id} = {param_value}")
    pixhawk_master.mav.param_set_send(
        pixhawk_master.target_system,
        pixhawk_master.target_component,
        param_id.encode('utf-8'),
        float(param_value),
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32
    )


    # Gửi lệnh lưu vào EEPROM
    time.sleep(0.5)
    pixhawk_master.mav.command_long_send(
        pixhawk_master.target_system,
        pixhawk_master.target_component,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_STORAGE,
        1,
        1, 0, 0, 0, 0, 0, 0
    )

    print("💾 Đã gửi lệnh lưu tham số vào EEPROM")
    return True

