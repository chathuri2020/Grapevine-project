import os, tempfile, zipfile
import pandas as pd
from ultralytics import YOLO
import os

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(APP_DIR, "models", "best_2025_10_09.pt")
print("Calculated model path:", model_path)

try:
    model = YOLO(model_path)
    print("YOLO Model loaded successfully for batch analysis.")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

def process_batch(zip_file):
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

    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, "grape_growth_results.csv")
    df.to_csv(csv_path, index=False)

    return df, csv_path
