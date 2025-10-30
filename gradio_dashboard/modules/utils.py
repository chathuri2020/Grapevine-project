from PIL import Image, ImageOps

def resize_and_pad(img, size=(512, 512), color=(255, 255, 255)):
    img = img.copy()
    img.thumbnail(size, Image.Resampling.LANCZOS)
    delta_w = size[0] - img.size[0]
    delta_h = size[1] - img.size[1]
    padding = (
        delta_w // 2,
        delta_h // 2,
        delta_w - (delta_w // 2),
        delta_h - (delta_h // 2)
    )
    new_img = ImageOps.expand(img, padding, fill=color)
    return new_img, padding, img.size

def scale_boxes_back(boxes, resized_size, original_size, padding):
    pad_left, pad_top, _, _ = padding
    res_w, res_h = resized_size
    orig_w, orig_h = original_size
    scale_x = orig_w / (res_w - pad_left * 2)
    scale_y = orig_h / (res_h - pad_top * 2)

    scaled_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        x1 = max(0, (x1 - pad_left) * scale_x)
        y1 = max(0, (y1 - pad_top) * scale_y)
        x2 = min(orig_w, (x2 - pad_left) * scale_x)
        y2 = min(orig_h, (y2 - pad_top) * scale_y)
        scaled_boxes.append([x1, y1, x2, y2])
    return scaled_boxes
