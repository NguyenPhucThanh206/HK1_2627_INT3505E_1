Báo cáo Rà soát Bảo mật API

Báo cáo này tập trung rà soát và đánh giá các nguy cơ tiềm ẩn về bảo mật đối với 3 endpoint chính (`POST /auth/login`, `POST /auth/refresh`, `GET /posts/{id}`) dựa trên 5 nguyên tắc Auth cốt lõi.

---

## 1. Phân tách Xác thực (AuthN) và Ủy quyền (AuthZ) (Nguyên tắc 01)
* **Nguy cơ (Risk):** Gộp chung xử lý đăng nhập và quyết định quyền hạn trong cùng một logic xử lý. Ví dụ: Endpoint `GET /posts/{id}` nếu chỉ kiểm tra token hợp lệ (AuthN) mà không kiểm tra người dùng có quyền xem bài viết hay không (AuthZ) sẽ dẫn tới việc lộ dữ liệu riêng tư.
* **Điểm rò rỉ:** Lộ bài viết chế độ `PRIVATE` hoặc `FRIENDS` cho toàn bộ người dùng đã đăng nhập trong hệ thống.
* **Biện pháp khắc phục:** Tách biệt middleware xác thực danh tính (AuthN) và middleware kiểm tra chính sách truy cập (AuthZ). Trả về `403 Forbidden` hoặc `404 Not Found` khi người dùng không đủ quyền hạn.

---

## 2. Lựa chọn Cơ chế Phiên & Quản lý Token theo Ngữ cảnh (Nguyên tắc 02)
* **Nguy cơ (Risk):** Lựa chọn nơi lưu trữ token phía client không an toàn (ví dụ: lưu JWT trong `localStorage` thay vì `HttpOnly, Secure Cookie`). Kẻ tấn công có thể chèn mã độc JavaScript qua lỗ hổng XSS để đánh cắp Access Token và Refresh Token.
* **Điểm rò rỉ:** Thất thoát toàn bộ phiên làm việc của người dùng khi ứng dụng bị tấn công Cross-Site Scripting (XSS).
* **Biện pháp khắc phục:** Đánh giá đúng ngữ cảnh sử dụng. Nếu chạy trên giao diện Web Browser, ưu tiên lưu Refresh Token trong Cookie có cờ `HttpOnly`, `SameSite=Strict` và `Secure` để chống XSS và CSRF.

---

## 3. Kỷ luật trong Triển khai JWT & Quản lý Token (Nguyên tắc 03)
* **Nguy cơ (Risk):** 
  - Đặt thời gian hết hạn (`exp`) của Access Token quá dài.
  - Không triển khai cơ chế **Refresh Token Rotation (RTR)** tại endpoint `POST /auth/refresh`.
  - Cho phép chấp nhận các JWT không kiểm tra thuật toán (`alg: "none"`).
* **Điểm rò rỉ:** Khi một Refresh Token bị rò rỉ, kẻ tấn công có thể liên tục lấy Access Token mới để chiếm quyền tài khoản vĩnh viễn mà hệ thống không thể thu hồi.
* **Biện pháp khắc phục:** 
  - Thiết lập whitelist thuật toán mã hóa (chỉ chấp nhận `RS256` hoặc `HS256`).
  - Cài đặt thời gian sống Access Token ngắn (5–15 phút).
  - Áp dụng cơ chế xoay vòng Refresh Token (RTR): Mỗi Refresh Token chỉ được dùng 01 lần. Nếu phát hiện Refresh Token cũ được tái sử dụng (Reuse Detection), ngay lập tức vô hiệu hóa (revoke) toàn bộ chuỗi token của user đó.

---

## 4. Ủy quyền theo Chính sách & Kiểm soát Quyền Đối tượng - BOLA/IDOR (Nguyên tắc 04)
* **Nguy cơ (Risk):** Lỗi **Broken Object Level Authorization (BOLA / IDOR)** tại endpoint `GET /posts/{id}`. Kẻ tấn công có thể thay đổi chuỗi UUID `{id}` trên đường dẫn URL để truy xuất bài viết của bất kỳ ai.
* **Điểm rò rỉ:** Rò rỉ thông tin cá nhân, nội dung riêng tư, và danh tính của người dùng khác.
* **Biện pháp khắc phục:** 
  - Thực hiện kiểm tra quyền sở hữu (Ownership check) ở tầng Service/Database trước khi trả về dữ liệu.
  - Với các bài viết ẩn hoặc riêng tư mà caller không có quyền xem, hệ thống nên trả về `404 Not Found` thay vì `403 Forbidden` để tránh việc kẻ tấn công thu thập và đoán sự tồn tại của ID (Resource Enumeration).

---

## 5. Mã hóa & Băm Mật khẩu Đạt chuẩn (Nguyên tắc 05)
* **Nguy cơ (Risk):** Sử dụng các thuật toán băm yếu, đã lạc hậu (như MD5, SHA1, SHA256 đơn thuần) hoặc không có Salt khi xử lý đăng nhập tại `POST /auth/login`.
* **Điểm rò rỉ:** Nếu cơ sở dữ liệu bị rò rỉ, kẻ tấn công có thể dễ dàng dùng phương pháp Rainbow Table hoặc Brute-Force để giải mã toàn bộ mật khẩu của người dùng.
* **Biện pháp khắc phục:** 
  - Bắt buộc mã hóa mật khẩu bằng thuật toán băm hiện đại như **Argon2id** (hoặc `bcrypt`) kèm theo Salt ngẫu nhiên và thông số Cost phù hợp.
  - Triển khai cơ chế Rehash khi tăng tham số bảo mật hệ thống mà không bắt buộc người dùng đổi mật khẩu định kỳ một cách vô lý.

---

## 6. Lỗ hổng Tấn công Vét cạn (Brute-Force & Credential Stuffing)
* **Nguy cơ (Risk):** Endpoint `POST /auth/login` không được bảo vệ bởi cơ chế giới hạn tần suất gửi yêu cầu (Rate Limiting).
* **Điểm rò rỉ:** Kẻ tấn công có thể tự động hóa gửi hàng triệu yêu cầu đăng nhập mỗi phút để dò mật khẩu của người dùng.
* **Biện pháp khắc phục:** Triển khai Middleware Rate Limiting ở API Gateway hoặc ứng dụng, trả về HTTP Status Code `429 Too Many Requests` khi có quá nhiều lượt thử thất bại trong khoảng thời gian ngắn.