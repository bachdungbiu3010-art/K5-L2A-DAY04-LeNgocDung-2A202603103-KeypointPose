# Rubric

Chấm theo từng học viên.

**Đạt:** từ **60/100** điểm chính, không quá **1** người bị đổi trái/phải toàn bộ, và thỏa đủ điều kiện tối thiểu sau:

- Đủ người cao từ 60 px trong ảnh được giao; không gán poster, gương, màn hình.
- Không có điểm `v > 0` nằm ngoài ảnh (điểm ngoài ảnh phải là `outside`, xuất ra `v = 0`).
- Hai file xuất mở được, đúng tên 17 điểm và 13 điểm.
- Bảng tự review có ít nhất 8 dòng.

Coach tính lại bộ 12 ảnh của bạn từ MSSV (`src/exports/assignment.json`), rồi so file `HoVaTen_persons.zip` với ground truth COCO của đúng 12 ảnh đó: ghép từng skeleton với người GT, tính OKS từng người (σ của COCO, chỉ tính điểm GT `v > 0`), đếm cặp trái/phải bị đổi, so cờ `v`, đếm người thiếu / thừa. File `HoVaTen_faces.zip` so với GT khuôn mặt coach tự gán. Coach đối chiếu bảng tự review trong báo cáo với lỗi thật tìm được.

## Điểm chính (100)

| Tiêu chí | Điểm | Bằng chứng | Điều kiện được điểm / bị trừ |
|---|---:|---|---|
| C1 — Label và định dạng file xuất (CP0, CP4) | 10 | `src/exports/*.zip`, báo cáo mục 1 và 5 | Đúng tên 17 + 13 điểm (5). File mở được, 51 / 39 số mỗi annotation, `v` chỉ gồm 0 / 1 / 2, `num_keypoints` khớp (5). −3 nếu sai định dạng xuất (không phải COCO Keypoints 1.0); −2 nếu zip kèm ảnh |
| C2 — Vị trí điểm: OKS (CP1) | 30 | `*_persons.zip` so với GT | OKS trung bình các người so với GT: 0,5 → 0 điểm, 0,9 → 30 điểm, tuyến tính ở giữa |
| C3 — Trái/phải (CP1) | 15 | `*_persons.zip` so với GT | −3 mỗi người đổi trái/phải toàn bộ; −1 mỗi cặp điểm đổi lẻ |
| C4 — Cờ visibility (CP1) | 15 | `*_persons.zip` so với GT | Trên mỗi điểm GT `v > 0`: đúng hẳn cờ = 1; có gán nhưng nhầm giữa `v = 1` và `v = 2` = 0,5; bỏ trống (`outside`) = 0. Điểm = 15 × trung bình. Trừ thêm 1 điểm cho mỗi điểm `v > 0` nằm ngoài ảnh, hoặc bị kéo về mép trong khi khớp thật nằm ngoài ảnh |
| C5 — Đủ người, không thừa (CP1) | 10 | `*_persons.zip`, báo cáo mục 2 | −2 mỗi người cao từ 60 px bị bỏ sót; −2 mỗi skeleton trên poster / gương / màn hình hoặc trùng người |
| C6 — Khuôn mặt 13 điểm (CP2) | 10 | `*_faces.zip` so với GT mặt, ảnh mục 6.3 | Mắt và miệng trái/phải đúng (4); mí và khóe đặt ở mép (4); kính râm đúng cờ `v = 1` (2) |
| C7 — Tự review và báo cáo (CP0–CP4) | 10 | `report/individual/MSSV_HoTen.md`, `report/individual/images/` | Bảng review ≥ 8 dòng với mã lỗi rõ (4); bảng ca khó có lý do (3); mục kiểm file xuất, kết quả script và 4 ảnh chụp (3). −2 mỗi lỗi `lr_swap` dễ thấy còn trong file nộp mà bảng review không ghi |
| **Tổng điểm chính** | **100** | | |

## Bonus (tối đa 10, ghi riêng, không tự cộng vào điểm chính)

| Mục | Điểm tối đa | Bằng chứng | Điều kiện |
|---|---:|---|---|
| B1 — 3 ảnh người khó thêm | 5 | `src/exports/HoVaTen_bonus_persons.zip`, báo cáo mục Bonus | Đủ người, không `lr_swap` toàn bộ, cờ đúng quy tắc |
| B2 — 5 ảnh khuôn mặt đen trắng / hồng ngoại | 5 | `src/exports/HoVaTen_bonus_faces.zip`, báo cáo mục Bonus | Đủ 5 mặt, mắt trái/phải đúng; có đoạn nhận xét về ảnh không màu |
| B3 — Model so với nhãn của tôi | 0 | Báo cáo mục Bonus | Không tính điểm, chỉ để học. Ghi để coach phản hồi |

Bonus chỉ được tính khi CP0–CP4 đã hoàn thành. Bonus là điểm cộng cho bài lab, không phải điểm phát biểu hay giơ tay.

## Điều kiện mất điểm chung

- Thiếu `src/exports/assignment.json` hoặc file bị sửa tay: coach chấm theo bộ ảnh tính từ MSSV; ảnh không thuộc bộ của bạn không được tính.
- Repo hoặc file báo cáo đặt sai tên: coach có thể không tìm thấy bài; nếu vẫn chấm được, −5 điểm.
- Commit ảnh gốc COCO hay Wikimedia vào repo: −10 điểm và phải xóa khỏi lịch sử git.
- Sửa JSON xuất bằng tay: tiêu chí C1 = 0.
- Nộp muộn: theo `RULES.md`.
- Chép tọa độ từ annotation COCO gốc hoặc chép file xuất của người khác (gần như trùng hoàn toàn): 0 điểm.
