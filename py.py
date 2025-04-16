from pymavlink import mavutil
import time

# Kết nối MAVLink
master = mavutil.mavlink_connection('COM5', baud=57600)
print("Đang chờ heartbeat...")
master.wait_heartbeat()
print("Đã nhận heartbeat, kết nối thành công!")

# Hàm gửi PWM
def send_pwm(channel, pwm_value):
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        183,
        0,  # confirmation
        channel, pwm_value, 0, 0, 0, 0, 0
    )
    print(f"Gửi PWM {pwm_value:.0f} µs đến kênh {channel}")

# Thông số sweep
channel = 9
pwm_start = 800
pwm_end = 2200
duration = 5  # thời gian quét từ start -> end (giây)
step_time = 0.1  # thời gian mỗi bước (20ms)

steps = int(duration / step_time)
for i in range(steps + 1):
    t = i / steps  # giá trị từ 0.0 -> 1.0
    pwm = pwm_start + (pwm_end - pwm_start) * t
    send_pwm(channel, pwm)
    time.sleep(step_time)
