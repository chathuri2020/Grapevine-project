from PIL import Image, ImageDraw
from modules.utils import resize_and_pad, scale_boxes_back
from ultralytics import YOLO

model = YOLO("models/best_2025_10_09.pt")

def process_single(image_file):
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
        color = "blue" if cls == 1 else "purple"
        draw.rectangle([x1, y1, x2, y2], outline=color, width=5)

    metrics = {"Flowers": flower_count, "Berries": berry_count}
    return img_overlay, metrics
