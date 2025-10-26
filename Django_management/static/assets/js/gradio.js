// static/assets/js/gradio.js (ONLY SINGLE IMAGE LOGIC)

document.addEventListener('DOMContentLoaded', (event) => {

    // Function to get the CSRF token from the HTML
    function getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }

    // --- 1. SINGLE IMAGE ANALYSIS ---
    document.getElementById('run-single-btn').addEventListener('click', async () => {
        const fileInput = document.getElementById('img-input-single');
        const outputImage = document.getElementById('img-output-single');
        const metricsOutput = document.getElementById('metrics-output-single');
        const loadingText = document.getElementById('single-loading-text');
        const file = fileInput.files[0];

        if (!file) {
            alert("Please select a single image file.");
            return;
        }

        // Show loading state
        loadingText.style.display = 'block';
        outputImage.style.display = 'none';
        metricsOutput.textContent = 'Processing...';

        const formData = new FormData();
        formData.append('image_file', file); 
        formData.append('csrfmiddlewaretoken', getCsrfToken()); 
        
        try {
            // Path MUST match the URL pattern in urls.py ('single_image/')
            const response = await fetch('/single_image_t/', { 
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                // If Django returns a non-200 status (e.g., 400 or 500)
                const errorData = await response.json();
                throw new Error(`Server Error: ${errorData.error || response.statusText}`);
            }

            const data = await response.json();
            
            // Set image source from Base64 string returned by the view
            outputImage.src = 'data:image/png;base64,' + data.processed_image_b64;
            outputImage.style.display = 'block';
            
            // Display metrics
            metricsOutput.innerHTML = `
                <strong>Results:</strong><br>
                ${Object.entries(data.metrics)
                    .map(([key, value]) => `<strong>${key}</strong>: ${value.toFixed(2)}`)
                    .join('<br>')}
            `;

        } catch (e) {
            metricsOutput.textContent = `API Error: ${e.message}`;
            console.error("Single Image API error:", e);
        } finally {
            loadingText.style.display = 'none';
        }
    });

    // NOTE: If you add BATCH or REPORT logic later, add it HERE, inside this wrapper!
});