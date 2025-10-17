import gradio as gr
import PIL.Image as Image
from ultralytics import ASSETS, YOLO
import tempfile, zipfile, os

model = YOLO("best_2025_10_09.pt")

'''
def predict_image(img, conf_threshold, iou_threshold):
    """Predicts and plots labeled objects in an image using YOLOv8 model with adjustable confidence and IOU thresholds."""
    results = model.predict(
        source=img,
        conf=conf_threshold,
        iou=iou_threshold,
        show_labels=True,
        show_conf=True,
        imgsz=640,
    )

    for r in results:
        im_array = r.plot()
        im = Image.fromarray(im_array[..., ::-1])

    return im

'''

def predict_zip(zip_file, conf_threshold, iou_threshold):
    """Predicts and plots labeled objects for all images inside a ZIP file."""
    
    # Temporary folder to extract zip
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file.name, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    results_images = []

    # Loop through all extracted images
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            results = model.predict(
                source=file_path,
                conf=conf_threshold,
                iou=iou_threshold,
                show_labels=True,
                show_conf=True,
                imgsz=640,
                verbose=False
            )

            for r in results:
                im_array = r.plot()
                im = Image.fromarray(im_array[..., ::-1])
                results_images.append(im)

    return results_images

# Build Gradio interface
iface = gr.Interface(
    fn=predict_zip,
    inputs=[
        gr.File(label="Upload ZIP Folder of Images", file_count="single", file_types=[".zip"]),
        gr.Slider(minimum=0, maximum=1, value=0.25, label="Confidence Threshold"),
        gr.Slider(minimum=0, maximum=1, value=0.45, label="IoU Threshold"),
    ],
    #outputs=gr.Gallery(label="Predicted Results").style(grid=[2], height="auto"),
    outputs=gr.Gallery(label="Predicted Results"),  
    title="YOLOv8 ZIP Image Batch Inference",
    description="Upload a ZIP file of images for batch inference using your trained YOLO model.",
)

'''
iface = gr.Interface(
    fn=predict_image,
    inputs=[
        gr.Image(type="pil", label="Upload Image"),
        gr.Slider(minimum=0, maximum=1, value=0.25, label="Confidence threshold"),
        gr.Slider(minimum=0, maximum=1, value=0.45, label="IoU threshold"),
    ],
    outputs=gr.Image(type="pil", label="Result"),
    title="Ultralytics Gradio",
    description="Upload images for inference. The Ultralytics YOLOv8n model is used by default.",
    examples=[
        [ASSETS / "bus.jpg", 0.25, 0.45],
        [ASSETS / "zidane.jpg", 0.25, 0.45],
    ],
)
'''


if __name__ == "__main__":
    iface.launch()