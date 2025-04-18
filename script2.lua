function update()
    -- Đọc giá trị PWM từ RC Channel 1
    local pwm_channel_1 = rc:get_pwm(1)

    if pwm_channel_1 then
        -- Áp dụng công thức đảo chiều PWM
        local pwm_channel_9 = 3000 - pwm_channel_1

        -- Đảm bảo PWM trong phạm vi 1000 - 2000
        pwm_channel_9 = math.min(math.max(pwm_channel_9, 1000), 2000)

        -- Gửi tín hiệu PWM đã đảo chiều vào Channel 9
        SRV_Channels:set_output_pwm_chan(8, pwm_channel_9)  -- Channel 9 tương ứng với chỉ số 8 (0-based index)

        -- Gửi thông báo cho GCS để kiểm tra
        gcs:send_text(6, string.format("PWM Channel 1: %d -> PWM Channel 9 (Đảo chiều): %d", pwm_channel_1, pwm_channel_9))
    else
        gcs:send_text(6, "Không đọc được PWM Channel 1")
    end

    -- Đặt lại sau mỗi 100ms (mỗi 100ms sẽ tính toán và cập nhật PWM)
    return update, 500
end

return update()
