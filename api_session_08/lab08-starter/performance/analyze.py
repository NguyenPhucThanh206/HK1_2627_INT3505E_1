"""Đọc reports/{A,B,C}_stats.csv (Locust --csv) -> bảng markdown + biểu đồ p95. Chạy từ gốc repo:
python performance/analyze.py"""
import csv
from pathlib import Path

USERS = {"A": 10, "B": 50, "C": 200}
SLO_P95 = 300
base = Path(__file__).resolve().parent.parent / "reports"


def load(tag):
    f = base / f"{tag}_stats.csv"
    return {r["Name"]: r for r in csv.DictReader(f.open(encoding="utf-8"))} if f.exists() else None


def row(tag, name, r):
    n, fail = int(r["Request Count"]), int(r["Failure Count"])
    ratio = fail / n if n else 0.0
    return (f"| {tag} | {USERS[tag]} | {name} | {n} | {float(r['Requests/s']):.1f} | {r['50%']} | "
            f"{r['95%']} | {r['99%']} | {ratio:.2%} |")


data = {t: load(t) for t in USERS}
print("| KB | users | endpoint | reqs | RPS | p50 | p95 | p99 | fail % |")
print("|----|------:|----------|-----:|----:|----:|----:|----:|-------:|")
for tag, stats in data.items():
    if not stats:
        print(f"| {tag} | – | (chưa có reports/{tag}_stats.csv) | | | | | | |")
        continue
    for name, r in stats.items():
        if name != "Aggregated":
            print(row(tag, name, r))
    print(row(tag, "**Aggregated**", stats["Aggregated"]))

pts = [(USERS[t], int(float(s["Aggregated"]["95%"]))) for t, s in data.items() if s]
if pts:
    print()
    for u, p in pts:
        print(f"p95 @ {u} users = {p}ms -> SLO p95<{SLO_P95}ms: {'ĐẠT' if p < SLO_P95 else 'KHÔNG ĐẠT'}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.plot(*zip(*pts), marker="o")
        plt.axhline(SLO_P95, color="red", ls="--", label=f"SLO {SLO_P95}ms")
        plt.xlabel("users"); plt.ylabel("p95 (ms)"); plt.legend(); plt.grid(alpha=.3)
        plt.savefig(base / "p95_vs_users.png", dpi=120, bbox_inches="tight")
        print("Đã lưu reports/p95_vs_users.png")
    except ImportError:
        print("(pip install matplotlib để vẽ biểu đồ p95 theo số user)")
