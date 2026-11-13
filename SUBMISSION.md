# Submission

## Loại bài

**Cá nhân.** Mỗi học viên tự nộp repo của mình.

## Tên repo

Repo đề bài (dùng chung cho level 2):

```text
K5-L2-KeypointPose
```

Repo bài nộp của bạn:

```text
K5-L2-DAY04-HoVaTen-MSSV-KeypointPose
```

Ví dụ: `K5-L2-DAY04-NguyenVanAn-20241234-KeypointPose`.

- Viết không dấu, không khoảng trắng; ngăn cách các phần bằng dấu `-`.
- Ngày học dùng hai chữ số: `DAY04`.
- Nếu lớp bạn tách A / B và coach yêu cầu, thay `L2` bằng `L2A` hoặc `L2B`.

## Cấu trúc và file phải nộp

```text
K5-L2-DAY04-HoVaTen-MSSV-KeypointPose/
├── src/exports/
│   ├── assignment.json              # BẮT BUỘC: do lab.py setup tạo (MSSV + bộ ảnh của bạn), không sửa tay
│   ├── HoVaTen_persons.zip          # BẮT BUỘC: COCO Keypoints 1.0, task persons, không kèm ảnh (lab.py export tạo)
│   ├── HoVaTen_faces.zip            # BẮT BUỘC: COCO Keypoints 1.0, task faces, không kèm ảnh (lab.py export tạo)
│   ├── HoVaTen_bonus_persons.zip    # chỉ khi làm bonus B1
│   └── HoVaTen_bonus_faces.zip      # chỉ khi làm bonus B2
└── report/individual/
    ├── 20241234_NguyenVanAn.md      # BẮT BUỘC: đổi tên từ MSSV_HoTen.md
    └── images/                      # BẮT BUỘC: 4 ảnh chụp màn hình
```

| File | Yêu cầu |
|---|---|
| `src/exports/assignment.json` | Tạo bởi `python lab.py setup`. Coach dùng MSSV trong file để tính lại bộ ảnh của bạn khi chấm |
| `src/exports/HoVaTen_persons.zip` | `python lab.py export` tạo tự động (`HoVaTen` = giá trị `--ten` bạn nhập). Xuất từ task `persons-<tên>`, định dạng **COCO Keypoints 1.0**, bỏ chọn Save images. Bên trong có `annotations/person_keypoints_default.json` |
| `src/exports/HoVaTen_faces.zip` | Xuất từ task `faces-<tên>`, cùng định dạng, bỏ chọn Save images |
| `report/individual/MSSV_HoTen.md` | Đổi tên theo MSSV và họ tên không dấu, ví dụ `20241234_NguyenVanAn.md`. Điền đủ mục 0–8 |
| `report/individual/images/` | 4 ảnh: `1_label_person.png`, `2_nguoi_quay_lung.png`, `3_mat_phong_to.png`, `4_json_export.png` (chi tiết ở báo cáo mục 6) |

Ngoài repo, trên CVAT: hai job của bạn phải ở trạng thái **completed**.

**Không nộp:** thư mục `data/` (ảnh tải về), ảnh gốc COCO hay Wikimedia, annotation COCO gốc, file `.env`, mật khẩu.

## Nơi nộp

Bạn đã clone repo đề bài về thư mục `K5-L2-DAY04-HoVaTen-MSSV-KeypointPose` (README, bước 1). Để nộp:

1. Trên GitHub, tạo một repo **trống** (không tick README, .gitignore, license) tên đúng `K5-L2-DAY04-HoVaTen-MSSV-KeypointPose`. Chế độ private hay public và tài khoản chấm bài cần mời: làm theo thông báo của LC (mặc định: private, mời tài khoản chấm bài vào repo với quyền Read).
2. Trong thư mục repo trên máy, trỏ về repo của bạn và đẩy lên (thay `<tai-khoan>` bằng tài khoản GitHub của bạn):

   ```bash
   git remote set-url origin https://github.com/<tai-khoan>/K5-L2-DAY04-HoVaTen-MSSV-KeypointPose.git
   git add -A
   git commit -m "Nop bai Lab Ngay 4"
   git push -u origin main
   ```

   Sửa bài sau đó: `git add -A`, `git commit -m "Sua bai"`, `git push`.
3. Mở link repo trên trình duyệt, kiểm có `src/exports/assignment.json`, hai file zip, báo cáo `report/individual/<MSSV>_<HoTen>.md` và 4 ảnh.
4. Nộp **link repo** trên LMS bằng tài khoản cá nhân, trước deadline.

Bài được chấm **sau hạn nộp**, dựa trên commit cuối cùng trước deadline. LC trong buổi chỉ hướng dẫn, không chấm tại lớp.

## Deadline (GMT+7)

- **23:59 GMT+7 ngày làm lab.**
- Nếu coach thông báo deadline khác trong vòng 48h sau lab, làm theo thông báo đó.
- Nộp muộn: xem `RULES.md`.

## Cách kiểm tra trước khi nộp

Chạy từ thư mục gốc của repo (lệnh xuất lại hai file và tự kiểm):

```bash
python lab.py export
```

Đạt khi: dòng cuối là `Kết quả: ĐẠT` (không có dòng `[LỖI]`), script báo 12 ảnh người và 8 ảnh mặt.

Kiểm tra không lỡ commit ảnh gốc:

```bash
git ls-files | grep -iE "\.(jpg|jpeg|png|webp)$"
```

Lệnh chỉ được in ra ảnh minh họa có sẵn trong `docs/images/` và ảnh chụp màn hình của bạn trong `report/individual/images/`.

## Checklist

- [ ] Repo đặt đúng tên `K5-L2-DAY04-HoVaTen-MSSV-KeypointPose`.
- [ ] Có `src/exports/assignment.json`, `src/exports/HoVaTen_persons.zip` và `src/exports/HoVaTen_faces.zip` (chạy `python lab.py export` lần cuối sau khi gán xong).
- [ ] Script tự kiểm in `Kết quả: ĐẠT`; đã dán phần tóm tắt vào báo cáo mục 5.
- [ ] Báo cáo đã đổi tên thành `MSSV_HoTen.md` và điền đủ mục 0–8.
- [ ] Bảng tự review có ít nhất 8 dòng (5 ảnh người, 3 ảnh mặt).
- [ ] Có 4 ảnh chụp màn hình trong `report/individual/images/` và đã chèn vào báo cáo.
- [ ] Hai job trên CVAT đã chuyển sang **completed**.
- [ ] Không commit ảnh gốc, annotation COCO gốc, `.env` hay mật khẩu.
- [ ] Đã push lên repo GitHub của bạn, mời tài khoản chấm bài nếu repo private, và nộp link repo trên LMS trước 23:59 GMT+7 ngày lab.
