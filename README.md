# Hệ thống chấm bài trắc nghiệm

Bài tập lớn môn Xử lý ảnh. Ứng dụng desktop chấm phiếu trả lời trắc nghiệm từ ảnh chụp hoặc ảnh scan, chỉ dùng xử lý ảnh truyền thống (OpenCV + NumPy), không dùng học máy.

## Cài đặt và chạy

Yêu cầu Python 3.8 trở lên.

```
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Cách dùng

1. Bấm **+ Tạo kỳ thi**, đặt tên và chọn mẫu phiếu.
2. Mục **Đề & đáp án**: thêm mã đề (3 số), chọn đáp án trên bảng, bấm **Lưu đáp án**. Bấm vào mã đề ở cột trái để xem lại hoặc sửa. Đáp án tự lưu khi chuyển đề, chuyển mục hoặc đóng ứng dụng.
3. Mục **Chấm bài**: chọn ảnh, bấm **Chấm bài**. Ứng dụng đọc mã đề trên phiếu và dùng đáp án của mã đề đó. Kỳ thi chỉ có một đề thì dùng luôn đề đó.
4. Mục **Thống kê**: số phiếu, số lỗi, điểm trung bình, cao nhất, thấp nhất, bảng tất cả lần chấm và nút tải file điểm CSV.

Chấm nhiều lần trong cùng một kỳ thi thì kết quả được gộp vào một file. Một SBD chấm nhiều lần chỉ tính lần mới nhất.

## Mẫu phiếu hỗ trợ

| Mẫu | Nội dung | File in |
|---|---|---|
| Mẫu 20 câu | 20 câu ABCD | `Form20_VI_6SBD_NOLABEL.pdf` |
| Mẫu 40 câu | 40 câu ABCD | `Form40_VI_6SBD_NOLABEL.pdf` |
| Mẫu 50 câu | 50 câu ABCD | `Form_50_VI_NOLABEL - BLACK.cdr.pdf` |
| Mẫu 100 câu | 100 câu ABCD | `Form100_VI_6SBD_NOLABEL.pdf` |
| Mẫu 120 câu | 120 câu ABCD | `Form_120_VI_NOLABEL-BLACK.pdf` |
| Mẫu THPT 3 phần | Phần I: 12 câu ABCD, Phần II: 4 câu Đúng/Sai, Phần III: 6 câu điền số | `mau_thpt_A4.pdf` |

Các file PDF nằm trong `sheets`. In đúng khổ A4, không cắt mất 4 ô vuông đen ở góc. Khi chụp, cầm máy song song với mặt giấy và thấy đủ 4 góc.

## Thang điểm

- Mẫu chỉ có câu ABCD: chia đều 10 điểm cho số câu có đáp án.
- Mẫu THPT: Phần I 0,25 điểm/câu; Phần II đúng 1/2/3/4 ý được 0,1/0,25/0,5/1 điểm; Phần III 0,5 điểm/câu, so sánh theo giá trị (`1,5` và `1,50` như nhau).
- Câu để trống đáp án thì không chấm.

## Thuật toán (`grader.py`)

Hàm chính: `grade_image(anh, mau, cac_de)` chấm 1 ảnh, `find_corners(anh, mau)` tìm 4 góc phiếu.

1. **Tìm phiếu** (`find_corners`): thu nhỏ ảnh về rộng 1000 px, ảnh xám, lọc Gaussian, ngưỡng thích nghi, tìm contour. Giữ các contour gần vuông, 4 đỉnh, bên trong đặc; 4 ô ngoài cùng là 4 góc. Kiểm tra tỉ lệ cao/rộng của tứ giác so với phiếu mẫu để báo lỗi ảnh chụp quá nghiêng.
2. **Hiệu chỉnh phối cảnh**: ma trận phối cảnh từ 4 góc tìm được sang 4 góc của mẫu, nắn phiếu về kích thước mẫu.
3. **Nhị phân hóa** phiếu đã nắn bằng ngưỡng thích nghi, cửa sổ 4R+1.
4. **Connected components**: vết tô có kích thước gần bằng ô tròn được gán vào ô gần nhất để bù sai lệch nhỏ khi nắn.
5. **Phát hiện ô được tô**: tỉ lệ điểm đen ở phần giữa ô lớn hơn `NGUONG_TO` (0,5) là đã tô.
6. **Ghép bài làm**: mỗi nhóm ô chỉ được tô 1 ô; `_` là bỏ trống, `X` là tô nhiều ô.
7. **Chọn đáp án theo mã đề, tính điểm, vẽ kết quả**: xanh là đúng, đỏ là sai.

## Cấu trúc thư mục

```
BTL XLA/
├── app.py              Giao diện desktop (CustomTkinter)
├── grader.py           Thuật toán chấm phiếu
├── templates.py        Tọa độ ô và thang điểm của từng mẫu phiếu
├── fonts/              Font Plus Jakarta Sans (giấy phép OFL) cho giao diện
├── requirements.txt
├── sheets/             Phiếu mẫu PDF để in và ảnh PNG 150 dpi để đo tọa độ
└── exams/              Dữ liệu từng kỳ thi (tạo tự động)
    └── <tên kỳ thi>/
        ├── de.json     Mẫu phiếu và đáp án các mã đề
        ├── diem.csv    Kết quả tất cả các lần chấm
        └── images/     Ảnh kết quả và ảnh phiếu lỗi
```

## Thêm mẫu phiếu mới

1. Đổi file PDF sang ảnh PNG 150 dpi (khổ A4 cho ảnh khoảng 1240 x 1754 px), lưu vào `sheets`.
2. Đo tọa độ tâm 4 ô vuông góc, các ô số báo danh, mã đề và các ô câu hỏi trên ảnh PNG.
3. Thêm một mục vào `DANH_SACH_MAU` trong `templates.py`. Ý nghĩa các thông số được ghi ở đầu file.

## Hạn chế

- Ảnh chụp nghiêng mạnh (mép xa nhỏ hơn hẳn mép gần) bị báo lỗi, cần chụp lại thẳng hơn.
- Phiếu xoay ngang hoặc lộn ngược, phiếu bị gấp hay cong nhiều có thể đọc sai.
- Vết tẩy còn mờ có thể bị tính là ô đã tô.
- Không đọc số viết tay ở ô phía trên, chỉ đọc phần tô.
