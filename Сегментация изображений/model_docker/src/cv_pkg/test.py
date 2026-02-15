from ultralytics import YOLO

device = 'cpu'

model = YOLO('best.onnx', task='segment')

metrics = model.val(
    data='../dataset_ready_for_yolo/data.yaml',
    task='segment',
    imgsz=640,
    batch=1,
    conf=0.001,
    iou=0.7,
    device=device,
    plots=True,
    verbose=True
)

print("\nМетрики для сегментации")
print(f"mAP@50-95 (seg): {metrics.seg.map:.4f}")
print(f"mAP@50 (seg): {metrics.seg.map50:.4f}")
print(f"mAP@75 (seg): {metrics.seg.map75:.4f}")
print(f"mAP@50-95 по классам (seg): {metrics.seg.maps}")

print("\nМетрики для детекции (box)")
print(f"mAP@50-95 (box): {metrics.box.map:.4f}")
print(f"Precision: {metrics.box.p.mean():.4f}")
print(f"Recall: {metrics.box.r.mean():.4f}")
print(f"F1: {metrics.box.f1.mean():.4f}")