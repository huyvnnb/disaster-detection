# Hướng dẫn cài đặt và chạy dự án

1. Cài đặt ultralytics
- Vì có một số thay đổi trong source code của YOLO, nên mọi người hãy clone project này về từ github của mình:
```git
git clone https://github.com/huyvnnb/ultralytics.git
```
- Đổi tên ultralytics thành tên khác, ví dụ ultralytics_custom
```commandline
cd ultralytics_custom
pip install -e .
```

2. Chạy và xem kết quả
- Hãy chỉnh sửa các đường dẫn trong file app/main.py
  - Ảnh ở trong thư mục: app/images/test
  - Model: model/custom/best.pt
  - Kết quả sẽ được show ra ngay lập tức, hoặc bạn có thể lưu vào app/images/result
- Do mình muồn lưu cả file model của YOLO gốc và YOLO đã thay đổi (thêm cơ chế chú ý **CBAM**)

- Chạy kết quả
```commandline
python run.py
```
