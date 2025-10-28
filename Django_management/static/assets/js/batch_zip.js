// static/assets/js/batch_zip.js (BATCH ZIP LOGIC)

document.addEventListener('DOMContentLoaded', (event) => {

    // --- 0. FUNCTION: Get CSRF token ---
    function getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }

    if (typeof $.fn.DataTable === "undefined") {
        console.error("⚠️ DataTables is not loaded!");
        return;
    }
    else {
        console.log(" DataTables is  loaded!");

    }
    // --- 1. BATCH ZIP PROCESS ---
    document.getElementById('run-batch-btn').addEventListener('click', async () => {
        const fileInput = document.getElementById('zip-input-batch');
        const resultsContainer = document.getElementById('zip-output-batch'); // ✅ updated
        const loadingText = document.getElementById('single-loading-text');
        const file = fileInput.files[0];
        console.log("hi we are loading")
        if (!file) {
            alert("Please select a ZIP file containing images.");
            return;
        }

        // Show loading state
        loadingText.style.color = 'green';
        loadingText.textContent = 'Processing ZIP file, please wait...';
        /*  resultsContainer.value = ''; // clear previous text
         resultsContainer.placeholder = "Processing..."; */

        const formData = new FormData();
        formData.append('zip_file', file);
        formData.append('csrfmiddlewaretoken', getCsrfToken());

        try {
            const response = await fetch('/batch_zip_t/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Server Error-Try-Catch: ${errorData.error || response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                console.log(data);
                createTableFromJson(data.results_data, 'table-container');
            } else {
                resultsContainer.innerHTML = `<div class="alert alert-danger">❌ ${data.error || 'Processing failed'}</div>`;
            }

        } catch (e) {
            resultsContainer.value = `⚠️ Error: ${e.message}`;
            console.error("Batch ZIP API error:", e);
        } finally {
            loadingText.style.display = 'none';
        }
    }); // ✅ this closes the event listener correctly


    // --- 2. Helper: Create responsive DataTable ---
    function createTableFromJson(data, containerId) {
        if (!data || data.length === 0) {
            document.getElementById(containerId).innerHTML = "<p>No data to display.</p>";
            return;
        }

        // Clear previous table if exists
        document.getElementById(containerId).innerHTML = "";

        // Create wrapper div with Bootstrap responsive table
        const wrapper = document.createElement('div');
        wrapper.className = "table-responsive w-100";

        // Create table
        const table = document.createElement('table');
        table.id = "batchTable";
        table.className = "table  table-bordered table-hover align-middle";
        wrapper.appendChild(table);

        document.getElementById(containerId).appendChild(wrapper);

        // Define columns
        const columns = Object.keys(data[0]).map(key => ({
            title: key.charAt(0).toUpperCase() + key.slice(1),
            data: key
        }));

        // Initialize DataTable
        $(table).DataTable({
            data: data,
            columns: columns,
            pageLength: 10,
            lengthMenu: [5, 10, 25, 50],
            responsive: true,
            dom: 'Bfrtip',
            buttons: [
                {
                    extend: 'copy',
                    text: 'Copy',
                    className: 'btn btn-sm btn-primary mx-1'
                },
                {
                    extend: 'csv',
                    text: 'CSV',
                    className: 'btn btn-sm btn-success mx-1'
                },
                {
                    extend: 'excel',
                    text: 'Excel',
                    className: 'btn btn-sm btn-warning mx-1'
                },
                {
                    extend: 'print',
                    text: 'Print',
                    className: 'btn btn-sm btn-info mx-1'
                }
            ],
            language: {
                search: "Filter:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
            }
          
        });
    }

});
