from pymavlink import mavutil
import asyncio
pixhawk_master = None
pwm_channels = {}  # lưu toàn bộ pwm kênh 1-16

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

async def send_pwm(channel, pwm_value, step=10, delay=50):
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

        print(f"📤 Gửi PWM {current_pwm} µs tới kênh {channel}")
        pixhawk_master.mav.command_long_send(
            pixhawk_master.target_system,
            pixhawk_master.target_component,
            183, 0, channel, current_pwm, 0, 0, 0, 0, 0
        )
        await asyncio.sleep(delay / 1000.0)

    print(f"✅ Gửi PWM {pwm_value} µs thành công tới kênh {channel}")
    return True

def send_custom_command(master, command_id, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0):
    if master is None:
        print("❌ Pixhawk chưa kết nối, không gửi được lệnh.")
        return

    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        command_id,  # ID của lệnh (tùy mình, ví dụ: 30001)
        0,           # Confirmation
        param1,
        param2,
        param3,
        param4,
        param5,
        param6,
        param7
    )




def send_text_to_gcs(master, text, severity=6):
    """
    Gửi đoạn text lên GCS như Mission Planner hoặc QGroundControl (hoặc Lua script sẽ thấy).
    Severity từ 0 (EMERG) đến 6 (INFO)
    """
    if master is None:
        print("❌ Không có kết nối để gửi text.")
        return

    master.mav.statustext_send(severity, text.encode())

