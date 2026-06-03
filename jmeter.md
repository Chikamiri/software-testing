# Báo cáo kiểm thử hiệu năng bằng JMeter

# Tài liệu tham khảo

- Video yêu cầu của đề bài: https://www.youtube.com/watch?v=NTyY8wKSvik
- Link Github tham khảo: https://github.com/quocbinh93/JMeter

# Mục tiêu
- Sử dụng JMeter để tạo kịch bản kiểm tra mô phỏng người dùng truy cập trang web https://www.gameuidatabase.com
- Chạy kịch bản kiểm tra và ghi lại kết quả
- Phân tích kết quả và đưa ra kết luận.

# Kịch bản kiểm tra
## Threads Group
- Số lượng luồng: 50
- Thời gian khởi động: 30 giây
- Số vòng lặp: 5
- Mục tiêu**: Mô phỏng 50 người dùng đồng thời thực hiện tuần tự 3 bước:
  1. Truy cập Trang chủ (`01_HomePage`)
  2. Xem thông tin Game (`02_GameInfo` với id = 150)
  3. Xem ảnh lớn (`03_SeeFullIMG` với id = 150 & autoload = 2641)
- Cấu hình bổ sung: Bật tính năng tải tài nguyên nhúng và tải song song với pool size = 6.

# Kết quả kiểm thử
Trích xuất từ báo cáo `report/statistics.json` và `result.csv`:

### Bảng số liệu chi tiết các Transaction chính
| Transaction | Số lượng mẫu (Samples) | Số lỗi (Errors) | Tỉ lệ lỗi (Error %) | TB thời gian phản hồi (Mean) | Trung vị phản hồi (Median) | Phân vị 90% (90% Line) | Phân vị 95% (95% Line) | Phân vị 99% (99% Line) | Phản hồi lớn nhất (Max) | Băng thông (Throughput) | Dung lượng TB tải về (Avg Size) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **01_HomePage** | 245 | 22 | 8.98% | 36.25 s | 20.72 s | 91.98 s | 99.84 s | 204.15 s | 583.51 s | 0.359 req/s | 5.33 MB |
| **02_GameInfo** | 244 | 28 | 11.48% | 43.18 s | 27.53 s | 98.77 s | 109.83 s | 169.84 s | 597.73 s | 0.361 req/s | 10.20 MB |
| **03_SeeFullIMG** | 243 | 38 | 15.64% | 39.65 s | 27.73 s | 101.38 s | 104.63 s | 130.94 s | 164.07 s | 0.369 req/s | 10.10 MB |
| **Tổng cộng (Total)** | **96,675** | **471** | **0.487%** | **1.59 s** | **0.052 s** | **0.887 s** | **2.22 s** | **8.41 s** | **597.73 s** | **140.37 req/s** | **-** |

*Lưu ý: Tổng số mẫu là 96,675 vì đã bao gồm tất cả các request con tải tài nguyên nhúng (như CSS, JS, hình ảnh, CDN).*

# Phân tích kết quả và các vấn đề gặp phải

## 1. Lỗi tràn bộ nhớ
Trong quá trình kiểm thử, log hệ thống (`jmeter.log`) ghi nhận lỗi tràn bộ nhớ heap của Java:
```log
2026-06-03 20:32:21,306 ERROR o.a.j.JMeter: Uncaught exception in thread Thread[Thread Group 1-37,5,main]
java.lang.OutOfMemoryError: Java heap space
2026-06-03 20:35:09,677 ERROR o.a.j.JMeter: Uncaught exception in thread Thread[Thread Group 1-23,5,main]
```
Lỗi này làm xuất hiện file heap dump lớn `java_pid44446.hprof` (~971MB) trong thư mục làm việc.
- Hệ quả: Đã có ít nhất 2 luồng giả lập (`Thread Group 1-37` và `Thread Group 1-23`) bị crash hoàn toàn trước khi hoàn thành đủ 5 vòng lặp, dẫn tới số lượng mẫu của các bước chính không đạt đủ 250 (thiếu từ 5-7 mẫu).
- Nguyên nhân: JMeter lưu toàn bộ kết quả phản hồi của các luồng trong bộ nhớ RAM. Do tải quá nhiều tài nguyên nhúng song song, bộ nhớ Heap mặc định (thường là 1GB) của Java JVM chạy JMeter đã bị quá tải.

## 2. Lỗi mạng và Kết nối
Phân tích 471 lỗi ghi nhận trong `result.csv`, các loại lỗi chính bao gồm:
- 272 lỗi 'Connection pool shut down': Xảy ra sau khi các luồng bị crash do OOM làm đóng đột ngột HTTP connection pool của HttpClient4.
- 86 lỗi 'Connection reset / Socket closed': Xảy ra khi kết nối bị ngắt giữa chừng do quá tải mạng hoặc do phản hồi từ phía server bị quá hạn (timeout).

## 3. Thời gian phản hồi quá cao & Băng thông thấp
- Thời gian phản hồi trung bình của các trang chính rất lớn (từ 36 giây đến 43 giây). Phân vị 99% lên tới hơn 3 phút, có request mất gần 10 phút (`597.73 s`).
- Lý do:
  1. Dung lượng trang lớn: Mỗi lần truy cập trang thông tin game (`02_GameInfo` và `03_SeeFullIMG`) tải về trung bình tới **10.2 MB** dữ liệu. Với 50 người dùng chạy đồng thời, tổng lượng dữ liệu tải về trong 11 phút là **~6.2 GB**, tạo áp lực lớn lên băng thông mạng và CPU của máy chạy test.
  2. Tải tài nguyên bên thứ ba: Hệ thống phải tải hàng trăm tài nguyên từ bên thứ ba như:
     - Thư viện CDN: `code.jquery.com`, `cdn.jsdelivr.net`
     - Video nhúng của YouTube: `https://www.youtube-nocookie.com/embed/...`
     Khi chạy giả lập tải song song với số lượng lớn luồng, YouTube và các CDN sẽ kích hoạt chế độ chống DDOS, dẫn đến việc bóp băng thông (rate limit) hoặc ngắt kết nối (`Connection reset`), khiến thời gian tải kéo dài vô hạn và tạo ra lỗi kết nối.

# Đề xuất tối ưu hóa

1. Loại bỏ tải tài nguyên bên thứ ba
2. Tăng cấu hình bộ nhớ Heap cho JMeter
3. Cấu hình Timeout
