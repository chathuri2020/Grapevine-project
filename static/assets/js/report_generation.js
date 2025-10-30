document.addEventListener("DOMContentLoaded", () => {
    const generateBtn = document.getElementById("generate-report-btn");
    const fileInput = document.getElementById("csv-input-report");
    const loadingText = document.getElementById("report-loading-text");
    const downloadsDiv = document.getElementById("report-downloads");
    const downloadPdf = document.getElementById("download-pdf");
    const downloadCsv = document.getElementById("download-csv");
    const statusDiv = document.getElementById("report-status");

    function getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }

    generateBtn.addEventListener("click", async () => {
        const file = fileInput.files[0];
        if (!file) {
            alert("Please select a CSV file first.");
            return;
        }

        loadingText.style.display = "block";
        downloadsDiv.style.display = "none";
        statusDiv.innerHTML = "Generating reports...";

        const formData = new FormData();
        formData.append("csv_file", file);
        formData.append("csrfmiddlewaretoken", getCsrfToken());

        try {
            const response = await fetch("/generate_report_api/", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                const pdfFile = data.pdf_file;
                const csvFile = data.csv_file;
                console.log("PDF :",pdfFile)
                console.log("PDF :",csvFile)
                // Set download links
               // downloadPdf.href = `/download_report/?file=${encodeURIComponent(pdfFile)}&type=pdf`;
                //downloadCsv.href = `/download_report/?file=${encodeURIComponent(csvFile)}&type=csv`;
                downloadPdf.href = `/download_report/?file=${encodeURIComponent(pdfFile)}&type=pdf`;
                downloadCsv.href = `/download_report/?file=${encodeURIComponent(csvFile)}&type=csv`;
                console.log(downloadPdf.href)
                downloadsDiv.style.display = "block";
                statusDiv.innerHTML = "✅ Reports generated successfully!";
            } else {
                statusDiv.innerHTML = `<span class="text-danger">Error: ${data.error || "Report generation failed"}</span>`;
            }

        } catch (err) {
            statusDiv.innerHTML = `<span class="text-danger">Error: ${err.message}</span>`;
        } finally {
            loadingText.style.display = "none";
        }
    });
});
