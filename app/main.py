import tkinter as tk
from app.interface import App


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


# def run2():
#     test_folder = "app/images/test"
#     result_folder = "app/images/result"
#
#     test_image = "image_25.jpg"
#
#     img_path = os.path.join(test_folder, test_image)
#     save_path = os.path.join(result_folder, test_image)
#
#     result = model(img_path)
#     result[0].show()
#
#     img = result[0].plot()
#     cv2.imwrite(save_path, img)
#     print(f"Đã lưu kết quả trong thư mục: {result_folder}")
#
#
# def run3():
#     test_folder = "app/video/test"
#     result_folder = "app/video/result"
#
#     # Tên ảnh bạn muốn kiểm tra
#     test_video = "video.mp4"
#
#     video_path = os.path.join(test_folder, test_video)
#     save_path = os.path.join(result_folder, test_video)
#
#     cap = cv2.VideoCapture(video_path)
#
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))
#
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         results = model(frame)
#         annotated_frame = results[0].plot()
#
#         out.write(annotated_frame)
#         cv2.imshow("YOLOv8s", annotated_frame)
#
#         if cv2.waitKey(1) == 27:
#             break
#
#     cap.release()
#     out.release()
#     cv2.destroyAllWindows()
#     print(f"Đã lưu video kết quả tại: {save_path}")

    # result = model(img_path)
    # result[0].show()
    #
    # img = result[0].plot()
    # cv2.imwrite(save_path, img)
    # print(f"Đã lưu kết quả trong thư mục: {result_folder}")
