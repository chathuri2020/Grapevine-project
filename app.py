import gradio as gr
from modules.single_image import process_single
from modules.batch_processing import process_batch
from modules.report_generator import generate_report


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
                run_zip.click(process_batch, inputs=zip_input, outputs=[zip_output, csv_output])
               

       

    with gr.Tab("Single Image Analysis"):
        with gr.Row():
            with gr.Column():
                img_input = gr.Image(type="pil", label="Upload Single Image", height=512, width=512)
                run_single = gr.Button("Run Single Image Analysis")
            with gr.Column():
                img_output = gr.Image(type="pil", label="Detection Overlay", height=512, width=512)
                metrics_output = gr.Label(num_top_classes=3, label="Metrics")

        run_single.click(process_single, inputs=img_input, outputs=[img_output, metrics_output])

   
            
    with gr.Tab("Generate Report"):
        # Pass only the CSV file component
        with gr.Row():
                # ---------- Left column: Inputs ----------
                with gr.Column(scale=1):
                    csv_input = gr.File(file_types=[".csv"], label="Upload CSV File")
                    run_report = gr.Button("Generate PDF & CSV Report")
                
                # ---------- Right column: Outputs ----------
                with gr.Column(scale=1):
                    pdf_output = gr.File(label="Download PDF Report")
                    csv_output = gr.File(label="Download CSV Summary")
        run_report.click(generate_report, inputs=csv_input, outputs=[pdf_output, csv_output])

# ---------- Launch ----------

demo.launch()
