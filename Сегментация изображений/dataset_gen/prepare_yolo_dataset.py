import os
import json
import cv2
import numpy as np
import shutil
from tqdm import tqdm
from PIL import Image

SOURCE_DIR = "output/shapenet_google_style"
DEST_DIR = "dataset_ready_for_yolo"
GLOBAL_CLASSES = ["chair", "table", "sofa", "car", "airplane"]
class_to_id = {name: i for i, name in enumerate(GLOBAL_CLASSES)}

def create_yolo_polygon(mask, class_id):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    h, w = mask.shape
    for cnt in contours:
        if cv2.contourArea(cnt) > 50:
            cnt = cnt.flatten()
            normalized = []
            for i in range(0, len(cnt), 2):
                x = cnt[i] / w
                y = cnt[i+1] / h
                normalized.append(f"{x:.6f} {y:.6f}")
            if len(normalized) > 2:
                polygons.append(f"{class_id} {' '.join(normalized)}")
    return polygons

if os.path.exists(DEST_DIR): shutil.rmtree(DEST_DIR)

for split in ["train", "val"]:
    os.makedirs(f"{DEST_DIR}/{split}/images", exist_ok=True)
    os.makedirs(f"{DEST_DIR}/{split}/labels", exist_ok=True)

scenes = sorted([d for d in os.listdir(SOURCE_DIR) if d.startswith("scene_")])

split_idx = int(len(scenes) * 0.8)
train_scenes = scenes[:split_idx]
val_scenes = scenes[split_idx:]

print(f"Processing {len(scenes)} scenes...")

for split, scene_list in [("train", train_scenes), ("val", val_scenes)]:
    for scene_name in tqdm(scene_list):
        scene_path = os.path.join(SOURCE_DIR, scene_name)
        json_path = os.path.join(scene_path, "classes.json")
        
        if not os.path.exists(json_path): continue
        with open(json_path) as f: local_classes = json.load(f)
            
        frames = sorted([f for f in os.listdir(scene_path) if f.startswith("rgba_")])
        
        for frame_file in frames:
            idx = frame_file.replace("rgba_", "").replace(".png", "")
            seg_file = f"segmentation_{idx}.png"
            
            img = cv2.imread(os.path.join(scene_path, frame_file), cv2.IMREAD_UNCHANGED)
            if img is not None:
                if img.shape[2] == 4:
                    alpha = img[:,:,3]/255.0
                    bg = np.ones_like(img[:,:,:3])*255
                    img = (img[:,:,:3]*alpha[:,:,None] + bg*(1-alpha[:,:,None])).astype(np.uint8)
                cv2.imwrite(f"{DEST_DIR}/{split}/images/{scene_name}_{idx}.jpg", img)
            
            seg_path = os.path.join(scene_path, seg_file)
            if not os.path.exists(seg_path): continue
            
            pil_img = Image.open(seg_path)
            seg_arr = np.array(pil_img)
            
            labels = []
            for loc_id_str, cls_name in local_classes.items():
                if cls_name not in class_to_id: continue
                loc_id = int(loc_id_str)
                
                mask = (seg_arr == loc_id).astype(np.uint8)
                
                if mask.sum() > 0:
                    labels.extend(create_yolo_polygon(mask, class_to_id[cls_name]))
            
            if labels:
                with open(f"{DEST_DIR}/{split}/labels/{scene_name}_{idx}.txt", "w") as f:
                    f.write("\n".join(labels))

yaml_content = f"path: ../{DEST_DIR}\ntrain: train/images\nval: val/images\nnames:\n"
for i, name in enumerate(GLOBAL_CLASSES):
    yaml_content += f"  {i}: {name}\n"
with open(f"{DEST_DIR}/data.yaml", "w") as f: f.write(yaml_content)

print("Done!")
