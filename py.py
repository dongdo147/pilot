from pymavlink import mavutil
import time

# Kết nối qua TELEM 5 bằng COM5
master = mavutil.mavlink_connection('com5', baud=57600)
print("Đang chờ heartbeat...")
master.wait_heartbeat()
print("Đã nhận heartbeat, kết nối thành công!")

# Hàm gửi PWM đến kênh
def set_pwm(channel, pwm_value):
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
        0, channel, pwm_value, 0, 0, 0, 0, 0)
    print(f"Đã gửi PWM {pwm_value} µs đến kênh {channel}")
set_pwm(9, 800)
time.sleep(3)
# Gửi PWM từ 800 đến 2200 với bước 100
for pwm in range(800, 2201, 20):  # 2201 để bao gồm cả 2200
    set_pwm(9, pwm)
    time.sleep(0.01)
time.sleep(1)
# Nếu muốn giảm ngược lại cũng được:
for pwm in range(2200, 799, -20):
    set_pwm(9, pwm)
    time.sleep(0.01)
time.sleep(1)
for pwm in range(800, 2201, 20):  # 2201 để bao gồm cả 2200
    set_pwm(9, pwm)
    time.sleep(0.01)
time.sleep(1)
for pwm in range(2200, 799, -20):
    set_pwm(9, pwm)
    time.sleep(0.01)