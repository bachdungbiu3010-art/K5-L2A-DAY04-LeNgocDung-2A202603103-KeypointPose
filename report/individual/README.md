# Báo cáo cá nhân

Báo cáo phải được đổi tên theo MSSV và họ tên không dấu:

```text
report/individual/MSSV_HoTen.md
```

Ví dụ: `report/individual/20241234_NguyenVanAn.md`.

Ảnh chụp màn hình đặt trong `report/individual/images/`, đúng 4 tên:

| File | Nội dung |
|---|---|
| `1_label_person.png` | Label `person` trong label constructor, thấy đủ 17 điểm có tên |
| `2_nguoi_quay_lung.png` | Một người quay lưng đã gán, cờ đã đặt (thấy điểm `occluded` / `outside`) |
| `3_mat_phong_to.png` | Một khuôn mặt đã gán 13 điểm, phóng to vùng mắt |
| `4_json_export.png` | Một đoạn JSON xuất của một người (mảng `keypoints`, `num_keypoints`) |

Chỉ cắt vùng cần thiết, không chép nguyên ảnh gốc độ phân giải đầy đủ. Ghi nguồn ảnh ("COCO val2017" hoặc "Wikimedia Commons") dưới mỗi ảnh trong báo cáo.
