import logging
import kubric as kb
from kubric.renderer import Blender as BlenderRenderer
from kubric.simulator import PyBullet as PyBulletSimulator
import numpy as np
import os
import json
import bpy

# --- АРГУМЕНТЫ ---
parser = kb.ArgumentParser() 
parser.add_argument("--scene_id", type=int, required=True, help="ID сцены для генерации")
parser.add_argument("--output_dir", type=str, default="output/shapenet_google_style")
parser.set_defaults(frame_end=40, resolution=(512, 512)) 
args = parser.parse_args()

# --- КОНСТАНТЫ ---
FRAMES_PER_SCENE = 5
RESOLUTION = (512, 512)
TARGET_CATEGORIES = ["chair", "table", "sofa", "car", "airplane"]

logging.basicConfig(level="INFO")

# --- МАНИФЕСТ ---
MANIFEST_URL = "gs://kubric-unlisted/assets/ShapeNetCore.v2.json"
shapenet = kb.AssetSource.from_manifest(MANIFEST_URL)

# --- ГЕНЕРАЦИЯ СЦЕНЫ ---
scene_id = args.scene_id
logging.info(f"--- Generating Scene {scene_id} ---")

scene = kb.Scene(resolution=RESOLUTION)
renderer = BlenderRenderer(scene, samples_per_pixel=64, background_transparency=True)
simulator = PyBulletSimulator(scene)

# RNG (Legacy)
rng = np.random.RandomState(seed=scene_id)

# --- ОСВЕЩЕНИЕ ---
clevr_lights = kb.assets.utils.get_clevr_lights(rng=rng)
for light in clevr_lights:
    scene += light
scene.ambient_illumination = kb.Color(0.05, 0.05, 0.05)

# --- ПОЛ ---
floor = kb.Cube(name="floor", scale=(100, 100, 1), position=(0, 0, -1), static=True)
scene += floor
if bpy.app.version > (3, 0, 0):
    floor.linked_objects[renderer].is_shadow_catcher = True
else:
    floor.linked_objects[renderer].cycles.is_shadow_catcher = True

# --- СПАВН ОБЪЕКТОВ ---
spawned_objects = []
num_objects_to_spawn = rng.randint(3, 7)

for i in range(num_objects_to_spawn):
    cat_name = rng.choice(TARGET_CATEGORIES)
    
    candidates = [name for name, spec in shapenet._assets.items()
                  if spec.get("metadata", {}).get("category", "").lower() == cat_name]
    
    if not candidates:
        continue
        
    asset_id = rng.choice(candidates)
    obj = shapenet.create(asset_id=asset_id)
    
    obj.scale = tuple([rng.uniform(0.8, 1.5)] * 3)
    obj.quaternion = kb.Quaternion(axis=[1, 0, 0], degrees=90)
    
    if obj.metadata is None:
        obj.metadata = {}
    obj.metadata["yolo_class"] = cat_name
    
    scene += obj
    
    try:
        kb.move_until_no_overlap(obj, simulator, spawn_region=[(-2, -2, 0.5), (2, 2, 2)], rng=rng)
        spawned_objects.append(obj)
    except Exception:
        scene.remove(obj)

# --- ФИЗИКА ---
simulator.run(frame_start=0, frame_end=40)

# --- ВЫВОД ---
scene_output_dir = os.path.join(args.output_dir, f"scene_{scene_id:04d}")
os.makedirs(scene_output_dir, exist_ok=True)

# --- РЕНДЕР ---
STILL_FRAME_INDEX = 40
scene.camera = kb.PerspectiveCamera(focal_length=35)

class_mapping = {}
for idx, obj in enumerate(spawned_objects, start=1):
    obj.segmentation_id = idx
    class_mapping[idx] = obj.metadata["yolo_class"]

with open(os.path.join(scene_output_dir, "classes.json"), "w") as f:
    json.dump(class_mapping, f)

for view_idx in range(FRAMES_PER_SCENE):
    scene.camera.position = kb.sample_point_in_half_sphere_shell(5.0, 6.5, 0.5)
    scene.camera.look_at((0, 0, 0))
    
    scene.camera.keyframe_insert("position", STILL_FRAME_INDEX)
    scene.camera.keyframe_insert("quaternion", STILL_FRAME_INDEX)

    data = renderer.render(return_layers=("rgba", "segmentation"), frames=[STILL_FRAME_INDEX])
    
    kb.compute_visibility(data["segmentation"], scene.assets)
    data["segmentation"] = kb.adjust_segmentation_idxs(
        data["segmentation"], scene.assets, spawned_objects
    ).astype(np.uint8)
    
    rgba = data["rgba"][0]
    segmentation = data["segmentation"][0]
    
    kb.file_io.write_png(rgba, os.path.join(scene_output_dir, f"rgba_{view_idx:03d}.png"))
    kb.file_io.write_palette_png(segmentation, os.path.join(scene_output_dir, f"segmentation_{view_idx:03d}.png"))

logging.info(f"Scene {scene_id} done. Classes mapped: {len(class_mapping)}")
