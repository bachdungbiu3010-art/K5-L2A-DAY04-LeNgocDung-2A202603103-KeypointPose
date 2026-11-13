#!/usr/bin/env python3
"""lab.py — trợ lý Lab Ngày 4 (Keypoint & Pose) trên CVAT cài sẵn ở máy bạn (từ Ngày 2).

Chạy từ thư mục gốc của repo, Python 3.8+, không cần cài thêm gì:

  python lab.py check                          kiểm và tự sửa CVAT (Docker, phân quyền, lỗi kẹt "Connecting...")
  python lab.py setup --mssv 20241234 --ten NguyenVanAn
                                               tạo project + 2 task với BỘ ẢNH NGẪU NHIÊN của riêng bạn
  python lab.py export                         xuất 2 file nộp vào src/exports/ và tự kiểm
  python lab.py lite                           máy yếu: tắt các phần CVAT không dùng (đỡ ~1 GB RAM)
  python lab.py full                           bật lại đầy đủ
  python lab.py stop | start                   tắt / bật toàn bộ CVAT (tắt sau buổi học cho máy nhẹ)

Trên macOS / Ubuntu dùng python3 thay cho python nếu máy báo không có lệnh python.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
import platform
import random
import re
import secrets
import shutil
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT / "src" / "lab"
EXPORTS = ROOT / "src" / "exports"
DATA = ROOT / "data"                       # ảnh tải về (không commit)
ASSIGN_FILE = EXPORTS / "assignment.json"  # bộ ảnh của bạn (commit cùng bài nộp)
PROJECT = "d04-keypoint"
CORE = ["cvat_db", "cvat_redis_inmem", "cvat_redis_ondisk", "cvat_opa", "traefik", "cvat_server", "cvat_ui",
        "cvat_worker_import", "cvat_worker_export", "cvat_worker_annotation", "cvat_worker_chunks", "cvat_worker_utils"]
OPTIONAL = ["cvat_clickhouse", "cvat_grafana", "cvat_vector", "cvat_worker_webhooks",
            "cvat_worker_quality_reports", "cvat_worker_consensus"]
UA = {"User-Agent": "AI20K-D04-lab/1.0 (education)"}

# ---------------------------------------------------------------------------------------------- in ra
def setup_console():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    if os.name == "nt":
        os.system("")  # bật màu ANSI trên Windows 10+


def ok(m):   print(f"  \033[32m[OK]\033[0m {m}")
def warn(m): print(f"  \033[33m[CHÚ Ý]\033[0m {m}")
def bad(m):  print(f"  \033[31m[LỖI]\033[0m {m}")
def step(m): print(f"\n\033[1m== {m}\033[0m")


def die(m, hint=None):
    bad(m)
    if hint:
        print("     " + hint.replace("\n", "\n     "))
    sys.exit(1)

# ---------------------------------------------------------------------------------------------- Docker
class Docker:
    """Gọi docker trực tiếp (Docker Desktop / Docker Engine) hoặc qua WSL (Windows cài Docker trong Ubuntu)."""

    def __init__(self):
        self.prefix = None
        cands = [["docker"]]
        if os.name == "nt":
            cands.append(["wsl", "-e", "docker"])
        for c in cands:
            try:
                r = subprocess.run(c + ["version", "--format", "{{.Server.Version}}"], capture_output=True, text=True, timeout=60)
                if r.returncode == 0 and r.stdout.strip():
                    self.prefix, self.version = c, r.stdout.strip()
                    break
            except (OSError, subprocess.TimeoutExpired):
                continue
        self.wsl = bool(self.prefix and self.prefix[0] == "wsl")

    def run(self, *args, timeout=600, check=False, input=None):
        r = subprocess.run(self.prefix + list(args), capture_output=True, text=True, timeout=timeout, input=input,
                           encoding="utf-8", errors="replace")
        if check and r.returncode != 0:
            raise RuntimeError(f"docker {' '.join(args)}: {r.stderr.strip()[:300]}")
        return r

    def out(self, *args, **kw):
        return self.run(*args, **kw).stdout.strip()

    def shell_in_dir(self, directory, cmd, input=None, timeout=900):
        """Chạy lệnh shell trong thư mục compose của CVAT (máy chạy Docker)."""
        if self.wsl:
            return subprocess.run(["wsl", "-e", "sh", "-c", f"cd '{directory}' && {cmd}"], capture_output=True, text=True,
                                  input=input, timeout=timeout, encoding="utf-8", errors="replace")
        if os.name == "nt":
            return subprocess.run(cmd, shell=True, cwd=directory, capture_output=True, text=True, input=input,
                                  timeout=timeout, encoding="utf-8", errors="replace")
        return subprocess.run(["sh", "-c", cmd], cwd=directory, capture_output=True, text=True, input=input,
                              timeout=timeout, encoding="utf-8", errors="replace")

    def containers(self):
        out = self.out("ps", "-a", "--filter", "name=cvat", "--filter", "name=traefik", "--format", "{{.Names}}\t{{.State}}")
        return dict(line.split("\t", 1) for line in out.splitlines() if "\t" in line)


def docker_or_die():
    d = Docker()
    if not d.prefix:
        sysname = platform.system()
        hint = {"Windows": "Mở Docker Desktop (biểu tượng cá voi), đợi chữ 'Engine running', rồi chạy lại.\n"
                           "Nếu Ngày 2 bạn cài Docker trong Ubuntu (WSL): mở Ubuntu, chạy 'sudo service docker start'.",
                "Darwin": "Mở ứng dụng Docker (Launchpad → Docker), đợi biểu tượng cá voi ngừng chuyển động, rồi chạy lại.",
                "Linux": "Chạy: sudo systemctl start docker   (hoặc sudo service docker start), rồi chạy lại.\n"
                         "Nếu báo 'permission denied': sudo usermod -aG docker $USER, đăng xuất rồi đăng nhập lại."}
        die("Không gọi được Docker.", hint.get(sysname, ""))
    return d

# ---------------------------------------------------------------------------------------------- HTTP / CVAT
class Cvat:
    def __init__(self, url):
        self.url = url.rstrip("/")
        self.h = {"Accept": "application/vnd.cvat+json"}

    def login(self, user=None):
        tok, sid = os.environ.get("CVAT_TOKEN"), os.environ.get("CVAT_SESSIONID")
        if tok:
            self.h["Authorization"] = f"Bearer {tok}"
        elif sid:  # chỉ dùng khi kiểm thử
            csrf = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            self.h.update({"Cookie": f"sessionid={sid}; csrftoken={csrf}", "X-CSRFToken": csrf, "Referer": self.url + "/"})
        else:
            print("  Đăng nhập CVAT bằng tài khoản bạn tạo ở Ngày 2 (mật khẩu không hiện khi gõ, không được lưu lại).")
            try:
                user = user or os.environ.get("CVAT_USER") or input("  Tên đăng nhập CVAT: ").strip()
                pw = os.environ.get("CVAT_PASSWORD") or getpass.getpass("  Mật khẩu CVAT: ")
            except EOFError:
                die("Không nhập được tên đăng nhập / mật khẩu.", "Chạy lệnh trong một cửa sổ Terminal / PowerShell bình thường để gõ được.")
            self.h["Authorization"] = "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()
        try:
            me = self.get("/api/users/self")
        except RuntimeError as e:
            die("Đăng nhập không được.", "Kiểm lại tên đăng nhập / mật khẩu (thử đăng nhập trên trình duyệt "
                f"{self.url}). Quên mật khẩu: hỏi LC cách tạo lại tài khoản.\n({e})")
        ok(f"Đăng nhập: {me['username']}")
        return me

    def req(self, method, path, data=None, headers=None, raw=False, timeout=120):
        h = dict(self.h); h.update(headers or {})
        body = None
        if isinstance(data, (bytes, bytearray)):
            body = data
        elif data is not None:
            body = json.dumps(data).encode(); h["Content-Type"] = "application/json"
        r = urllib.request.Request(path if path.startswith("http") else self.url + path, data=body, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, timeout=timeout) as resp:
                c = resp.read()
                return c if raw else (json.loads(c) if c else {})
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} {method} {path}: {e.read()[:300].decode('utf-8', 'replace')}") from None

    def get(self, p, **kw): return self.req("GET", p, **kw)
    def post(self, p, d=None, **kw): return self.req("POST", p, d if d is not None else {}, **kw)
    def patch(self, p, d, **kw): return self.req("PATCH", p, d, **kw)

    def all(self, path):
        sep = "&" if "?" in path else "?"
        out, page = [], 1
        while True:
            d = self.get(f"{path}{sep}page_size=100&page={page}")
            out += d.get("results", [])
            if not d.get("next"):
                return out
            page += 1

    def project(self, name):
        for p in self.all(f"/api/projects?search={urllib.parse.quote(name)}"):
            if p["name"] == name:
                return p

    def task(self, pid, name):
        for t in self.all(f"/api/tasks?project_id={pid}&search={urllib.parse.quote(name)}"):
            if t["name"] == name:
                return t

    def upload(self, tid, files, quality):
        b = "----lab" + uuid.uuid4().hex
        parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
                 for k, v in {"image_quality": str(quality), "sorting_method": "lexicographical"}.items()]
        for i, f in enumerate(files):
            parts.append((f'--{b}\r\nContent-Disposition: form-data; name="client_files[{i}]"; filename="{f.name}"\r\n'
                          f'Content-Type: image/jpeg\r\n\r\n').encode() + f.read_bytes() + b"\r\n")
        parts.append(f"--{b}--\r\n".encode())
        self.req("POST", f"/api/tasks/{tid}/data", b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={b}"}, timeout=900)
        for _ in range(900):
            t = self.get(f"/api/tasks/{tid}")
            if t.get("size"):
                return t
            time.sleep(1)
        raise RuntimeError("CVAT xử lý ảnh quá 15 phút")

    def export(self, tid, fmt="COCO Keypoints 1.0"):
        q = urllib.parse.urlencode({"format": fmt, "save_images": "false"})
        rq = self.post(f"/api/tasks/{tid}/dataset/export?{q}").get("rq_id")
        for _ in range(900):
            st = self.get(f"/api/requests/{urllib.parse.quote(rq, safe='')}")
            if st.get("status") == "finished":
                return self.get(st["result_url"], raw=True, timeout=600)
            if st.get("status") == "failed":
                raise RuntimeError(st.get("message"))
            time.sleep(1)
        raise RuntimeError("export quá 15 phút")


def http_ok(url, timeout=5):
    try:
        with urllib.request.urlopen(url + "/api/server/about", timeout=timeout) as r:
            return json.loads(r.read()).get("version")
    except Exception:
        return None


def wait_server(url, seconds=300):
    t0 = time.time()
    while time.time() - t0 < seconds:
        v = http_ok(url)
        if v:
            return v
        time.sleep(3)
    return None

# ---------------------------------------------------------------------------------------------- check / sửa
def opa_policies(d):
    out = d.out("exec", "cvat_server", "sh", "-c", "curl -s -m 5 http://opa:8181/v1/policies", timeout=60)
    return out.count('"id"')


def compose_dir(d):
    return d.out("inspect", "-f", '{{ index .Config.Labels "com.docker.compose.project.working_dir" }}', "cvat_server")


def cmd_check(args, quiet=False):
    step("1. Docker")
    d = docker_or_die()
    ok(f"Docker {d.version}" + (" (trong WSL)" if d.wsl else ""))
    mem = d.out("info", "--format", "{{.MemTotal}}")
    mem_gb = int(mem) / 2**30 if mem.isdigit() else 0
    if mem_gb:
        (ok if mem_gb >= 5.5 else warn)(f"Docker được dùng {mem_gb:.1f} GB RAM" +
            ("" if mem_gb >= 5.5 else " — ít. Chạy 'python lab.py lite' và đóng bớt ứng dụng (xem docs/MAY_YEU.md)"))

    step("2. CVAT (cài ở Ngày 2)")
    cs = d.containers()
    if "cvat_server" not in cs:
        die("Không thấy CVAT trên máy (không có container cvat_server).",
            "CVAT của Ngày 2 đã bị xóa hoặc cài trên máy khác. Báo LC; cách cài lại ở docs/MAY_YEU.md mục 4.")
    cdir = compose_dir(d)
    stopped = [n for n in CORE if cs.get(n) != "running"]
    if stopped:
        warn("Đang tắt: " + ", ".join(stopped) + " → bật lại...")
        r = d.run("start", *[n for n in CORE if n in cs], timeout=600)
        if r.returncode != 0 and cdir:
            d.shell_in_dir(cdir, "docker compose up -d {0} || docker-compose up -d {0}".format(" ".join(CORE)))
    ver = wait_server(args.url)
    if not ver:
        die(f"CVAT chưa trả lời ở {args.url} sau 5 phút.",
            "Máy yếu có thể cần lâu hơn: đợi thêm rồi chạy lại 'python lab.py check'.\n"
            "Vẫn không được: chụp màn hình và báo LC.")
    ok(f"CVAT {ver} tại {args.url}" + (f" (thư mục {cdir})" if cdir else ""))
    if not ver.startswith("2."):
        warn("Lab viết cho CVAT 2.x; bản khác có thể khác tên menu.")

    step("3. Phân quyền (OPA)")
    n = opa_policies(d)
    if n:
        ok(f"OPA đã nạp {n} quy tắc")
    else:
        warn("OPA chưa nạp quy tắc → CVAT sẽ báo lỗi 500. Đang khởi động lại cvat_opa...")
        d.run("restart", "cvat_opa", timeout=180)
        for _ in range(40):
            n = opa_policies(d)
            if n: break
            time.sleep(3)
        ok(f"OPA đã nạp {n} quy tắc") if n else bad("OPA vẫn chưa nạp được. Báo LC.")

    step("4. Lỗi kẹt \"Connecting...\" (Nuclio)")
    has_nuclio = any("nuclio" in name for name in cs)
    ip = d.out("exec", "cvat_server", "sh", "-c", "getent hosts nuclio | awk '{print $1}'", timeout=60)
    if has_nuclio:
        ok("Có Nuclio đang chạy")
    elif not ip or ip.startswith("127."):
        ok("Không ảnh hưởng (tên nuclio không trỏ ra ngoài)")
    else:
        warn(f"Tên 'nuclio' bị mạng trỏ sang {ip} → giao diện CVAT có thể đứng ở 'Connecting...' tới 2 phút. Đang sửa...")
        fixed = False
        if cdir and not getattr(args, "no_persist", False):
            ov = "docker-compose.override.yml"
            r = d.shell_in_dir(cdir, f"test -e {ov} && echo YES || echo NO")
            if "NO" in r.stdout:
                content = 'services:\n  cvat_server:\n    extra_hosts:\n      - "nuclio:127.0.0.1"\n'
                d.shell_in_dir(cdir, f"cat > {ov}", input=content)
                r = d.shell_in_dir(cdir, "docker compose up -d cvat_server || docker-compose up -d cvat_server")
                fixed = r.returncode == 0
                if fixed:
                    ok(f"Đã thêm {ov} (trỏ nuclio về 127.0.0.1) và khởi động lại cvat_server")
                    wait_server(args.url)
                    for _ in range(30):
                        if opa_policies(d): break
                        time.sleep(3)
                    else:
                        d.run("restart", "cvat_opa", timeout=180)
            else:
                warn(f"Đã có {ov} trong {cdir}: không ghi đè. Dùng cách sửa tạm.")
        if not fixed:
            d.run("exec", "-u", "root", "cvat_server", "sh", "-c", "grep -q ' nuclio' /etc/hosts || echo '127.0.0.1 nuclio' >> /etc/hosts")
            ok("Đã sửa tạm (mất khi CVAT khởi động lại; khi đó chạy lại 'python lab.py check')")

    step("5. Dung lượng")
    free = shutil.disk_usage(ROOT).free / 2**30
    (ok if free > 2 else warn)(f"Ổ chứa repo còn {free:.1f} GB trống")
    opt_on = [n for n in OPTIONAL if d.containers().get(n) == "running"]
    if opt_on and mem_gb and mem_gb < 7:
        warn("Máy ít RAM: chạy 'python lab.py lite' để tắt " + ", ".join(opt_on))
    if d.wsl:
        warn("CVAT chạy trong WSL: để một cửa sổ PowerShell chạy 'wsl -e sleep infinity' trong lúc làm bài, "
             "nếu không WSL có thể tự tắt khi rảnh.")
    print("\n\033[32mCVAT sẵn sàng.\033[0m Mở trình duyệt: " + args.url)
    return d

# ---------------------------------------------------------------------------------------------- chia ảnh
def norm_mssv(m):
    return re.sub(r"\s+", "", str(m)).upper()


def assignment(pool, mssv):
    """Chia ảnh ngẫu nhiên nhưng CỐ ĐỊNH theo MSSV (chạy lại vẫn ra đúng bộ đó; coach tính lại được)."""
    seed = int(hashlib.sha256(f"{pool['version']}:{norm_mssv(mssv)}".encode()).hexdigest(), 16)
    rng = random.Random(seed)
    chosen = []
    for group, q in pool["quota"].items():
        ids = sorted(p["file"] for p in pool["persons"] if p["group"] == group)
        chosen += sorted(rng.sample(ids, q))
    faces = []
    if pool.get("face_quota"):
        for kind, q in pool["face_quota"].items():
            ids = sorted(f["file"] for f in pool["faces"] if f["kind"] == kind)
            faces += sorted(rng.sample(ids, q))
    else:
        faces = [f["file"] for f in pool["faces"]]
    eq = pool.get("extra_quota", {"persons": 3, "faces": len(pool["faces_extra"])})
    extra = sorted(rng.sample(sorted(p["file"] for p in pool["persons_extra"]), min(eq["persons"], len(pool["persons_extra"]))))
    fextra = sorted(rng.sample(sorted(f["file"] for f in pool["faces_extra"]), min(eq["faces"], len(pool["faces_extra"]))))
    return {"persons": chosen, "faces": faces, "persons_extra": extra, "faces_extra": fextra}


BUNDLED = LAB / "images"  # ảnh kèm sẵn trong repo (không cần mạng)


def download(items, dest, images_dir=None):
    dest.mkdir(parents=True, exist_ok=True)
    for it in items:
        f = dest / it["file"]
        if f.exists() and f.stat().st_size > 1000:
            continue
        if (BUNDLED / it["file"]).exists():
            shutil.copy(BUNDLED / it["file"], f); continue
        if images_dir:
            src = next(Path(images_dir).rglob(it["file"]), None)
            if src:
                shutil.copy(src, f); continue
        for attempt in range(4):
            try:
                req = urllib.request.Request(it["url"], headers=UA)
                with urllib.request.urlopen(req, timeout=60) as r:
                    f.write_bytes(r.read())
                break
            except Exception as e:
                if attempt == 3:
                    die(f"Không tải được {it['file']} ({e}).",
                        "Mạng chậm hoặc bị chặn: xin LC thư mục ảnh (USB / Drive) rồi chạy lại với --images-dir <thư mục>.")
                time.sleep(3 + 4 * attempt)
        time.sleep(0.3)
    return [dest / it["file"] for it in items]


def load_pool():
    return json.loads((LAB / "pool.json").read_text(encoding="utf-8"))


def safe_name(s):
    s = re.sub(r"[^A-Za-z0-9]", "", s)
    if not s:
        die("--ten phải là họ tên không dấu, không khoảng trắng, ví dụ NguyenVanAn")
    return s


def cmd_setup(args):
    ten, mssv = safe_name(args.ten), norm_mssv(args.mssv)
    if ASSIGN_FILE.exists():
        old = json.loads(ASSIGN_FILE.read_text(encoding="utf-8"))
        if norm_mssv(old.get("mssv")) != mssv and not args.force:
            die(f"src/exports/assignment.json đang là của MSSV {old.get('mssv')}.", "Sai MSSV? Thêm --force nếu chắc chắn muốn đổi.")
    if not args.skip_check:
        cmd_check(args)
    pool = load_pool()
    a = assignment(pool, mssv)
    step("6. Bộ ảnh của bạn (ngẫu nhiên theo MSSV)")
    by = {p["file"]: p for p in pool["persons"] + pool["persons_extra"]}
    fby = {f["file"]: f for f in pool["faces"] + pool["faces_extra"]}
    for g in pool["quota"]:
        print(f"  {g:9s} " + ", ".join(f for f in a["persons"] if by[f]["group"] == g))
    print(f"  faces     {len(a['faces'])} ảnh (3 thẳng, 2 nghiêng, 1 kính trong, 1 kính râm, 1 tóc che)")
    sets = [("persons", [by[f] for f in a["persons"]]), ("faces", [fby[f] for f in a["faces"]])]
    if args.bonus:
        sets += [("persons-extra", [by[f] for f in a["persons_extra"]]), ("faces-extra", [fby[f] for f in a["faces_extra"]])]
    step("7. Chuẩn bị ảnh (lấy từ src/lab/images trong repo)")
    files = {}
    for kind, items in sets:
        files[kind] = download(items, DATA / kind, args.images_dir)
        ok(f"{kind}: {len(files[kind])} ảnh trong data/{kind}/")

    step("8. Tạo project và task trên CVAT")
    cv = Cvat(args.url)
    me = cv.login(args.user)
    proj = cv.project(args.project)
    if not proj:
        labels = json.loads((LAB / "labels_d04_keypoint.json").read_text(encoding="utf-8"))
        proj = cv.post("/api/projects", {"name": args.project, "labels": labels})
        ok(f"Đã tạo project {args.project}")
    else:
        names = {l["name"] for l in cv.all(f"/api/labels?project_id={proj['id']}") if not l.get("parent_id")}
        if not {"person", "face"} <= names:
            die(f"Project {args.project} đã có nhưng thiếu label person/face.", "Xóa project đó trên CVAT (hoặc đổi tên) rồi chạy lại.")
        ok(f"Project {args.project} đã có")
    jobs = {}
    for kind, items in sets:
        name = f"{kind}-{ten}"
        t = cv.task(proj["id"], name)
        if not t:
            print(f"  Đang tạo {name} và tải {len(items)} ảnh lên CVAT (máy yếu có thể mất vài phút)...")
            t = cv.post("/api/tasks", {"name": name, "project_id": proj["id"]})
            cv.upload(t["id"], files[kind], args.quality)
            ok(f"Đã tạo {name}")
        else:
            ok(f"{name} đã có, giữ nguyên nhãn bạn đã gán")
        js = cv.all(f"/api/jobs?task_id={t['id']}")
        for j in js:
            if not j.get("assignee"):
                cv.patch(f"/api/jobs/{j['id']}", {"assignee": me["id"]})
        jobs[kind] = {"task_id": t["id"], "job_id": js[0]["id"] if js else None, "task_name": name}

    EXPORTS.mkdir(parents=True, exist_ok=True)
    rec = {"mssv": mssv, "ten": ten, "pool_version": pool["version"], "cvat_user": me["username"], "project": args.project,
           "persons": a["persons"], "faces": a["faces"], "tasks": jobs}
    if args.bonus:
        rec.update({"persons_extra": a["persons_extra"], "faces_extra": a["faces_extra"]})
    ASSIGN_FILE.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    ok("Đã ghi src/exports/assignment.json (commit file này cùng bài nộp)")
    print("\n\033[32mXong.\033[0m Mở các job sau trong trình duyệt và bắt đầu gán (CP1, CP2):")
    for kind, j in jobs.items():
        if j["job_id"]:
            print(f"  {kind:14s} {args.url}/tasks/{j['task_id']}/jobs/{j['job_id']}")

# ---------------------------------------------------------------------------------------------- export
def cmd_export(args):
    if not ASSIGN_FILE.exists():
        die("Chưa có src/exports/assignment.json.", "Chạy 'python lab.py setup --mssv ... --ten ...' trước.")
    rec = json.loads(ASSIGN_FILE.read_text(encoding="utf-8"))
    if not http_ok(args.url):
        warn("CVAT chưa chạy, đang kiểm và bật...")
        cmd_check(args)
    cv = Cvat(args.url)
    cv.login(args.user)
    step("Xuất COCO Keypoints 1.0")
    made = []
    for kind, j in rec["tasks"].items():
        out = EXPORTS / f"{rec['ten']}_{'bonus_' if 'extra' in kind else ''}{kind.replace('-extra', '')}.zip"
        try:
            out.write_bytes(cv.export(j["task_id"]))
            ok(f"{out.relative_to(ROOT)}")
            made.append((kind, out))
        except RuntimeError as e:
            bad(f"{kind}: {e}")
        try:
            jobs = cv.all(f"/api/jobs?task_id={j['task_id']}")
            if any(x.get("state") != "completed" for x in jobs):
                warn(f"Job {j['task_name']} chưa 'completed': khi xong, trong job bấm Menu → Finish the job.")
        except RuntimeError:
            pass
    main = {k: p for k, p in made if "extra" not in k}
    if "persons" in main or "faces" in main:
        step("Tự kiểm (src/check_submission.py)")
        cmd = [sys.executable, str(ROOT / "src" / "check_submission.py")]
        if "persons" in main: cmd += ["--persons", str(main["persons"]), "--expected-person-images", str(len(rec["persons"]))]
        if "faces" in main: cmd += ["--faces", str(main["faces"]), "--expected-face-images", str(len(rec["faces"]))]
        sys.stdout.flush()
        subprocess.run(cmd)

# ---------------------------------------------------------------------------------------------- lite / full / stop / start
def cmd_lite(args):
    d = docker_or_die()
    on = [n for n in OPTIONAL if d.containers().get(n) == "running"]
    if on:
        d.run("stop", *on, timeout=300)
    ok("Đã tắt phần không dùng cho lab: " + (", ".join(on) if on else "(đã tắt từ trước)"))
    print("  Bật lại đầy đủ: python lab.py full")


def cmd_full(args):
    d = docker_or_die()
    names = [n for n in OPTIONAL if n in d.containers()]
    d.run("start", *names, timeout=300)
    ok("Đã bật: " + ", ".join(names))


def cmd_stop(args):
    d = docker_or_die()
    names = [n for n in d.containers() if n.startswith("cvat") or n == "traefik"]
    d.run("stop", *names, timeout=600)
    ok("Đã tắt CVAT. Bật lại: python lab.py start")


def cmd_start(args):
    d = docker_or_die()
    d.run("start", *[n for n in CORE if n in d.containers()], timeout=600)
    cmd_check(args)

# ---------------------------------------------------------------------------------------------- main
def main():
    setup_console()
    if sys.version_info < (3, 8):
        die("Cần Python 3.8 trở lên.")
    ap = argparse.ArgumentParser(description="Trợ lý Lab Ngày 4 trên CVAT cục bộ")
    ap.add_argument("--url", default=os.environ.get("CVAT_URL", "http://localhost:8080"), help="địa chỉ CVAT (mặc định localhost:8080)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="kiểm và tự sửa CVAT")
    c.add_argument("--no-persist", action="store_true", help="chỉ sửa tạm, không ghi docker-compose.override.yml")
    s = sub.add_parser("setup", help="tạo project + task với bộ ảnh của bạn")
    s.add_argument("--mssv", required=True)
    s.add_argument("--ten", required=True, help="họ tên không dấu, ví dụ NguyenVanAn")
    s.add_argument("--user", help="tên đăng nhập CVAT (không có thì hỏi)")
    s.add_argument("--bonus", action="store_true", help="tạo thêm task bonus B1/B2")
    s.add_argument("--images-dir", help="thư mục ảnh LC phát (khi mạng chậm)")
    s.add_argument("--quality", type=int, default=75, help="chất lượng ảnh trên CVAT, máy yếu để 60")
    s.add_argument("--project", default=PROJECT)
    s.add_argument("--skip-check", action="store_true")
    s.add_argument("--force", action="store_true")
    e = sub.add_parser("export", help="xuất file nộp vào src/exports/ và tự kiểm")
    e.add_argument("--user")
    for c in ("lite", "full", "stop", "start"):
        sub.add_parser(c)
    args = ap.parse_args()
    {"check": cmd_check, "setup": cmd_setup, "export": cmd_export, "lite": cmd_lite, "full": cmd_full,
     "stop": cmd_stop, "start": cmd_start}[args.cmd](args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nĐã dừng.")
