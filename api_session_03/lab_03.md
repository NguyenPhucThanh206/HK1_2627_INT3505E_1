curl 'localhost:5000/orders?status=paid' == ![alt text](image-8.png)
curl 'localhost:5000/orders?limit=2'     == ![alt text](image-9.png)
curl 'localhost:5000/orders?fields=id,total' == ![alt text](image-10.png)
Test cursor hỏng để nhận lỗi HTTP 400    == ![alt text](image-11.png)