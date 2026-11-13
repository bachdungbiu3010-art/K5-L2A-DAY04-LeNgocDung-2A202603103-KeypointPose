# Lab Ngày 4 — Gán keypoint: skeleton 17 điểm COCO và 13 điểm khuôn mặt

> **Loại bài: CÁ NHÂN.** Bạn làm trên **CVAT cài ở máy mình từ Ngày 2**. Mỗi người nhận một **bộ ảnh riêng, chọn ngẫu nhiên theo MSSV**, tự review và tự nộp một repo riêng.

Bạn gán **skeleton 17 điểm COCO** cho **20 người** trong **12 ảnh** COCO và **skeleton 13 điểm** cho **8 khuôn mặt** trên CVAT. Mỗi điểm cần đúng tên, đúng chỗ và đúng cờ. Trái/phải tính theo chính người trong ảnh, không theo người xem. Cờ visibility gồm `v = 2` (thấy), `v = 1` (bị che nhưng ước lượng chắc), `v = 0` (ngoài ảnh hoặc không đoán được). Cuối buổi bạn tự review, xuất file **COCO Keypoints 1.0** và tự kiểm file bằng script.

Đây là loại nhãn mà model pose 2D (HRNet, RTMPose, YOLO-Pose, OpenPose…) học theo. Mỗi điểm `v > 0` thành một đỉnh heatmap. Cờ `v` quyết định điểm nào được tính vào loss. Cặp trái/phải được đổi tên khi lật ảnh để tăng dữ liệu. Lệch 3 px, đổi trái/phải hay một điểm đoán bừa đều được model học theo y như vậy.

## Mục tiêu học tập

Sau bài lab, bạn có thể:

1. Kiểm label Skeleton `person` (17 điểm COCO, 19 cạnh) và `face` (13 điểm của lab) trên CVAT: đúng tên, đúng thứ tự.
2. Gán 12 ảnh người và 8 ảnh khuôn mặt với trái/phải theo người trong ảnh, kể cả người quay lưng, người nghiêng và người chồng lên nhau.
3. Đặt cờ `v = 0 / 1 / 2` cho **từng điểm** theo bốn câu hỏi của buổi học. Không kéo điểm ngoài ảnh về mép, không đoán bừa.
4. Tự review nhãn của mình bằng năm mã lỗi `lr_swap`, `vis_flag`, `position`, `missing`, `extra`.
5. Xuất COCO Keypoints 1.0, đọc được mảng `keypoints` (51 số cho người, 39 số cho mặt), giải thích được vì sao OKS phạt lệch ở mắt nặng hơn lệch ở hông.

## Thông tin nhanh

| Mục | Giá trị |
|---|---|
| Loại bài | Cá nhân |
| Thời lượng | 240 phút (195′ làm bài + 15′ nghỉ + 30′ buffer) |
| Dữ liệu | 12 ảnh người COCO (5 nhóm khó dần, chia ngẫu nhiên theo MSSV từ kho 120 ảnh, mọi người cùng 20 người cần gán) và 8 ảnh khuôn mặt (chia theo loại từ kho 78 ảnh). Ảnh nằm sẵn trong repo, `lab.py` tạo task |
| Công cụ | CVAT trên máy bạn (cài ở Ngày 2, đang chạy bằng Docker), Python 3.8+ để chạy `lab.py`. Không cần cài thêm thư viện. Windows, macOS, Ubuntu đều chạy được |
| Deadline | **23:59 GMT+7 ngày làm lab**, trừ khi coach thông báo khác trong 48h sau lab. Xem [`SUBMISSION.md`](SUBMISSION.md) |
| Điểm | 100 điểm chính và tối đa 10 điểm bonus. Xem [`RUBRIC.md`](RUBRIC.md) |

## Chuẩn bị trước buổi

- [ ] Docker đang chạy và mở được CVAT của bạn ở http://localhost:8080 (tài khoản tạo ở Ngày 2).
- [ ] Đã chạy `python lab.py check` một lần ở nhà: lệnh tự bật CVAT, sửa các lỗi hay gặp, báo máy có đủ RAM không.
- [ ] Máy yếu (RAM 8 GB trở xuống, hoặc CVAT chạy chậm): đọc [`docs/MAY_YEU.md`](docs/MAY_YEU.md).
- [ ] Đã xem slide lý thuyết Ngày 4, nhất là phần 17 điểm COCO, câu hỏi trái/phải, cờ visibility và OKS.
- [ ] Đã xem [`docs/HUONG_DAN_BANG_HINH.md`](docs/HUONG_DAN_BANG_HINH.md) (10 phút, có ảnh), rồi đọc [`docs/GUIDELINE.md`](docs/GUIDELINE.md) và [`docs/CVAT_CHEATSHEET.md`](docs/CVAT_CHEATSHEET.md).
- [ ] Máy có Python 3.8+ (`python --version`; macOS / Ubuntu: `python3 --version`).

## Cách bắt đầu

1. Clone repo về máy, đặt luôn tên thư mục theo tên repo bài nộp (thay HoVaTen, MSSV của bạn):

   ```bash
   git clone https://github.com/VinUni-AI20k/K5-L2-KeypointPose.git K5-L2-DAY04-HoVaTen-MSSV-KeypointPose
   cd K5-L2-DAY04-HoVaTen-MSSV-KeypointPose
   ```

2. Mở Terminal (Windows: PowerShell) **trong thư mục repo**, chạy:

   ```bash
   python lab.py check
   python lab.py setup --mssv 20241234 --ten NguyenVanAn
   ```

   `check` kiểm và tự sửa CVAT. `setup` hỏi tài khoản CVAT của bạn, lấy bộ ảnh riêng của bạn (có sẵn trong repo, không cần mạng), tạo project `d04-keypoint` cùng hai task `persons-<ten>` và `faces-<ten>`, rồi in ra đường link mở job. macOS / Ubuntu: dùng `python3` thay cho `python`.
3. Đổi tên file báo cáo `report/individual/MSSV_HoTen.md` thành MSSV và họ tên của bạn, ví dụ `report/individual/20241234_NguyenVanAn.md`.
4. **Mới dùng CVAT?** Xem trước [`docs/HUONG_DAN_BANG_HINH.md`](docs/HUONG_DAN_BANG_HINH.md): ảnh chụp từng bước, ảnh thật cho từng quy tắc.
5. Đọc theo thứ tự: [`RULES.md`](RULES.md) → [`docs/GUIDELINE.md`](docs/GUIDELINE.md) → [`CHECKPOINTS.md`](CHECKPOINTS.md) → [`RUBRIC.md`](RUBRIC.md) → [`SUBMISSION.md`](SUBMISSION.md).
6. Gán nhãn theo CP0 → CP3. Xong thì chạy `python lab.py export` (CP4): lệnh xuất 2 file nộp vào `src/exports/` và tự kiểm.
7. Nộp bài: đưa repo lên GitHub của bạn và nộp **link repo** trên LMS (các lệnh ở `SUBMISSION.md`, mục "Nơi nộp"). Bài được chấm sau hạn nộp, không chấm tại lớp.

| Lệnh | Khi nào |
|---|---|
| `python lab.py check` | Đầu buổi, hoặc khi CVAT báo lỗi / đứng ở "Connecting…" |
| `python lab.py setup --mssv <MSSV> --ten <HoVaTen>` | Một lần, đầu buổi (chạy lại an toàn: không xóa nhãn đã gán) |
| `python lab.py setup --mssv <MSSV> --ten <HoVaTen> --bonus` | Khi làm bonus B1/B2 |
| `python lab.py export` | Cuối buổi (CP4), chạy lại được nhiều lần |
| `python lab.py lite` / `full` | Máy yếu: tắt / bật lại phần CVAT không dùng cho lab |
| `python lab.py stop` / `start` | Tắt CVAT sau buổi học cho máy nhẹ / bật lại |

## Lịch buổi thực hành

Mốc tính bằng phút kể từ lúc bắt đầu buổi thực hành (phút 0). Lịch này áp dụng cho cả lab sáng lẫn lab chiều. Với lab chiều bắt đầu 13:00, phút 105 là 14:45.

| Mốc phút | Thời lượng | Nội dung | Checkpoint |
|---|---:|---|---|
| 0–5 | 5′ | Chữa exit ticket buổi sáng | |
| 5–15 | 10′ | Ba luật, bộ 17 + 13 điểm, bảng cờ; kiểm label trong project | CP0 |
| 15–40 | 25′ | Coach demo CVAT: một người quay lưng bị xe che chân, đổi cờ từng điểm | CP0 |
| 40–45 | 5′ | Quiz thao tác (2 câu) | CP0 |
| 45–105 | 60′ | 10 ảnh người: `easy` (5), `occluded` (3), `back` (2). **Mốc phút 105: xong ít nhất 8 ảnh** | CP1 |
| 105–120 | 15′ | Nghỉ (bấm `Ctrl+S` trước khi nghỉ) | |
| 120–150 | 30′ | 2 ảnh người còn lại: `small`, `crowd`; hoàn thiện ảnh dở. **Mốc phút 150: đủ 12 ảnh** | CP1 |
| 150–180 | 30′ | 8 ảnh khuôn mặt, 13 điểm; self-QC | CP2 |
| 180–200 | 20′ | Tự review 5 ảnh người và 3 ảnh mặt | CP3 |
| 200–210 | 10′ | Xuất file, chạy script tự kiểm, chuyển job sang completed | CP4 |
| 210–240 | 30′ | Buffer: làm bù, sửa theo review, bonus; hoàn thiện báo cáo | Bonus |

## Cấu trúc repo

```text
K5-L2-DAY04-HoVaTen-MSSV-KeypointPose/
├── README.md              # trang này
├── lab.py                 # trợ lý: check, setup, export, lite, stop
├── RULES.md               # luật làm bài, AI, dữ liệu, nộp muộn
├── CHECKPOINTS.md         # CP0–CP4: làm gì, nộp gì, tự kiểm thế nào
├── RUBRIC.md              # cách chấm 100 điểm + bonus
├── SUBMISSION.md          # tên repo, file phải nộp, deadline, checklist
├── docs/
│   ├── HUONG_DAN_BANG_HINH.md  # hướng dẫn bằng ảnh chụp CVAT thật, ảnh minh họa từng quy tắc
│   ├── MAY_YEU.md         # máy yếu, Windows / macOS / Ubuntu, lỗi CVAT hay gặp
│   ├── GUIDELINE.md       # quy ước nhãn: 17 + 13 điểm, trái/phải, cờ v, ca khó
│   ├── CVAT_CHEATSHEET.md # vẽ skeleton, đổi cờ một điểm, xuất file
│   ├── COCO_KEYPOINTS.md  # đọc file COCO Keypoints 1.0, OKS
│   └── images/            # ảnh minh họa (nguồn: images/NGUON_ANH.md)
├── src/
│   ├── README.md
│   ├── check_submission.py     # script tự kiểm file xuất
│   ├── keypoint_schema.json    # tên điểm, cạnh, cặp trái/phải của 2 label
│   ├── lab/                    # pool.json (danh sách ảnh, không có đáp án), labels CVAT
│   └── exports/                # lab.py export ghi 2 file nộp + assignment.json vào đây
└── report/individual/
    ├── MSSV_HoTen.md           # ĐỔI TÊN rồi điền báo cáo
    └── images/                 # ảnh chụp màn hình cho báo cáo
```

## Dữ liệu và giấy phép

- **Ảnh người:** COCO train2017 / val2017 (Lin et al., 2014), giấy phép CC BY / CC BY-SA. Kho 120 ảnh (+ 20 ảnh bonus), từng ảnh đã được kiểm bằng mắt. `lab.py` chia cho mỗi học viên 12 ảnh (5 easy, 3 occluded, 2 back, 1 small, 1 crowd) theo MSSV: cùng MSSV luôn ra cùng bộ; với 300 học viên, hai người bất kỳ trùng trung bình khoảng 1 ảnh.
- **Ảnh khuôn mặt:** cắt quanh mặt từ ảnh COCO (CC BY / CC BY-SA). Mỗi học viên 8 ảnh chia theo MSSV: 3 mặt thẳng, 2 nghiêng, 1 kính trong, 1 kính râm, 1 tóc che. Nguồn, giấy phép từng ảnh: `src/lab/NGUON_ANH.md` và `src/lab/pool.json`.

Ảnh gốc nằm trong `src/lab/images/`; `setup` chép bộ của bạn vào `data/` (không commit). Khi xuất từ CVAT, `lab.py export` luôn tắt "Save images". Ảnh chụp màn hình trong báo cáo chỉ cắt vùng cần thiết và ghi nguồn "COCO 2017".

Đáp án chỉ coach giữ. **Không tìm đáp án COCO trên mạng để chép tọa độ**, không đổi MSSV để lấy bộ ảnh khác: coach tính lại bộ ảnh từ MSSV của bạn khi chấm.
