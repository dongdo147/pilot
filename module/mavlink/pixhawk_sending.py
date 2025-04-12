from pymavlink import mavutil

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

