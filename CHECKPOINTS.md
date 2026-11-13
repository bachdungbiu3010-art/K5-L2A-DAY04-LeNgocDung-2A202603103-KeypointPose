# Checkpoints

Có năm checkpoint, làm theo thứ tự. Mốc thời gian tính bằng **phút kể từ lúc bắt đầu buổi thực hành** (phút 0), dùng được cho cả lab sáng lẫn lab chiều. Mỗi checkpoint có phần **Tự kiểm tra**. Chưa đạt thì chưa sang checkpoint sau.

Quy ước nhãn đầy đủ ở `docs/GUIDELINE.md`. Thao tác CVAT ở `docs/CVAT_CHEATSHEET.md`. Định dạng file xuất ở `docs/COCO_KEYPOINTS.md`.

---

## CP0 — Dựng bài trên CVAT của bạn, kiểm label, xem demo (phút 5–45, 40′)

- **Mục tiêu:** CVAT trên máy bạn chạy ổn, có hai task với bộ ảnh riêng của bạn, vào đúng job, chắc chắn hai label Skeleton đúng tên và đúng thứ tự trước khi gán, biết đổi cờ cho **một điểm** trên đúng bản CVAT của lớp.
- **Cần làm:**
  1. Mở Terminal / PowerShell trong thư mục repo, chạy (macOS / Ubuntu dùng `python3`):

     ```bash
     python lab.py check
     python lab.py setup --mssv <MSSV của bạn> --ten <HoVaTen không dấu>
     ```

     `check` tự bật và sửa CVAT. `setup` hỏi tài khoản CVAT (Ngày 2), lấy 12 ảnh người và 8 ảnh mặt chia ngẫu nhiên theo MSSV (ảnh có sẵn trong repo), tạo project `d04-keypoint` cùng hai task `persons-<ten>`, `faces-<ten>`, rồi ghi `src/exports/assignment.json`. Máy yếu: chạy thêm `python lab.py lite` (xem `docs/MAY_YEU.md`).
  2. Mở CVAT → **Projects** → `d04-keypoint` → tab **Labels**.
  3. Kiểm label `person`, kiểu **Skeleton**: có đúng 17 điểm, tên và thứ tự đúng bảng 1 trong `docs/GUIDELINE.md`, 19 cạnh, mẫu dựng theo người **quay mặt về camera** (các điểm `left_*` nằm bên phải khung mẫu).
  4. Kiểm label `face`, kiểu **Skeleton**: có đúng 13 điểm theo bảng 2 trong `docs/GUIDELINE.md`.
  5. Sai tên, thiếu điểm hay sai thứ tự thì **báo coach ngay**, không tự sửa label. Sai một tên trong label là sai điểm đó trên mọi người trong task.
  6. Mở job bằng đường link `setup` in ra (hoặc **Jobs** → job của `persons-<ten>`, `faces-<ten>`). Luôn làm trong trang **Job**, không làm trong trang Task.
  7. Xem coach demo một người quay lưng bị xe che chân. Ghi lại vào báo cáo mục **1** cách đổi `occluded` / `outside` cho **một điểm** trên bản CVAT đang dùng, và số phiên bản CVAT (**Help → About**).
  8. Làm 2 câu quiz thao tác trên slide.
- **Sản phẩm:** `src/exports/assignment.json`; báo cáo mục **1. Kiểm tra label** đã điền đủ.
- **Cần hiểu:** vì sao kiểm label trước khi gán (script và model đọc điểm theo tên; một tên sai làm sai cả task); vì sao mẫu `person` dựng theo người quay mặt về camera.
- **Tự kiểm tra:**
  - [ ] Đếm được 17 điểm trong `person` và 13 điểm trong `face`, tên khớp từng chữ với bảng trong `docs/GUIDELINE.md`.
  - [ ] Thử bật `occluded` cho **một điểm** trên một skeleton nháp: chỉ điểm đó đổi kiểu hiển thị, các điểm còn lại giữ nguyên. Xóa skeleton nháp.
  - [ ] `python lab.py check` in `CVAT sẵn sàng`.
  - [ ] Đang ở trang Job (thanh địa chỉ có `/jobs/`), tên task có tên của bạn.

---

## CP1 — Gán 12 ảnh người, 17 điểm (phút 45–105 và 120–150, 90′)

- **Mục tiêu:** mọi người thật trong cảnh cao từ 60 px có **một** skeleton `person`, đủ 17 điểm, đúng trái/phải, đúng cờ.
- **Cần làm:** job `persons-<ten>`, 12 ảnh của bạn (5 `easy`, 3 `occluded`, 2 `back`, 1 `small`, 1 `crowd`; `setup` in danh sách theo nhóm). Với **mỗi người**:
  1. Chọn công cụ **Skeleton**, label `person`, chế độ **Shape** (không dùng Track). Kéo một khung bao người. CVAT đặt 17 điểm theo mẫu vào khung.
  2. **Nói ra hướng người** trước khi kéo điểm: quay mặt, quay lưng, nghiêng nhìn sang trái ảnh, nghiêng nhìn sang phải ảnh.
  3. Nếu quay lưng: đổi chỗ các điểm `left_*` sang bên trái ảnh **trước**, rồi mới tinh chỉnh.
  4. Kéo từng điểm vào tâm khớp theo thứ tự đầu → vai → tay → hông → chân. Phóng to khi đặt mắt, mũi, tai. Đặt hông vào khớp, không đặt vào cạp quần.
  5. Đặt cờ cho từng điểm cần đổi theo bốn câu hỏi ở mục 4 của `docs/GUIDELINE.md`: bị che nhưng ước lượng chắc thì `occluded` (`v = 1`); ngoài ảnh hoặc không đoán được thì `outside` (`v = 0`).
  6. Nhìn lại đường nối. Hai chân bắt chéo hoặc tay vắt qua thân bất thường thì kiểm lại trái/phải.
  7. `Ctrl+S` sau mỗi người.
- **Nhịp:** `easy` khoảng 5 phút/ảnh, `occluded` 7, `back` 8, `small` 8, `crowd` 14. Một ảnh quá gấp rưỡi nhịp: ghi vào bảng ca khó, chuyển sang ảnh khác, quay lại sau.
- **Không làm:** không gán người trên poster, trong gương, trên màn hình; không gán người cao dưới 60 px (chỉ đếm vào báo cáo); không kéo điểm ngoài ảnh về mép ảnh; không dùng cờ `hidden` thay cho `occluded`.
- **Sản phẩm:** một skeleton `person` cho mỗi người cao từ 60 px trong 12 ảnh của bạn; báo cáo mục **2. Số lượng và thời gian** (dòng 5 nhóm ảnh người) và mục **3. Bảng ca khó** (mỗi điểm phân vân giữa `v = 1` và `v = 0` một dòng).
- **Cần hiểu:** trái/phải theo người trong ảnh (người quay mặt về camera: tay trái nằm bên phải ảnh; người nghiêng nhìn sang phải ảnh: bên gần camera là bên phải của họ); vì sao một điểm đoán bừa có `v > 0` hại hơn một điểm `v = 0`.
- **Tự kiểm tra:**
  - [ ] Mỗi người cao từ 60 px có đúng một skeleton; không có skeleton trên poster, gương, màn hình.
  - [ ] Không điểm nào nằm sát mép ảnh "cho có": điểm ngoài ảnh đã là `outside`.
  - [ ] Đường nối không bắt chéo bất thường.
  - [ ] **Mốc phút 105:** xong ít nhất 8 ảnh. **Mốc phút 150:** đủ 12 ảnh. Chưa đạt thì báo coach.

---

## CP2 — Gán 8 ảnh khuôn mặt, 13 điểm (phút 150–180, 30′)

- **Mục tiêu:** mỗi ảnh một skeleton `face` 13 điểm, mắt trái/phải đúng theo người, mí và khóe đặt đúng mép.
- **Cần làm:** job `faces-<ten>`, 8 ảnh của bạn: 3 mặt thẳng, 2 mặt nghiêng, 1 kính trong, 1 kính râm, 1 tóc che một phần.
  1. Skeleton → label `face` → Shape → kéo khung bao mặt.
  2. Người quay mặt về camera: mắt bên **phải ảnh** là **mắt trái** (`left_eye_*`), khóe miệng bên phải ảnh là `mouth_left`.
  3. Phóng to đến khi thấy từng mép mí. Mí trên, mí dưới: điểm giữa mép mí, ngay trên và dưới tâm con ngươi, không đặt ở lông mi. Khóe miệng: góc gặp nhau của môi trên và môi dưới.
  4. Kính râm tối (ảnh màu): bốn điểm của mắt đó `occluded`, đặt theo gọng kính. Kính trong: bình thường (`v = 2`).
  5. Mặt nghiêng: điểm bị sống mũi che thì `occluded` nếu đoán chắc, `outside` nếu không.
  6. Nhịp khoảng 3 phút/ảnh (24′), còn 6′ để đi hết checklist self-QC ở mục 7 của `docs/GUIDELINE.md`. `Ctrl+S`.
- **Sản phẩm:** 8 skeleton `face` trong job; dòng `faces` trong báo cáo mục **2**; các điểm phân vân vào mục **3**.
- **Cần hiểu:** vì sao mí mắt cần chính xác từng pixel (tỉ số mở mắt = khoảng cách mí trên–mí dưới ÷ bề ngang mắt; mặt xa camera chỉ rộng vài chục pixel, lệch 2 px có thể biến "mắt mở" thành "mắt lim dim" cho hệ thống giám sát tài xế).
- **Tự kiểm tra:**
  - [ ] Ở mặt thẳng đầu tiên, `left_eye_*` nằm bên **phải** ảnh.
  - [ ] Khóe ngoài (`*_eye_outer`) xa sống mũi hơn khóe trong (`*_eye_inner`).
  - [ ] Ảnh kính râm: bốn điểm mắt sau tròng kính hiển thị kiểu `occluded`.

---

## CP3 — Tự review (phút 180–200, 20′)

- **Mục tiêu:** tìm và sửa lỗi trong job của chính mình bằng "mắt người lạ", gọi đúng tên lỗi.
- **Cần làm:** **ghi lỗi trước, sửa sau.**
  1. Đi từ ảnh cuối về ảnh đầu, không theo thứ tự lúc gán. Chọn **5 ảnh người** (ít nhất 2 ảnh thuộc nhóm `back` hoặc `crowd`) và **3 ảnh mặt**.
  2. Bật hiển thị tên điểm. Với từng người: nói to hướng của người, rồi nhìn lại tên điểm trái/phải.
  3. Nhìn đường nối: chân hoặc tay bắt chéo bất thường thường là đổi trái/phải.
  4. Rà cờ từng điểm đã đổi sang `occluded` / `outside`: có đúng bảng cờ không?
  5. Mỗi lỗi một dòng trong bảng review: ảnh, người, điểm, mã lỗi, ghi chú. Sửa ngay, đánh dấu "đã sửa", `Ctrl+S`. Ảnh không có lỗi ghi một dòng `ok`.
- **Mã lỗi:** dùng đúng một trong sáu mã ở mục 6 của `docs/GUIDELINE.md`: `lr_swap`, `vis_flag`, `position`, `missing`, `extra`, `ok`.
- **Sản phẩm:** báo cáo mục **4. Bảng tự review**, ít nhất 8 dòng (5 ảnh người + 3 ảnh mặt, kể cả dòng `ok`).
- **Cần hiểu:** vì sao `lr_swap` là lỗi nặng nhất (điểm nằm đúng khớp nhưng sai tên làm OKS sụp, và phá bước lật ảnh khi huấn luyện).
- **Tự kiểm tra:**
  - [ ] Bảng có ít nhất 8 dòng, mỗi dòng có mã lỗi đúng tên.
  - [ ] Mọi lỗi đã ghi đều có cột "Đã sửa?" là có, hoặc có lý do vì sao không sửa.
  - [ ] Điểm phân vân `v = 1` / `v = 0`: đã ghi cả hai lựa chọn và lý do chọn.

---

## CP4 — Xuất file, chạy script tự kiểm, hoàn thành báo cáo (phút 200–210, 10′; hoàn thiện báo cáo trong buffer)

- **Mục tiêu:** có 2 file xuất đúng định dạng, đã tự kiểm bằng script, báo cáo đủ các mục.
- **Cần làm:**
  1. Chạy:

     ```bash
     python lab.py export
     ```

     Lệnh xuất **COCO Keypoints 1.0** (không kèm ảnh) của hai task thành `src/exports/<HoVaTen>_persons.zip`, `src/exports/<HoVaTen>_faces.zip`, rồi tự chạy `src/check_submission.py`. Chạy lại được nhiều lần; mỗi lần ghi đè bằng nhãn mới nhất.
  2. (Cách tay, nếu cần) Task → **Actions → Export task dataset** → **COCO Keypoints 1.0**, tắt Save images, đổi tên và đặt vào `src/exports/` như trên; rồi chạy `python src/check_submission.py --persons <file persons> --faces <file faces>`.
  3. Đọc kết quả tự kiểm.

  4. Có `[LỖI]` thì sửa trên CVAT rồi xuất lại. Đọc từng `[CẢNH BÁO]`: sửa nếu đúng là lỗi, hoặc ghi lý do giữ nguyên vào báo cáo.
  5. Mở file JSON trong zip, tự kiểm tay 2 người và 1 mặt: `keypoints` có 51 số (mặt: 39 số), điểm bạn bật `outside` ra `v = 0`, điểm `occluded` ra `v = 1`, `num_keypoints` bằng số bộ có `v > 0`. Ghi vào báo cáo mục **5**, dán phần tóm tắt của script.
  6. Chụp 4 ảnh màn hình vào `report/individual/images/` (mục **6** của báo cáo). Viết mục **7. Tự đánh giá**.
  7. Chuyển cả hai job sang **completed** trên CVAT (trong job: **Menu → Finish the job**). Chạy lại `python lab.py export` lần cuối rồi commit.
- **Sản phẩm:** 2 file zip và `assignment.json` trong `src/exports/`; báo cáo đủ mục 0–8; 4 ảnh; hai job ở trạng thái completed.
- **Cần hiểu:** đọc được bộ ba `(x, y, v)` trong mảng `keypoints` (`docs/COCO_KEYPOINTS.md`); vì sao tọa độ của điểm `v = 0` không được dùng (CVAT 2.x vẫn ghi tọa độ cũ, chuẩn COCO ghi `0, 0`); vì sao `num_keypoints = 0` thì người đó bị bỏ khi huấn luyện và khi chấm.
- **Tự kiểm tra:**
  - [ ] Script in `Kết quả: ĐẠT` (không có dòng `[LỖI]`).
  - [ ] Script báo 12 ảnh người, 8 ảnh mặt, mỗi ảnh mặt đúng 1 skeleton.
  - [ ] Zip không chứa ảnh (script báo lỗi nếu có).

---

## Bonus (phút 210–240, chỉ làm khi xong CP0–CP4)

Chọn tối đa hai mục, ghi vào mục **Bonus** của báo cáo. Điểm ở `RUBRIC.md`.

- Tạo task bonus: `python lab.py setup --mssv <MSSV> --ten <HoVaTen> --bonus` (giữ nguyên hai task chính). `python lab.py export` sẽ xuất thêm file bonus.
- **B1 — 3 ảnh người khó thêm:** gán 3 ảnh khó (đông người, chỉ thấy một phần người…) trong task `persons-extra-<ten>` → `src/exports/<HoVaTen>_bonus_persons.zip`.
- **B2 — 5 ảnh khuôn mặt đen trắng:** gán 13 điểm cho 5 ảnh trong task `faces-extra-<ten>` → `src/exports/<HoVaTen>_bonus_faces.zip`. Ghi một đoạn: ảnh không màu khó hơn ở điểm nào, kính râm trên ảnh hồng ngoại có còn là `v = 1` không.
- **B3 — Model so với nhãn của tôi:** mở một demo model pose chạy ngay trên trình duyệt, ví dụ [MediaPipe Studio](https://mediapipe-studio.webapps.google.com/) (Pose Landmarker, Face Landmarker). Không cài gì. Chỉ dùng 2–3 ảnh của buổi do coach chỉ định. So với nhãn của bạn và trả lời 3 câu trong báo cáo. Link không chạy thì bỏ qua, không thay bằng công cụ phải cài đặt.
