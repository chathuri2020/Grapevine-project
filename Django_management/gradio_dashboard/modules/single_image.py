from PIL import Image, ImageDraw
# Assuming 'utils' is also in the 'modules' directory or accessible via this path
from .utils import resize_and_pad, scale_boxes_back 
from ultralytics import YOLO
import os


APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#D:\Django_projects\Grapevine_analyzer\Django_management\gradio_dashboard\models\best_2025_10_09.pt
# Now append 'models' to the app root (gradio_dashboard/)
model_path = os.path.join(APP_DIR, "models", "best_2025_10_09.pt")

print("Calculated model path:", model_path)

try:
    model = YOLO(model_path)
    print("YOLO Model loaded successfully for single image analysis.")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

def process_single(image_file):
    """
    Processes a PIL Image object using the YOLO model.
    :param image_file: A PIL Image object.
    :return: (processed_img_pil, metrics_dict)
    """
    if not model:
        raise RuntimeError("Model is unavailable.")
        
    img = image_file
    img_resized, padding, orig_size = resize_and_pad(img)
    results = model(img_resized, verbose=False)[0]

    flower_count = sum(1 for box in results.boxes if int(box.cls) == 1)
    berry_count = sum(1 for box in results.boxes if int(box.cls) == 0)

    img_overlay = img.copy()
    draw = ImageDraw.Draw(img_overlay)
    scaled_boxes = scale_boxes_back(results.boxes, img_resized.size, img.size, padding)
    for box, scaled in zip(results.boxes, scaled_boxes):
        x1, y1, x2, y2 = scaled
        cls = int(box.cls)
        color = "blue" if cls == 1 else "black"
        draw.rectangle([x1, y1, x2, y2], outline=color, width=5)

    metrics = {"Flowers": flower_count, "Berries": berry_count}
    return img_overlay, metrics