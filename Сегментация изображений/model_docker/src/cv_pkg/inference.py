from ultralytics import YOLO

device = 'cpu'

model = YOLO('best.onnx', task='segment')

path_to_img = "../dataset_ready_for_yolo/val/images/scene_0179_002.jpg" ## можно поменять изображение

results = model.predict([path_to_img], device = device)

for i in range(len(results)):
    result = results[i]
    result.save(filename=f"result_{i}.jpg")