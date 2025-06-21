import os.path

from ultralytics import YOLO
import cv2
import os


def run():
    test_folder = "app/images/test"
    result_folder = "app/images/result"

    # Tên ảnh bạn muốn kiểm tra
    test_image = "image_2.jpg"

    img_path = os.path.join(test_folder, test_image)
    save_path = os.path.join(result_folder, test_image)
    model = YOLO("model/custom/best.pt")
    result = model(img_path)
    result[0].show()

    img = result[0].plot()
    cv2.imwrite(save_path, img)
    print(f"Đã lưu kết quả trong thư mục: {result_folder}")
