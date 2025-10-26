import gradio as gr
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageOps
import tempfile, zipfile, os
import pandas as pd

# Load model
model = YOLO("best_2025_10_09.pt")

# ---------- Utility Functions ----------

def resize_and_pad(img, size=(512, 512), color=(255, 255, 255)):
    """Resize image to fit into fixed square frame with padding."""
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
    """Scale YOLO box coordinates from resized image back to original image."""
    pad_left, pad_top, _, _ = padding
    res_w, res_h = resized_size
    orig_w, orig_h = original_size
    scale_x = orig_w / (res_w - pad_left * 2)
    scale_y = orig_h / (res_h - pad_top * 2)

    scaled_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        # Remove padding offset and rescale
        x1 = max(0, (x1 - pad_left) * scale_x)
        y1 = max(0, (y1 - pad_top) * scale_y)
        x2 = min(orig_w, (x2 - pad_left) * scale_x)
        y2 = min(orig_h, (y2 - pad_top) * scale_y)
        scaled_boxes.append([x1, y1, x2, y2])
    return scaled_boxes

# ---------- Processing Functions ----------

def process_single(image_file):
    img = image_file
    img_resized, padding, orig_size = resize_and_pad(img)
    results = model(img_resized, verbose=False)[0]

    # Count detections
    flower_count = sum(1 for box in results.boxes if int(box.cls) == 1)
    berry_count = sum(1 for box in results.boxes if int(box.cls) == 0)
    

    # Draw boxes on original image with coordinate correction
    img_overlay = img.copy()
    draw = ImageDraw.Draw(img_overlay)
    scaled_boxes = scale_boxes_back(results.boxes, img_resized.size, img.size, padding)
    for box, scaled in zip(results.boxes, scaled_boxes):
        x1, y1, x2, y2 = scaled
        cls = int(box.cls)
        color = "blue" if cls == 1 else "purple"
        draw.rectangle([x1, y1, x2, y2], outline=color, width=5)

    metrics = {
        "Flowers": flower_count,
        "Berries": berry_count,
       
    }
    return img_overlay, metrics

def process_zip(zip_file):
    results_list = []
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(zip_file.name, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)

        for root, _, files in os.walk(tmpdirname):
            for file in files:
                if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue

                img_path = os.path.join(root, file)
                results = model(img_path, verbose=False)[0]

                flower_count = sum(1 for box in results.boxes if int(box.cls) == 1)
                berry_count = sum(1 for box in results.boxes if int(box.cls) == 0)
               

                relative_path = os.path.relpath(root, tmpdirname)
                parts = relative_path.split(os.sep)
                main_stage = parts[1].capitalize() if len(parts) > 0 else "Unknown"
                treatment = parts[2].lower() if len(parts) > 1 else "unknown"

                numbering_folder = os.path.basename(root)
                if numbering_folder.lower().startswith("pt"):
                    numbering_folder = numbering_folder[2:]

                image_number = os.path.splitext(file)[0]

                image_id = f"{main_stage}_{treatment}_{numbering_folder}_{image_number}"
                bunch_id = f"{treatment}_{numbering_folder}_{image_number}"

                results_list.append({
                    "Bunch_ID": bunch_id,
                    "Image_ID": image_id,
                    "Treatment": treatment,
                    "Flowers": flower_count,
                    "Berries": berry_count,
                    
                })

    df = pd.DataFrame(results_list)
     # ---------- Save CSV for download ----------
    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, "grape_growth_results.csv")
    df.to_csv(csv_path, index=False)

    return df, csv_path


# ---------- Gradio UI ----------

with gr.Blocks() as demo:
    gr.Markdown("# 🌿 **Grapevine Analyzer**")
    gr.Markdown("Upload either a **Batch ZIP** or a **Single Image** for detection analysis.")

    with gr.Tab("Batch ZIP Analysis"):
        with gr.Row():
            with gr.Column(scale=1):
                zip_input = gr.File(file_types=[".zip"], label="Upload ZIP of Images")
                run_zip = gr.Button("Run Batch Analysis")
                
            with gr.Column(scale=2):
  
                zip_output = gr.Dataframe(headers=["Bunch_ID", "Image_ID", "Treatment", "Flowers", "Berries"])
                csv_output = gr.File(label="⬇️ Download CSV File", visible=True)
                run_zip.click(process_zip, inputs=zip_input, outputs=[zip_output, csv_output])
               

       

    with gr.Tab("Single Image Analysis"):
        with gr.Row():
            with gr.Column():
                img_input = gr.Image(type="pil", label="Upload Single Image", height=512, width=512)
                run_single = gr.Button("Run Single Image Analysis")
            with gr.Column():
                img_output = gr.Image(type="pil", label="Detection Overlay", height=512, width=512)
                metrics_output = gr.Label(num_top_classes=3, label="Metrics")

        run_single.click(process_single, inputs=img_input, outputs=[img_output, metrics_output])

# ---------- Launch ----------

demo.launch()
