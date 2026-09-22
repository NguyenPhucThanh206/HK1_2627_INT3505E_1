# BÁO CÁO AUDIT PUBLIC API: GITHUB REST API 
Đường dẫn: https://docs.github.com/en/rest/users/users?apiVersion=2026-03-10#get-a-user
#1.Tổng hợp các endpoints
    1-/users/{username}
    2-/users/{username}/repos
    3-/user/repos
    4-/repos/{owner}/{repo}
    5-/repos/{owner}/{repo}
#2.method và status code 
    1-GET {200, 404}
    2-GET {200, 404}
    3-POST {201, 401, 422}
    4-PATCH {200, 403, 404}
    5-DELETE {204, 403, 404}
#3.HEADERS 
    1-GET /users/{username}
        *Request Headers: 
            + Accept: application/vnd.github+json (Yêu cầu nhận dữ liệu định dạng JSON theo chuẩn GitHub)
            + X-GitHub-Api-Version: 2022-11-28 (Khai báo phiên bản API)
            + If-None-Match: "33a867ed..." (Tùy chọn: dùng khi gửi conditional request)
        *Response Headers:
            + Content-Type: application/json; charset=utf-8 (Định dạng dữ liệu trả về)

            + ETag: "33a867ed700920..." (Mã băm nội dung để client lưu cache)

            + Cache-Control: public, max-age=60, s-maxage=60 (Cho phép lưu cache tối đa 60 giây)

            + X-RateLimit-Limit: 60 (Số request tối đa allowed trong 1 giờ)

            + X-RateLimit-Remaining: 59 (Số request còn lại)
    2-GET /users/{username}/repos
        * Request Headers (Gửi đi):

            + Accept: application/vnd.github+json

            + X-GitHub-Api-Version: 2022-11-28
        * Response Headers (Nhận về):

            + Content-Type: application/json; charset=utf-8

            +Link: <https://api.github.com/user/58277/repos?page=2>; rel="next"

            + ETag: "W/\"4f5a...\""

            + Cache-Control: public, max-age=60
    3-POST /user/repos
        * Request Headers (Gửi đi):

            + Authorization: Bearer <YOUR_ACCESS_TOKEN> (Bắt buộc để xác thực người dùng)

            + Content-Type: application/json (Báo cho server biết body gửi lên là JSON)

            + Accept: application/vnd.github+json

        * Response Headers (Nhận về khi tạo thành công - 201 Created):
            + Location: https://api.github.com/repos/octocat/Hello-World

            + Content-Type: application/json; charset=utf-8
    4-PATCH /repos/{owner}/{repo}
        * Request Headers (Gửi đi):

            + Authorization: Bearer <YOUR_ACCESS_TOKEN>

            + Content-Type: application/json

            + Accept: application/vnd.github+json

        * Response Headers (Nhận về khi cập nhật thành công - 200 OK):

            + Content-Type: application/json; charset=utf-8

            + ETag: "a1b2c3d4..." (ETag mới sau khi dữ liệu đã thay đổi)

            + Cache-Control: private, max-age=60
    5-DELETE /repos/{owner}/{repo}
        * Request Headers (Gửi đi):

            + Authorization: Bearer <YOUR_ACCESS_TOKEN>

            + Accept: application/vnd.github+json

        * Response Headers (Nhận về khi xóa thành công - 204 No Content):

            + Không có Content-Type vì Response Body hoàn toàn rỗng đối với mã 204

            + X-RateLimit-Limit: 5000

            + X-RateLimit-Remaining: 4999

#4.Đánh giá 
    1.GET /users/{username} — Đạt chuẩn RESTful
        + Định danh tài nguyên bằng danh từ (/users) kết hợp tham số định danh ({username}).

        + Phương thức GET an toàn (Safe) và mang tính lặp lại (Idempotent).

        + Tối ưu hóa băng thông bằng các Header ETag và Cache-Control
    2.GET /users/{username}/repos — Đạt chuẩn RESTful
        + Cấu trúc đường dẫn thể hiện rõ ràng quan hệ phân cấp tài nguyên cha - con (/users $\rightarrow$ /repos).
        
        + Áp dụng nguyên lý HATEOAS thông qua Header Link để cung cấp các đường dẫn điều hướng phân trang (rel="next", rel="last").
    3.POST /user/repos — Đạt chuẩn RESTful
        + Sử dụng phương thức POST đúng bản chất cho thao tác tạo mới tài nguyên.

        + Phản hồi chuẩn HTTP Status 201 Created và kèm theo Header Location chứa đường dẫn tới tài nguyên vừa khởi tạo.
    4.PATCH /repos/{owner}/{repo} — Đạt chuẩn RESTful
        + Phân định chính xác giữa PATCH (Cập nhật một phần - Partial Update) và PUT (Thay thế toàn bộ tài nguyên).

        + Trả về đúng HTTP Status 200 OK cùng dữ liệu sau khi cập nhật thành công.
    5.DELETE /repos/{owner}/{repo} — Đạt chuẩn RESTful
        + Sử dụng phương thức DELETE cho thao tác xóa tài nguyên.

        + Trả về đúng mã 204 No Content và tối ưu băng thông bằng cách không gửi kèm response body dư thừa.