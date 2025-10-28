import gradio as gr
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from PIL import Image
from io import BytesIO
import base64

# Import your model logic function
from .modules.single_image import process_single
from .modules.batch_processing import process_batch
from django.http import FileResponse

# --- Normal HTML pages ---


def single_image(request):
    return render(request, 'gradio/single_image.html')


def batch_zip(request):
    return render(request, 'gradio/batch_zip.html')


def report(request):
    return render(request, 'gradio/report.html')

# your_app/views.py


@require_POST
@csrf_exempt  # Use this because CSRF token is manually passed via FormData
def single_image_api(request):

    if 'image_file' not in request.FILES:
        return JsonResponse({'error': 'Image file not provided.'}, status=400)

    uploaded_file = request.FILES['image_file']

    try:
        # 1. Convert Django UploadedFile to PIL Image
        img_input_pil = Image.open(BytesIO(uploaded_file.read()))
    except Exception:
        return JsonResponse({'error': 'Invalid image format or failed to read.'}, status=400)

    try:
        # 2. Run your model logic
        processed_img_pil, metrics_dict = process_single(img_input_pil)
    except RuntimeError as e:
        return JsonResponse({'error': f'Server setup error: {e}'}, status=500)
    except Exception as e:
        print(f"Model processing failed: {e}")
        return JsonResponse({'error': f'Processing failed on the server: {e}'}, status=500)

    # 3. Convert processed image (PIL) to Base64 string for the JS frontend
    buffered = BytesIO()
    processed_img_pil.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # 4. Return the structured JSON response
    return JsonResponse({
        'processed_image_b64': img_str,
        'metrics': metrics_dict
    })


""" Batch processing  """


@csrf_exempt
def batch_zip_api(request):
    """
    API endpoint to process a ZIP file of images and return YOLO results.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)

    if 'zip_file' not in request.FILES:
        return JsonResponse({'error': 'ZIP file not provided.'}, status=400)
    """ else:
        return JsonResponse({'error': 'ZIP file is here.'}, status=400) """

    zip_file = request.FILES['zip_file']

    try:
        df, csv_path = process_batch(zip_file)

        # Convert DataFrame to string for frontend display
        csv_text = df.to_string(index=False)
        #convert 
        df_json = df.to_dict(orient='records')
        columns = list(df.columns)

        return JsonResponse({
            'message': 'Batch processing completed successfully!',
            'results_text': csv_text,
            'results_data': df_json,
            'columns': columns,
            'success': True,
            # 'csv_download': csv_path  # optional: if you want a download link later
        })

    except Exception as e:
        print("Error in batch processing:", e)
        return JsonResponse({'error': f'Failed to process ZIP: {str(e)}'}, status=500)


def download_csv(request):
    csv_path = request.GET.get('path')
    if not csv_path or not os.path.exists(csv_path):
        return JsonResponse({'error': 'File not found'}, status=404)
    return FileResponse(open(csv_path, 'rb'), as_attachment=True, filename='grape_growth_results.csv')
