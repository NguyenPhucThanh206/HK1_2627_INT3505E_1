# Chạy từ thư mục gốc lab08-starter, API đang chạy ở cổng 5000.
#   powershell -ExecutionPolicy Bypass -File performance/run_scenarios.ps1
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force reports | Out-Null
$h = "http://127.0.0.1:5000"
Invoke-RestMethod "$h/health" | Out-Null   # fail sớm nếu API chưa chạy

locust -f performance/locustfile.py --headless -H $h -u 10  -r 2  -t 30s --html reports/A.html --csv reports/A
locust -f performance/locustfile.py --headless -H $h -u 50  -r 5  -t 60s --html reports/B.html --csv reports/B
locust -f performance/locustfile.py --headless -H $h -u 200 -r 50 -t 30s --html reports/C.html --csv reports/C
python performance/analyze.py
