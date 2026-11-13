# Đọc file COCO Keypoints 1.0 và OKS

## 1. File xuất từ CVAT trông thế nào

Zip xuất từ CVAT (định dạng COCO Keypoints 1.0, không kèm ảnh) có dạng:

```text
HoVaTen_persons.zip
└── annotations/
    └── person_keypoints_default.json
```

File JSON có ba phần chính:

```json
{
  "images": [
    { "id": 1, "file_name": "easy_01.jpg", "width": 640, "height": 480 }
  ],
  "categories": [
    {
      "id": 1,
      "name": "person",
      "keypoints": ["nose", "left_eye", "right_eye", "…", "right_ankle"],
      "skeleton": [[16, 14], [14, 12], "…"]
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "keypoints": [412, 96, 2,  0, 0, 0,  405, 88, 2,  380, 92, 1,  "…"],
      "num_keypoints": 14,
      "bbox": [360, 70, 118, 330],
      "area": 38940
    }
  ]
}
```

(Các chỗ `"…"` là phần lược bớt cho gọn, file thật có đủ số.)

- `categories[].keypoints`: danh sách tên điểm theo đúng thứ tự trong label. Phần tử thứ *i* của danh sách ứng với bộ ba thứ *i* trong `keypoints` của annotation.
- Mỗi skeleton là một phần tử trong `annotations`.
- File xuất từ task `persons` có thể vẫn khai báo cả category `face` (vì label đặt ở cấp project). Không sao, miễn là annotation chỉ thuộc đúng category.

## 2. Mảng `keypoints`: các bộ ba `(x, y, v)`

```text
"keypoints": [x1, y1, v1,  x2, y2, v2,  …,  x17, y17, v17]   // 17 × 3 = 51 số
```

| `v` | Nghĩa | Trên CVAT | Tọa độ |
|---:|---|---|---|
| 0 | không gán (not labeled) | `outside` | không được dùng (xem ghi chú) |
| 1 | có gán, không nhìn thấy (labeled, not visible) | `occluded` | vị trí ước lượng |
| 2 | có gán, nhìn thấy (labeled, visible) | bình thường | tâm khớp |

**Ghi chú về điểm `v = 0`.** Chuẩn COCO ghi điểm không gán là `0, 0, 0`. CVAT 2.x (đã thử trên bản 2.82) xuất điểm `outside` thành `v = 0` nhưng **vẫn giữ tọa độ cũ**, ví dụ `342, 625, 0`. Cả hai cách đều đúng về nghĩa: code huấn luyện và OKS chỉ nhìn `v`, điểm `v = 0` bị bỏ qua. Vì vậy không sửa JSON bằng tay để đưa về `0, 0`. Điều cần kiểm là: mọi điểm ngoài ảnh phải có `v = 0`, không được là `v = 1` hay `v = 2`. CVAT **không** tự cắt tọa độ: một điểm `v = 2` kéo ra ngoài khung vẫn được xuất nguyên như vậy.

- `num_keypoints` = số bộ có `v > 0`.
- Người: 17 điểm → **51 số**. Mặt: 13 điểm → **39 số**.
- Một annotation có `num_keypoints = 0` bị bỏ khi huấn luyện và khi chấm.

Đọc thử 5 bộ đầu của ví dụ trên (thứ tự: 1 `nose`, 2 `left_eye`, 3 `right_eye`, 4 `left_ear`, 5 `right_ear`):

| Bộ | Giá trị | Đọc là |
|---|---|---|
| 1 | `412, 96, 2` | mũi thấy rõ tại (412, 96) |
| 2 | `0, 0, 0` | mắt trái không gán (file CVAT có thể ghi tọa độ cũ kèm `v = 0`, nghĩa vẫn vậy) |
| 3 | `405, 88, 2` | mắt phải thấy rõ |
| 4 | `380, 92, 1` | tai trái bị che, vị trí ước lượng |

## 3. Nhãn của bạn đi vào model ở đâu

1. **Heatmap đích.** Mỗi điểm `v > 0` thành một ngọn đồi Gauss quanh (x, y) trên bản đồ nhiệt của khớp đó. Nhãn lệch 3 px thì đỉnh đích lệch 3 px. Nhãn không nhất quán giữa các ảnh thì đồi bè ra, đỉnh thấp.
2. **Trọng số trong loss.** Điểm `v = 0` có trọng số 0. Điểm `v = 1` và `v = 2` có trọng số 1: model học cả vị trí khớp bị che mà bạn ước lượng.
3. **Lật ảnh khi huấn luyện.** Ảnh lật ngang: `x' = W − x`, đồng thời đổi tên theo cặp left ↔ right. Code chỉ đổi đúng khi nhãn trái/phải của bạn đúng quy ước. Một annotator gán theo trái của người xem sẽ tạo ra dữ liệu mâu thuẫn mà không script nào tự sửa được.
4. **Chọn người để học và chấm.** Người có `num_keypoints = 0` bị bỏ. Khi chấm OKS, chỉ điểm `v > 0` trong nhãn được tính.

(Mô tả theo cách các code huấn luyện phổ biến như HRNet, MMPose xử lý file COCO. Dự án khác có thể đặt trọng số khác cho `v = 1`.)

## 4. OKS: chấm một bộ keypoint thế nào

```text
OKS = Σᵢ exp( −dᵢ² / (2 · s² · kᵢ²) ) · [vᵢ > 0]  /  Σᵢ [vᵢ > 0]
```

| Ký hiệu | Nghĩa |
|---|---|
| `dᵢ` | khoảng cách pixel giữa điểm dự đoán và điểm nhãn thứ *i* |
| `s²` | diện tích (area) của người trong nhãn: người càng to thì càng được dung sai nhiều pixel |
| `kᵢ = 2σᵢ` | hệ số riêng của từng loại điểm |
| `[vᵢ > 0]` | chỉ tính điểm có gán (`v = 1` hoặc `v = 2`) trong nhãn |

Mỗi số hạng `exp(…)` là similarity của một điểm, từ 1 (trùng) về 0.

σ của COCO (theo cocoapi):

| Điểm | σ | Điểm | σ |
|---|---:|---|---:|
| `nose` | 0,026 | `wrists` | 0,062 |
| `eyes` | 0,025 | `hips` | 0,107 |
| `ears` | 0,035 | `knees` | 0,087 |
| `shoulders` | 0,079 | `ankles` | 0,089 |
| `elbows` | 0,072 | | |

σ của hông lớn hơn 4 lần σ của mắt. Lý do: khi COCO cho nhiều annotator gán lại cùng một ảnh, mắt là một chấm rõ nên mọi người đặt gần như trùng nhau, còn hông nằm dưới quần áo nên hai annotator giỏi vẫn lệch nhau nhiều.

### Ví dụ: lệch 8 px ở mắt và ở hông

Người cao khoảng 300 px, area `s² = 15 000 px²`. Model đặt mắt trái lệch 8 px và hông trái cũng lệch 8 px.

- Mắt (σ = 0,025, k = 0,05): `2 · 15 000 · 0,0025 = 75`; `64 / 75 ≈ 0,85`; similarity `= exp(−0,85) ≈ 0,43`.
- Hông (σ = 0,107, k = 0,214): `2 · 15 000 · 0,0458 ≈ 1 374`; `64 / 1 374 ≈ 0,047`; similarity `≈ 0,95`.

Cùng 8 px, mắt mất hơn một nửa điểm, hông gần như không mất gì. Vì vậy: **phóng to khi đặt mắt, mũi, tai.**

### OKS trong rubric

Coach tính OKS từng người trong `HoVaTen_persons.zip` so với GT COCO, lấy trung bình. Điểm C2 = 0 khi OKS trung bình ≤ 0,5 và = 30 khi ≥ 0,9, tuyến tính ở giữa. Một người bị đổi trái/phải toàn bộ có OKS rất thấp dù mọi chấm nằm đúng khớp.

Script tự kiểm trong `src/` **không** có GT nên không tính OKS. Nó chỉ kiểm định dạng và các dấu hiệu lỗi thường gặp.
