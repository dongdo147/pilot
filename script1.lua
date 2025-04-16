-- Script để đọc yaw từ Pixhawk 4, chuyển thành PWM và gửi đến servo kênh 9
-- Lưu script này vào thư mục APM/scripts trên thẻ SD của Pixhawk

-- Cấu hình kênh servo và PWM
local channel = 9        -- Kênh servo (kênh 9)
local min_pwm = 800      -- Giá trị PWM tối thiểu
local max_pwm = 2200     -- Giá trị PWM tối đa
local delay = 100        -- Thời gian timeout PWM (ms)

-- Hàm ánh xạ giá trị yaw (0-360 độ) sang PWM (min_pwm đến max_pwm)
local function map_yaw_to_pwm(yaw_deg)
    -- Đảm bảo yaw trong khoảng 0-360
    yaw_deg = yaw_deg % 360
    -- Ánh xạ tuyến tính: 0° -> min_pwm, 360° -> max_pwm
    local pwm = min_pwm + (yaw_deg / 360) * (max_pwm - min_pwm)
    -- Giới hạn PWM trong khoảng min_pwm đến max_pwm
    return math.floor(math.max(min_pwm, math.min(max_pwm, pwm)))
end

-- Hàm chính để đọc yaw và điều khiển servo
local function update()
    -- Kiểm tra xem ahrs có sẵn không
    if not ahrs then
        gcs:send_text(6, "Error: AHRS not available")
        return update, 100
    end

    -- Lấy giá trị yaw từ cảm biến AHRS
    local yaw_rad = ahrs:get_yaw()
    if yaw_rad then
        local yaw_deg = yaw_rad * 180 / math.pi -- Chuyển từ radian sang độ
        local pwm = map_yaw_to_pwm(yaw_deg)     -- Chuyển yaw thành PWM

        -- Gửi PWM đến kênh servo (channel - 1 vì ArduPilot dùng 0-based index)
        SRV_Channels:set_output_pwm_chan_timeout(channel - 1, pwm, delay)

        -- Gửi thông báo đến Mission Planner
        gcs:send_text(6, string.format("Yaw: %.2f deg, PWM: %d", yaw_deg, pwm))
    else
        gcs:send_text(6, "Error: Unable to read yaw")
    end

    -- Lên lịch chạy lại hàm sau 100ms
    return update, 100
end

-- Kiểm tra xem gcs và SRV_Channels có sẵn không
if not gcs then
    return
end
if not SRV_Channels then
    gcs:send_text(6, "Error: SRV_Channels not available")
    return
end

-- Gửi thông báo khởi động
gcs:send_text(6, "Yaw to PWM script started")

-- Bắt đầu vòng lặp
return update()