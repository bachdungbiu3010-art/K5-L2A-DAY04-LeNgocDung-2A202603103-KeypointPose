"""
prelabel_pose.py — Gán NHÁP keypoint cho Lab Ngày 4 (theo ghi chú của Thầy: được dùng máy,
nhưng báo cáo phải ghi rõ hình nào máy làm, hình nào mình làm).

  - Người: YOLO11x-pose (17 điểm COCO, đúng thứ tự và tên của đề)
  - Khuôn mặt: dlib shape predictor 68 điểm -> quy đổi về 13 điểm của lab
  - Cờ visibility theo độ tin cậy của model + quy tắc đề (ngoài ảnh -> 0, kính râm -> mắt v=1)
  - Xuất COCO Keypoints 1.0 để Upload annotations vào task CVAT do lab.py setup tạo

Chạy:  python prelabel_pose.py --repo <thư mục bài lab> --mssv 2A202603103 [--persons ...] [--faces ...]
       --persons / --faces: chỉ gán các ảnh liệt kê (mặc định: toàn bộ bộ ảnh được giao)
"""
import argparse
import hashlib
import json
import random
import re
import zipfile
from pathlib import Path

import cv2
import numpy as np

V_SURE, V_OCC = 0.5, 0.3     # conf >= 0.5 -> v=2 ; 0.3..0.5 -> v=1 (ước lượng) ; < 0.3 -> v=0
MIN_H = 60                   # quy ước lab: người cao dưới 60 px không gán


def imread_u(p):
    return cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)


def imwrite_u(p, img):
    ok, b = cv2.imencode(".jpg", img)
    b.tofile(str(p))


# ---------------------------------------------------------------- bộ ảnh theo MSSV
def assignment(pool, mssv):
    """Viết lại đúng thuật toán chia ảnh của lab.py (để biết trước bộ ảnh; đối chiếu lại với assignment.json)."""
    m = re.sub(r"\s+", "", str(mssv)).upper()
    rng = random.Random(int(hashlib.sha256(f"{pool['version']}:{m}".encode()).hexdigest(), 16))
    persons = []
    for g, q in pool["quota"].items():
        persons += sorted(rng.sample(sorted(p["file"] for p in pool["persons"] if p["group"] == g), q))
    faces = []
    for k, q in pool["face_quota"].items():
        faces += sorted(rng.sample(sorted(f["file"] for f in pool["faces"] if f["kind"] == k), q))
    return persons, faces


# ---------------------------------------------------------------- người: YOLO-pose
def run_persons(model, files, img_dir, schema):
    imgs, anns, notes = [], [], {}
    aid = 1
    for i, f in enumerate(files, 1):
        img = imread_u(img_dir / f)
        h, w = img.shape[:2]
        imgs.append({"id": i, "file_name": f, "width": w, "height": h})
        r = model.predict(img, conf=0.25, verbose=False)[0]
        notes[f] = []
        if r.keypoints is None:
            continue
        for box, kxy, kc, sc in zip(r.boxes.xyxy.tolist(), r.keypoints.xy.tolist(),
                                    r.keypoints.conf.tolist(), r.boxes.conf.tolist()):
            x0, y0, x1, y1 = box
            if y1 - y0 < MIN_H:
                notes[f].append(f"bỏ 1 người cao {y1 - y0:.0f}px (< 60px)")
                continue
            kp, n = [], 0
            for (x, y), c in zip(kxy, kc):
                inside = 0 <= x < w and 0 <= y < h and (x, y) != (0, 0)
                v = 2 if c >= V_SURE else (1 if c >= V_OCC else 0)
                if not inside:
                    v = 0
                kp += [round(x, 2), round(y, 2), v] if v else [0, 0, 0]
                n += v > 0
            if n < 3:
                continue
            anns.append({"id": aid, "image_id": i, "category_id": 1, "keypoints": kp, "num_keypoints": n,
                         "bbox": [round(x0, 2), round(y0, 2), round(x1 - x0, 2), round(y1 - y0, 2)],
                         "area": round((x1 - x0) * (y1 - y0), 2), "iscrowd": 0, "segmentation": [],
                         "attributes": {"score": round(sc, 3)}})
            aid += 1
            if sc < 0.5:
                notes[f].append(f"người #{aid - 1} tin cậy thấp {sc:.2f}: có phải người thật (poster/gương?)")
    cat = {"id": 1, "name": "person", "supercategory": "", "keypoints": schema["person"]["keypoints"],
           "skeleton": schema["person"]["skeleton"]}
    return imgs, anns, cat, notes


# ---------------------------------------------------------------- khuôn mặt: dlib 68 -> 13 điểm
# dlib 68: 36-41 = mắt PHẢI của người (bên trái ảnh khi quay mặt), 42-47 = mắt TRÁI của người.
# 36 khóe ngoài mắt phải, 39 khóe trong; 42 khóe trong mắt trái, 45 khóe ngoài;
# mí trên = TB(37,38) / TB(43,44); mí dưới = TB(40,41) / TB(46,47); chóp mũi 30;
# 48 khóe miệng PHẢI của người, 54 khóe miệng TRÁI; 51 giữa môi trên (mép ngoài), 57 giữa môi dưới.
FACE13 = {
    "left_eye_outer": [45], "left_eye_inner": [42], "left_eye_upper": [43, 44], "left_eye_lower": [46, 47],
    "right_eye_outer": [36], "right_eye_inner": [39], "right_eye_upper": [37, 38], "right_eye_lower": [40, 41],
    "nose_tip": [30], "mouth_left": [54], "mouth_right": [48], "lip_upper": [51], "lip_lower": [57],
}


def run_faces(files, img_dir, schema, kinds):
    import dlib
    import face_recognition_models as frm
    det = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(frm.pose_predictor_model_location())
    names = schema["face"]["keypoints"]
    imgs, anns, notes = [], [], {}
    for i, f in enumerate(files, 1):
        img = imread_u(img_dir / f)
        h, w = img.shape[:2]
        imgs.append({"id": i, "file_name": f, "width": w, "height": h})
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = det(rgb, 1)
        notes[f] = []
        if faces:
            rect = max(faces, key=lambda r: r.area())
        else:   # ảnh đã cắt quanh mặt: dùng gần trọn khung ảnh
            rect = dlib.rectangle(int(w * .1), int(h * .1), int(w * .9), int(h * .9))
            notes[f].append("dlib không tự tìm thấy mặt, dùng khung ảnh — kiểm kỹ toàn bộ điểm")
        s = sp(rgb, rect)
        P = np.array([[p.x, p.y] for p in s.parts()], float)
        kind = kinds.get(f, "")
        kp, n = [], 0
        for name in names:
            x, y = P[FACE13[name]].mean(0)
            v = 2
            if kind == "kinh_ram" and "eye" in name:
                v = 1                       # đề: kính râm tối -> 4 điểm mỗi mắt occluded
            if not (0 <= x < w and 0 <= y < h):
                v = 0
            kp += [round(float(x), 2), round(float(y), 2), v] if v else [0, 0, 0]
            n += v > 0
        if kind == "nghieng":
            notes[f].append("mặt nghiêng: mắt phía xa có thể bị sống mũi che -> cân nhắc v=1/0")
        if kind == "toc":
            notes[f].append("tóc che: xem mắt nào bị che -> đổi v=1 hoặc v=0")
        x0, y0 = P.min(0); x1, y1 = P.max(0)
        anns.append({"id": i, "image_id": i, "category_id": 1, "keypoints": kp, "num_keypoints": n,
                     "bbox": [float(x0), float(y0), float(x1 - x0), float(y1 - y0)],
                     "area": float((x1 - x0) * (y1 - y0)), "iscrowd": 0, "segmentation": []})
    cat = {"id": 1, "name": "face", "supercategory": "", "keypoints": names, "skeleton": schema["face"]["skeleton"]}
    return imgs, anns, cat, notes


# ---------------------------------------------------------------- xuất + xem trước
def write_zip(path, imgs, anns, cat):
    coco = {"info": {"description": "MAY GAN NHAP - prelabel_pose.py"}, "licenses": [], "categories": [cat],
            "images": imgs, "annotations": anns}
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("annotations/person_keypoints_default.json", json.dumps(coco))


def preview(img_dir, imgs, anns, cat, out_dir):
    """Đỏ = TRÁI của người, xanh = PHẢI; tròn đặc v=2, tròn rỗng v=1, không vẽ v=0 (giống GUIDELINE)."""
    names = cat["keypoints"]
    for im in imgs:
        img = imread_u(img_dir / im["file_name"])
        sc = max(1, 900 // max(img.shape[:2]))
        img = cv2.resize(img, None, fx=sc, fy=sc)
        for k, a in enumerate([a for a in anns if a["image_id"] == im["id"]], 1):
            p = np.array(a["keypoints"]).reshape(-1, 3)
            for e0, e1 in cat["skeleton"]:
                if p[e0 - 1, 2] and p[e1 - 1, 2]:
                    cv2.line(img, tuple((p[e0 - 1, :2] * sc).astype(int)), tuple((p[e1 - 1, :2] * sc).astype(int)), (200, 200, 200), 1)
            for (x, y, v), nm in zip(p, names):
                if not v:
                    continue
                col = (0, 0, 255) if ("left" in nm) else (255, 120, 0) if ("right" in nm) else (0, 220, 0)
                cv2.circle(img, (int(x * sc), int(y * sc)), 4, col, -1 if v == 2 else 1)
            x, y = int(a["bbox"][0] * sc), int(a["bbox"][1] * sc)
            cv2.putText(img, f"#{k}", (x, max(14, y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        imwrite_u(out_dir / im["file_name"], img)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--mssv", required=True)
    ap.add_argument("--ten", default="LeNgocDung")
    ap.add_argument("--yolo", default="yolo11x-pose.pt")
    ap.add_argument("--out", default="may_gan_nhap")
    ap.add_argument("--persons", nargs="*", default=None)
    ap.add_argument("--faces", nargs="*", default=None)
    a = ap.parse_args()
    repo = Path(a.repo)
    pool = json.loads((repo / "src/lab/pool.json").read_text(encoding="utf-8"))
    schema = json.loads((repo / "src/keypoint_schema.json").read_text(encoding="utf-8"))
    persons, faces = assignment(pool, a.mssv)
    asg = repo / "src/exports/assignment.json"
    if asg.exists():                                    # ưu tiên file do lab.py setup tạo
        j = json.loads(asg.read_text(encoding="utf-8"))
        if (j["persons"], j["faces"]) != (persons, faces):
            print("CHÚ Ý: assignment.json khác bộ ảnh tự tính -> dùng assignment.json")
        persons, faces = j["persons"], j["faces"]
    if a.persons is not None:
        persons = [p for p in persons if p in a.persons]
    if a.faces is not None:
        faces = [f for f in faces if f in a.faces]
    out = repo / a.out
    (out / "preview_persons").mkdir(parents=True, exist_ok=True)
    (out / "preview_faces").mkdir(parents=True, exist_ok=True)
    img_dir = repo / "src/lab/images"
    kinds = {f["file"]: f["kind"] for f in pool["faces"]}
    groups = {p["file"]: p["group"] for p in pool["persons"]}
    report = ["# Danh sách ảnh MÁY gán nháp (đưa vào báo cáo theo ghi chú của Thầy)\n"]
    if persons:
        from ultralytics import YOLO
        imgs, anns, cat, notes = run_persons(YOLO(a.yolo), persons, img_dir, schema)
        write_zip(out / f"{a.ten}_persons_MAY.zip", imgs, anns, cat)
        preview(img_dir, imgs, anns, cat, out / "preview_persons")
        report.append("## Ảnh người — YOLO11x-pose\n\n| Ảnh | Nhóm | Số người máy gán | Cần kiểm |\n|---|---|---:|---|")
        for im in imgs:
            k = sum(1 for x in anns if x["image_id"] == im["id"])
            report.append(f"| {im['file_name']} | {groups.get(im['file_name'], '')} | {k} | {'; '.join(notes[im['file_name']]) or '—'} |")
    if faces:
        imgs, anns, cat, notes = run_faces(faces, img_dir, schema, kinds)
        write_zip(out / f"{a.ten}_faces_MAY.zip", imgs, anns, cat)
        preview(img_dir, imgs, anns, cat, out / "preview_faces")
        report.append("\n## Ảnh khuôn mặt — dlib 68 điểm quy đổi 13 điểm\n\n| Ảnh | Loại | Cần kiểm |\n|---|---|---|")
        for im in imgs:
            report.append(f"| {im['file_name']} | {kinds.get(im['file_name'], '')} | {'; '.join(notes[im['file_name']]) or '—'} |")
    report.append("\nQuy ước cờ của máy: tin cậy ≥ 0,5 → v=2; 0,3–0,5 → v=1; < 0,3 hoặc ngoài ảnh → v=0. "
                  "Kính râm → 8 điểm mắt v=1. Người cao < 60 px không gán.")
    (out / "MAY_LAM.md").write_text("\n".join(report), encoding="utf-8")
    print("Xong:", out)


if __name__ == "__main__":
    main()
