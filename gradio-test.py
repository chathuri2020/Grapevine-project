import gradio as gr
import PIL.Image as Image
from ultralytics import ASSETS, YOLO
import tempfile, zipfile, os
import io # Required to handle files in memory
import pandas as pd
from ultralytics import ASSETS, YOLO

model = YOLO("best_2025_10_09.pt")


def process_zip(zip_file):
    results_list = []

    # Create a temporary folder to extract the zip
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(zip_file.name, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # Walk through the extracted folder
        for root, dirs, files in os.walk(tmpdirname):
            for file in files:
                if not file.lower().endswith(('.jpg','.jpeg','.png')):
                    continue

                img_path = os.path.join(root, file)
                results = model(img_path, verbose=False)[0]

                flower_count = sum(1 for box in results.boxes if int(box.cls) == 1)
                berry_count  = sum(1 for box in results.boxes if int(box.cls) == 0)
                ratio = flower_count / berry_count if berry_count > 0 else None

                # Extract folder info for image ID
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
                    "Ratio": ratio
                })
    df = pd.DataFrame(results_list)
    return df

iface = gr.Interface(
    fn=process_zip,
    inputs=gr.File(file_types=[".zip"], label="Upload ZIP of Images"),
    outputs=gr.Dataframe(headers=["Bunch_ID","Image_ID","Treatment","Flowers","Berries","Ratio"])
)

iface.launch()

