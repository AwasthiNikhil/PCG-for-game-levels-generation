"""Smoke-check every generator through the JSON API: python check_generators.py (from the repo root)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))  # model paths are relative to api/
from main2 import app

client = app.test_client()
cases = [(t, "") for t in range(1, 8)] + [
    (6, "?max_rooms=15&max_room_size=40"),    # oversized rooms used to crash
    (6, "?x=8&y=8&min_room_size=6"),           # tiny grid
    (3, "?seed=7&scale=6&threshold=10"),
]
failed = 0
for t, q in cases:
    r = client.get(f"/generate/{t}{q}")
    grid = r.get_json().get("grid", []) if r.status_code == 200 else []
    cells = [c for row in grid for c in row]
    floor = cells.count("1") / len(cells) if cells else 0
    ok = r.status_code == 200 and cells and 0.05 < floor < 0.95
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'}  type {t}{q:42} HTTP {r.status_code}  floor {floor:.0%}")
sys.exit(failed)
