import cv2

class USBCamera:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)  # Thêm CAP_V4L2 nếu dùng Linux
        if not self.cap.isOpened():
            raise IOError(f"Không thể mở camera tại index {self.camera_index}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        print("Camera đã sẵn sàng")

    def read_frame(self):
        if self.cap is None:
            raise RuntimeError("Camera chưa được mở. Gọi .open() trước đã")
        
        ret, frame = self.cap.read()
        if not ret:
            raise IOError("Không thể đọc frame từ camera")
        return frame

    def show_preview(self, window_name="Camera Preview", delay=1):
        try:
            while True:
                frame = self.read_frame()
                cv2.imshow(window_name, frame)
                if cv2.waitKey(delay) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"💥 Lỗi trong show_preview: {e}")
        finally:
            self.release()
            cv2.destroyAllWindows()


    def release(self):
        if self.cap:
            self.cap.release()
            print("Camera đã đóng")

# Nếu chạy trực tiếp file này để test:
if __name__ == "__main__":
    cam = USBCamera()
    cam.open()
    cam.show_preview()
