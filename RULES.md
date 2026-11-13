# Rules

## Loại bài

**Cá nhân.** Mỗi học viên gán trên hai job CVAT của mình (`persons-<tên>`, `faces-<tên>`), tự review và tự nộp một repo riêng. Được trao đổi cách dùng CVAT với bạn. **Không** gán hộ, không chép file xuất của nhau.

## Bộ ảnh riêng

Mỗi học viên nhận 12 ảnh người chia ngẫu nhiên theo MSSV (`python lab.py setup`). Dùng đúng MSSV của mình. Không đổi MSSV, không sửa `src/exports/assignment.json`, không gán hộ hay chép nhãn của bạn có cùng ảnh: coach tính lại bộ ảnh từ MSSV khi chấm, và bài chỉ được chấm trên bộ ảnh đúng.

## AI và công cụ

Được dùng:

- Trợ lý AI dạng chat để tra cứu khái niệm (heatmap, OKS, định dạng COCO Keypoints), hỏi cách dùng CVAT, sửa câu chữ trong báo cáo.
- AI để giải thích lỗi khi chạy `src/check_submission.py`.
- Demo model pose chạy trên trình duyệt (ví dụ MediaPipe Studio) **chỉ** cho bonus B3, chỉ để so sánh, không đưa kết quả vào job.

Không được dùng:

- Model pose, auto-annotation (CVAT "From model", Nuclio, Segment Anything…) hay bất kỳ công cụ nào để **sinh điểm** rồi nộp như nhãn của mình. Bài lab đo chính kỹ năng gán tay của bạn.
- Chép tọa độ từ annotation COCO gốc hay từ bài của người khác.
- AI để viết hộ phần **Bảng ca khó**, **Tự review** và **Tự đánh giá** (mục 3, 4, 7 của báo cáo). Các mục này phải dựa trên job thật của bạn.

Khi coach hỏi, bạn phải tự giải thích được: người đó quay hướng nào nên left nằm bên nào, vì sao một điểm là `v = 1` mà không phải `v = 0`, và mỗi lỗi trong bảng review thuộc loại nào.

Nếu có dùng AI, ghi ngắn trong mục **9. Tài liệu tham khảo** của báo cáo: công cụ nào, dùng vào việc gì.

## Làm bài và liêm chính

- Không sao chép bài hoặc nhận bài làm thay.
- Ghi nguồn khi dùng tài liệu, ảnh hoặc dữ liệu bên ngoài.
- Không sửa JSON xuất từ CVAT bằng tay. Nếu file xuất sai (ví dụ `occluded` không ra `v = 1`), ghi vào báo cáo và báo coach.
- Ghi đúng thời gian thực tế. Thời gian là dữ liệu để coach căn khối lượng bài, không phải điểm trừ.

## Dữ liệu và quyền riêng tư

- Ảnh COCO và Wikimedia Commons giữ giấy phép của tác giả. Chỉ dùng trong lớp, ghi nguồn khi chụp màn hình.
- **Không commit** ảnh gốc vào repo. Xuất từ CVAT luôn **bỏ chọn Save images**.
- Không đưa ảnh lên app.cvat.ai hay dịch vụ nào khác: chỉ dùng CVAT trên máy bạn. Bonus B3 chỉ dùng 2–3 ảnh coach chỉ định, không dùng ảnh cá nhân hay ảnh người quen.
- Ảnh có người thật: không đăng lại ra ngoài lớp.

## Secret và tài khoản

- Không commit mật khẩu CVAT, token, file `.env`.
- Không chia sẻ tài khoản CVAT. Mỗi người chỉ mở job của mình.

## Nộp muộn và sửa bài sau deadline

- Deadline mặc định: **23:59 GMT+7 ngày làm lab**, trừ khi coach thông báo deadline khác trong vòng 48h sau lab.
- Coach có thể gia hạn tối đa 48h nếu có lý do chính đáng, báo trước deadline.
- Nộp muộn không có gia hạn: **−10% điểm mỗi ngày** (tính tròn theo ngày), quá 3 ngày không nhận.
- Commit sau deadline: coach chấm theo commit cuối cùng trước deadline, trừ khi bạn chấp nhận bị trừ điểm muộn cho commit mới.
- Sau khi coach đã thu file xuất, không xuất lại để thay file trên CVAT.

## Lỗi kỹ thuật

Nếu CVAT lỗi, mất dữ liệu, hoặc không xuất được file:

1. Chụp màn hình lỗi, ghi giờ.
2. Báo coach ngay trong buổi.
3. Ghi lại trong mục **8. Khó khăn và lỗi kỹ thuật** của báo cáo, kèm ảnh.

Có bằng chứng thì không bị trừ điểm vì lỗi hệ thống.
