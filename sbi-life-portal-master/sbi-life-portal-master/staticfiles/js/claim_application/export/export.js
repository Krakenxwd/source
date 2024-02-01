window.onload = function check_status() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const searchTerm = urlParams.get('search');
    const dateRange = urlParams.get('date_range');
    const fileType = urlParams.get('export_file_type');
    const outputType = urlParams.get('export_output_type');

    $('#search').val(searchTerm);
    $('#date_range').val(dateRange);
    $('#export_file_type').val(fileType);
    $('#export_output_type').val(outputType);

};



let queuedExportList = JSON.parse(document.getElementById('queued_export_list').innerText)
let processingExportList = JSON.parse(document.getElementById('processing_export_list').innerText)

if (queuedExportList.length > 0 || processingExportList.length > 0) {
    const requestData = {
        queued: queuedExportList,
        processing: processingExportList
    }
    const params = new URLSearchParams(requestData).toString()
    const url = `/htmx/export_table?${params}`

    const fetchJob = setInterval(async () => {
        const data = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        
        const response = await data.json()

        if (response.call_ajax === false) {
            clearInterval(fetchJob)
        }
        
        const processingExportResponseArray = response.processing_export_response
        const queuedExportResponseArray = response.queued_export_response

        processingExportResponseArray.forEach((processingExport) => {
            const documentStatusElement = document.getElementById(`${processingExport.export_id}_status`).parentElement
            documentStatusElement.innerHTML = processingExport.status_html
            const documentActionsElement = document.getElementById(`${processingExport.export_id}_action`).parentElement
            documentActionsElement.innerHTML = processingExport.actions_html
        })

        queuedExportResponseArray.forEach((queuedExport) => {
            const documentStatusElement = document.getElementById(`${queuedExport.export_id}_status`).parentElement
            documentStatusElement.innerHTML = queuedExport.status_html
            const documentActionsElement = document.getElementById(`${queuedExport.export_id}_action`).parentElement
            documentActionsElement.innerHTML = queuedExport.actions_html
        })

    }, 2000)
}