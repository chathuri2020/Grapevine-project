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
    } else {
        console.log("DataTables is loaded!");
    }

    // --- 0.5 CREATE DUMMY TABLE ON PAGE LOAD ---
    function createDummyTable(containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = "";

        // Wrapper for responsive table
        const wrapper = document.createElement('div');
        wrapper.className = "table-responsive w-100";

        // Table element
        const table = document.createElement('table');
        table.id = "batchTable";
        table.className = "table table-bordered table-hover table-dark w-100"; // dark-friendly
        wrapper.appendChild(table);

        container.appendChild(wrapper);

        // Initialize DataTable with empty data
        $(table).DataTable({
            data: [],              // no rows
            columns: [{ title: "No columns available", data: "col1" }], // dummy column, actual columns will be generated later
            paging: true,
            pageLength: 5,          // <-- number of rows to show by default
            lengthMenu: [5, 10, 25, 50],
            searching: true,
            responsive: true,
            dom: 'Bfrtip',         // buttons + filter
            buttons: [
                { extend: 'copy', text: 'Copy', className: 'btn btn-sm btn-primary mx-1' },
                { extend: 'csv', text: 'CSV', className: 'btn btn-sm btn-success mx-1' },
                { extend: 'excel', text: 'Excel', className: 'btn btn-sm btn-warning mx-1' },
                { extend: 'print', text: 'Print', className: 'btn btn-sm btn-info mx-1' }
            ],
            language: {
                search: "Filter:",
                paginate: { previous: "Prev", next: "Next" },
                info: "Showing _START_ to _END_ of _TOTAL_ entries"
            }
        });
    }

    // Call dummy table creation on page load
    createDummyTable('table-container');

    // --- 1. BATCH ZIP PROCESS ---
    document.getElementById('run-batch-btn').addEventListener('click', async () => {
        const fileInput = document.getElementById('zip-input-batch');
        const resultsContainer = document.getElementById('zip-output-batch');
        const loadingText = document.getElementById('single-loading-text');
        const file = fileInput.files[0];

        if (!file) {
            alert("Please select a ZIP file containing images.");
            return;
        }

        loadingText.style.color = 'green';
        loadingText.textContent = 'Processing ZIP file, please wait...';

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
                throw new Error(`Server Error: ${errorData.error || response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                console.log(data);
                createTableFromJson(data.results_data, 'table-container'); // actual data
            } else {
                resultsContainer.innerHTML = `<div class="alert alert-danger">❌ ${data.error || 'Processing failed'}</div>`;
            }

        } catch (e) {
            resultsContainer.value = `⚠️ Error: ${e.message}`;
            console.error("Batch ZIP API error:", e);
        } finally {
            loadingText.style.display = 'none';
        }
    });

    // --- 2. Helper: Create responsive DataTable with real data ---
    function createTableFromJson(data, containerId) {
        if (!data || data.length === 0) {
            document.getElementById(containerId).innerHTML = "<p>No data to display.</p>";
            return;
        }

        const container = document.getElementById(containerId);
        container.innerHTML = "";

        const wrapper = document.createElement('div');
        wrapper.className = "table-responsive w-100";

        const table = document.createElement('table');
        table.id = "batchTable";
        table.className = "table table-bordered table-hover align-middle";
        wrapper.appendChild(table);

        container.appendChild(wrapper);

        const columns = Object.keys(data[0]).map(key => ({
            title: key.charAt(0).toUpperCase() + key.slice(1),
            data: key
        }));

        $(table).DataTable({
            data: data,
            columns: columns,
            pageLength: 10,
            lengthMenu: [5, 10, 25, 50],
            responsive: true,
            dom: 'Bfrtip',
            buttons: [
                { extend: 'copy', text: 'Copy', className: 'btn btn-sm btn-primary mx-1' },
                { extend: 'csv', text: 'CSV', className: 'btn btn-sm btn-success mx-1' },
                { extend: 'excel', text: 'Excel', className: 'btn btn-sm btn-warning mx-1' },
                { extend: 'print', text: 'Print', className: 'btn btn-sm btn-info mx-1' }
            ],
            language: {
                search: "Filter:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries"
            }
        });
    }

});
