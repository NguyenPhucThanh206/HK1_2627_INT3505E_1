# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 9 | 0.00% | 4.7 |
| B | 50 | 5 | 60s | 13 | 0.29% | 23.4 |
| C | 200 | 50 | 30s | 81 | 0.07% | 98.1 |

*(Số lấy từ dòng Aggregated của `python performance/analyze.py`. Máy đo: [16CPU / 16GRAM / Window 11 64-bit].
Locust và API chạy cùng một máy; Flask development server + SQLite.)*

Số theo từng endpoint (p50 / p95 / p99, ms; fail %):

| Endpoint | A | B | C |
|---|---|---|---|
| GET /books | 4 / 6 / 15; 0% | 4 / 9 / 16; 0% | 6 / 82 / 170; 0% |
| GET /books/{id} | 4 / 6 / 7; 0% | 4 / 9 / 18; 0% | 5 / 47 / 150; 0% |
| GET /books?year= | 4 / 17 / 17; 0% (0/18) | 4 / 7 / 14; 1.92% (4/208) | 6 / 93 / 150; 0.48% (2/415) |
| POST /books | 8 / 11 / 11; 0% | 8 / 35 / 79; 0% | 11 / 130 / 220; 0% |

## 1. Kịch bản có p95 cao nhất là gì? Dùng số liệu quan sát để giải thích.

Kịch bản **C (200 user)** có p95 cao nhất: 81 ms, so với 13 ms ở B và 9 ms ở A (p99 của C là 170 ms).

- Từ A sang B, user tăng 5 lần nhưng p95 chỉ tăng từ 9 lên 13 ms (≈ 1,4 lần). Từ B sang C, user tăng 4 lần nhưng p95 tăng từ 13 lên 81 ms (≈ 6 lần). Tức là ở C độ trễ đuôi tăng **nhanh hơn tải**, dấu hiệu bắt đầu có tranh chấp/xếp hàng.
- Hệ thống **chưa bão hoà**: RPS tăng gần tỉ lệ với số user (4.7 → 23.4 → 98.1, khoảng 0,47–0,49 RPS/user, khớp think time trung bình 2 s) và p50 vẫn chỉ 4–6 ms. Nên không thể kết luận có nút cổ chai cứng, chỉ thấy p95/p99 bắt đầu giãn ra.
- Endpoint chậm nhất khi tải cao là `POST /books` (p95 = 130 ms, p99 = 220 ms ở C; p50 cũng cao hơn các GET: 8–11 ms so với 4–6 ms). Giả thuyết hợp lý: SQLite chỉ cho một writer tại một thời điểm nên các lần ghi xếp hàng; số liệu này phù hợp với giả thuyết nhưng chưa chứng minh nguyên nhân.
- Kịch bản C còn gồm giai đoạn tăng tải rất nhanh (200 user trong ~4 s, chưa warm-up) và Locust cùng API tranh CPU trên một máy, nên một phần p95 có thể do nhiễu đo.

## 2. Endpoint nào tăng failure rate? Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust.

Chỉ `GET /books?year=` có failure, và **toàn bộ là lỗi đánh dấu trong Locust** (`Simulated failure (client-side, server returned 200)`, xem Error report). Server luôn trả 200; **không có lỗi HTTP thực** nào (không có 5xx, timeout hay connection error).

- Fail rate của endpoint này: 0% (0/18) ở A, 1,92% (4/208) ở B, 0,48% (2/415) ở C. Con số **không tăng theo user**: đó là dao động ngẫu nhiên quanh mức 1% giả lập trên mẫu nhỏ (kỳ vọng ≈ 2 lỗi ở B và ≈ 4 lỗi ở C, quan sát được 4 và 2).
- `POST /books`, `GET /books`, `GET /books/{id}` đều 0%. Các 404 của `GET /books/{id}` được tính là thành công vì id ngẫu nhiên.
- Kết luận: không endpoint nào tăng failure rate do tải trong phạm vi đo; failure rate tổng (0,29% ở B, 0,07% ở C) hoàn toàn đến từ lỗi giả lập.
- Phân biệt: lỗi HTTP thực nghĩa là server trả status lỗi hoặc không phản hồi; lỗi đánh dấu là do code Locust gọi `response.failure()` dù server vẫn trả 200, nên không phản ánh độ tin cậy của server.

## 3. Với SLO giả định p95 < 300 ms, kịch bản nào đạt? Nêu giới hạn của phép đo.

| Kịch bản | p95 Aggregated (ms) | Đạt p95 < 300 ms? |
|---|---:|:---:|
| A | 9 | Đạt |
| B | 13 | Đạt |
| C | 81 | Đạt |

Cả ba kịch bản đạt, kể cả từng endpoint (cao nhất là `POST /books` ở C: p95 = 130 ms; p99 = 220 ms vẫn dưới 300 ms).

Giới hạn của phép đo:
- Locust và API chạy chung một máy, tranh CPU, nên số đo bị nhiễu và không đại diện cho môi trường triển khai thật.
- Flask development server + SQLite trên máy cá nhân chỉ có ý nghĩa thực hành, **không thể khẳng định SLO production**.
- Mỗi kịch bản chạy một lần, ngắn (30–60 s), không warm-up, không lặp để lấy trung vị. Số request ở A rất nhỏ (138 request; endpoint `year` chỉ 18) nên p95/p99 kém ổn định.
- Tải cao nhất (≈ 98 RPS, 200 user với think time 1–3 s) vẫn chưa làm bão hoà hệ thống (p50 chỉ 6 ms) nên **chưa biết ngưỡng chịu tải thật**. Cần stress/breakpoint test để tìm.
- Aggregated p95 bị chi phối bởi các request đọc rẻ, che bớt endpoint ghi chậm hơn.
- DB ban đầu nhỏ và tăng dần sau mỗi lần chạy (`POST /books`); dữ liệu nhỏ làm truy vấn rất nhanh.
- 1% failure là giả lập phía client nên không đo độ tin cậy thật.

## 4. Nếu connection pool bị giới hạn ở 5, bạn sẽ kiểm chứng ảnh hưởng như thế nào?

Giả thuyết: chỉ 5 request dùng DB song song, các request còn lại phải chờ connection ⇒ RPS chạm trần
(xấp xỉ `5 / thời_gian_giữ_connection`, định luật Little), p95 tăng khi user tăng; nếu chờ quá `pool_timeout` sẽ có lỗi
`QueuePool limit of size 5 overflow 0 reached` (HTTP 500) hoặc `ReadTimeout` ở Locust.

Ước lượng từ số đo hiện tại: số request đang giữ connection trung bình ≈ RPS × độ trễ ≈ 98 × (0,006–0,02 s) ≈ 0,6–2.
Con số này **thấp hơn 5**, nên với tải ở kịch bản C, pool = 5 nhiều khả năng **chưa gây nghẽn**; để thấy ảnh hưởng
cần tải cao hơn (nhiều user hơn, giảm `wait_time`) hoặc làm DB chậm hơn. Đây là dự đoán cần kiểm chứng bằng thí nghiệm.

Cách kiểm chứng (thí nghiệm có đối chứng):
1. Giữ nguyên locustfile và kịch bản; chỉ đổi cấu hình pool qua `create_app(config=...)`:
   `SQLALCHEMY_ENGINE_OPTIONS = {"pool_size": 5, "max_overflow": 0, "pool_timeout": 5}`
   so với `{"pool_size": 20, "max_overflow": 0, "pool_timeout": 5}`.
2. Chạy kịch bản C (và tăng dần user, ví dụ 200 → 500 → 1000 nếu máy cho phép) cho cả hai cấu hình; ghi p95, RPS, failure.
3. Dấu hiệu pool là nút cổ chai: với pool = 5, biểu đồ RPS đi ngang trong khi user tăng và p95 tăng vọt; tab Failures
   có thông điệp `QueuePool ... timed out`; với pool = 20, RPS cao hơn và p95 thấp hơn rõ rệt.
4. Loại trừ nguyên nhân khác: kiểm tra CPU của máy chạy Locust (< ~80%) và lặp lại 2–3 lần để chắc khác biệt không chỉ là nhiễu.

> Không điền số liệu giả định vào bảng. Không khẳng định hiệu năng production
> từ SQLite + Flask development server trên máy cá nhân.