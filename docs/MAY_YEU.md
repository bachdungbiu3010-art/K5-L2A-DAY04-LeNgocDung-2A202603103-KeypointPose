# Máy yếu, Windows / macOS / Ubuntu và lỗi CVAT hay gặp

Lab này chạy trên **CVAT cài ở máy bạn từ Ngày 2**. Trang này giúp CVAT chạy ổn trên mọi loại máy. Gặp lỗi gì, việc đầu tiên luôn là:

```bash
python lab.py check
```

(macOS / Ubuntu: `python3 lab.py check`.) Lệnh tự bật CVAT, tự sửa 3 lỗi hay gặp nhất và nói rõ còn thiếu gì.

## 1. Máy cần bao nhiêu

Số đo thật trên CVAT 2.82:

| Chế độ | RAM CVAT dùng | Khi nào |
|---|---:|---|
| Đầy đủ (mặc định) | khoảng 3,3 GB | Máy RAM từ 16 GB |
| **Lite** (`python lab.py lite`) | khoảng 2,2 GB | Máy RAM 8 GB, hoặc thấy máy chậm |

Lite chỉ tắt phần thống kê và vài worker lab không dùng (clickhouse, grafana, vector, webhooks, quality reports, consensus). Gán nhãn, lưu, export vẫn chạy bình thường (đã thử). Bật lại: `python lab.py full`.

Ổ đĩa: ảnh của lab nằm sẵn trong repo (khoảng 35 MB). CVAT đã cài từ Ngày 2 nên không phải tải thêm gì, không cần mạng khi chạy `setup`.

## 2. Mẹo cho máy yếu (RAM 8 GB trở xuống)

1. Chạy `python lab.py lite` trước khi bắt đầu.
2. Đóng bớt ứng dụng: Zoom/Teams, game, các tab trình duyệt không cần. **Chỉ mở một tab CVAT.**
3. Trong CVAT, khóa (`L`) các skeleton đã gán xong để giao diện nhẹ và khỏi kéo nhầm.
4. `setup` có tùy chọn `--quality 60` để ảnh trên CVAT nhẹ hơn (ảnh lab vốn nhỏ, thường không cần).
5. Sau buổi học: `python lab.py stop` để trả RAM cho máy. Lần sau `python lab.py start`.
6. Giới hạn RAM cho Docker (để máy không bị đơ):
   - **Windows + Docker Desktop:** Docker Desktop dùng WSL2. Tạo file `%UserProfile%\.wslconfig` với nội dung dưới, rồi chạy `wsl --shutdown` và mở lại Docker Desktop:

     ```ini
     [wsl2]
     memory=4GB
     ```

     Máy 8 GB để `memory=4GB`; máy 16 GB để `6GB`.
   - **macOS + Docker Desktop:** Settings → Resources → Memory: kéo về 4 GB (máy 8 GB) hoặc 6 GB (máy 16 GB) → Apply & restart.
   - **Ubuntu (Docker Engine):** không cần chỉnh; Docker dùng thẳng RAM của máy.

## 3. Theo từng hệ điều hành

| | Windows | macOS | Ubuntu |
|---|---|---|---|
| Mở Terminal | PowerShell (Start → gõ PowerShell), `cd` vào thư mục repo | Terminal (Cmd+Space → Terminal) | Terminal (Ctrl+Alt+T) |
| Lệnh Python | `python lab.py <lệnh>` | `python3 lab.py <lệnh>` | `python3 lab.py <lệnh>` |
| Docker chưa chạy | Mở Docker Desktop, đợi "Engine running" | Mở ứng dụng Docker, đợi cá voi ngừng chuyển động | `sudo systemctl start docker` |
| Báo "permission denied" | (ít gặp) chạy PowerShell bình thường, không cần Admin | (ít gặp) | `sudo usermod -aG docker $USER`, đăng xuất rồi đăng nhập lại |

**Windows, CVAT cài trong Ubuntu (WSL), không dùng Docker Desktop:** `lab.py` tự nhận ra và gọi Docker qua WSL. WSL có thể tự tắt khi không còn cửa sổ nào, kéo CVAT tắt theo. Trong lúc làm bài, mở thêm một cửa sổ PowerShell và để chạy:

```powershell
wsl -e sleep infinity
```

Muốn cố định, thêm vào `%UserProfile%\.wslconfig` rồi chạy `wsl --shutdown`:

```ini
[wsl2]
vmIdleTimeout=-1
```

**Python chưa có:** Windows cài từ python.org (tick "Add python.exe to PATH") hoặc Microsoft Store; macOS chạy `xcode-select --install` hoặc cài từ python.org; Ubuntu đã có sẵn `python3`.

## 4. Lỗi hay gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| Trình duyệt đứng ở **"Connecting…"** lâu | Mạng trỏ tên `nuclio` (phần AI tự gán của CVAT, lab không dùng) ra ngoài, CVAT chờ 2 phút | `python lab.py check`: tự thêm `docker-compose.override.yml` trỏ `nuclio` về máy mình |
| Mọi thao tác báo lỗi **500** | Phần phân quyền (OPA) khởi động trước server | `python lab.py check`: tự khởi động lại `cvat_opa` |
| Mở http://localhost:8080 không được | CVAT đang tắt (sau khi tắt máy / tắt Docker) | `python lab.py start` |
| CVAT tự tắt giữa buổi (Windows + WSL) | WSL tắt khi rảnh | Mục 3: `wsl -e sleep infinity` |
| Quên mật khẩu CVAT | | Chạy (thay `<tên>`): `docker exec -it cvat_server bash -ic "python3 ~/manage.py changepassword <tên>"`; quên cả tên: `docker exec -it cvat_server bash -ic "python3 ~/manage.py createsuperuser"` |
| `setup` báo thiếu ảnh | Repo clone thiếu (mạng đứt giữa chừng) | Clone lại repo, hoặc xin LC thư mục ảnh rồi chạy `python lab.py setup --mssv <MSSV> --ten <HoVaTen> --images-dir <thư mục>` |
| `lab.py check` báo không có CVAT | CVAT Ngày 2 đã bị xóa | Cài lại theo hướng dẫn chính thức (mục 5), hoặc báo LC để làm chung máy với bạn |
| Máy quá yếu, CVAT không chạy nổi kể cả lite | | Báo LC: làm cùng máy với một bạn (mỗi người một task riêng trên cùng CVAT, `setup` với MSSV của từng người) |

## 5. Cài lại CVAT (chỉ khi CVAT Ngày 2 đã mất)

Theo hướng dẫn chính thức của CVAT (cần Docker và Git, tải khoảng 6 GB):

```bash
git clone https://github.com/cvat-ai/cvat --branch v2.82.0 --depth 1
cd cvat
docker compose up -d
docker exec -it cvat_server bash -ic "python3 ~/manage.py createsuperuser"
```

Rồi quay lại repo lab, chạy `python lab.py check`.
