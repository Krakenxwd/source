/* global console */
/* global $ */
/* jshint esversion: 6 */


window.onload = function check_status() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const searchTerm = urlParams.get('search');

    $('#search').val(searchTerm);
    $('#status').val(urlParams.get('status'));
    $('#validation_status').val(urlParams.get('validation_status'));
    $('#mode').val(urlParams.get('mode'));
    $('#date_range').val(urlParams.get('date_range'));
    $('#claim_id').val(urlParams.get('claim_id'));
    $('#policy_no').val(urlParams.get('policy_no'));
};


let queuedDocumentsList = JSON.parse(document.getElementById('queued_docs_list').innerText)
let processingDocumentsList = JSON.parse(document.getElementById('processing_docs_list').innerText)

if (queuedDocumentsList.length > 0 || processingDocumentsList.length > 0) {
    const requestData = {
        queued: queuedDocumentsList,
        processing: processingDocumentsList
    }
    const params = new URLSearchParams(requestData).toString()
    const url = `/htmx/document_table?${params}`

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

        const processingDocsResponseArray = response.processing_docs_response
        const queuedDocsResponseArray = response.queued_docs_response
        processingDocsResponseArray.forEach((processingDoc) => {
            const documentStatusElement = document.getElementById(`${processingDoc.document_id}_status`).parentElement;
            documentStatusElement.innerHTML = processingDoc.status_html;
            const documentActionsElement = document.getElementById(`${processingDoc.document_id}_actions`).parentElement;
            documentActionsElement.innerHTML = processingDoc.actions_html;
            const documentCheckboxElement = document.getElementById(`${processingDoc.document_id}_checkbox`).parentElement;
            documentCheckboxElement.innerHTML = processingDoc.checkbox_html;
        })

        queuedDocsResponseArray.forEach((queuedDoc) => {
            const documentStatusElement = document.getElementById(`${queuedDoc.document_id}_status`).parentElement;
            documentStatusElement.innerHTML = queuedDoc.status_html;
            const documentActionsElement = document.getElementById(`${queuedDoc.document_id}_actions`).parentElement;
            documentActionsElement.innerHTML = queuedDoc.actions_html;
            const documentCheckboxElement = document.getElementById(`${queuedDoc.document_id}_checkbox`).parentElement
            documentCheckboxElement.innerHTML = queuedDoc.checkbox_html
        })

        document.getElementById('queued-docs-placeholder').innerText = response.total_count_of_queued_docs
        document.getElementById('success-docs-placeholder').innerText = response.total_count_of_success_docs
        document.getElementById('failed-docs-placeholder').innerText = response.total_count_of_failed_docs
        document.getElementById('processing-docs-placeholder').innerText = response.total_count_of_processing_docs

    }, 10000)
}

// Multi Delete/Re-run/validation/ Documents
const checkAllCheckbox = document.querySelector('.check-all');
const singleCheckbox = document.querySelectorAll('.single-checkbox');
const batchActions = document.querySelector('.batch-actions');

if (checkAllCheckbox) {
    checkAllCheckbox.addEventListener('change', (e) => {
        if (checkAllCheckbox.checked == false) {
            singleCheckbox.forEach((checkbox) => {
                checkbox.checked = false
            })
        } else {
            singleCheckbox.forEach((checkbox) => {
                if (!checkbox.checked == true) {
                    checkbox.checked = !checkbox.checked
                }
            })
        }
        toggleBatchActionsVisibility();
    })
}

if (singleCheckbox) {
    singleCheckbox.forEach((checkbox) => {
        checkbox.addEventListener('change', (e) => {
            const allChecked = Array.from(singleCheckbox).every((checkbox) => checkbox.checked)
            checkAllCheckbox.checked = allChecked
            toggleBatchActionsVisibility();
        })
    })
}

/**
 * Toggle the visibility of the batch actions div containing batch
 * actions buttons.
 */
function toggleBatchActionsVisibility() {
    let anyCheckboxChecked = false;
    singleCheckbox.forEach((checkbox) => {
        if (checkbox.checked == true) {
            anyCheckboxChecked = true;
        }
    })
    if (anyCheckboxChecked || checkAllCheckbox.checked) {
        if (batchActions) {
            batchActions.classList.remove('hidden')
        }
    } else {
        if (batchActions) {
            batchActions.classList.add('hidden')
        }
    }
}

const batchActionsContainer = document.querySelector('.batch-actions-container');

if (batchActionsContainer) {
    batchActionsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('open-delete-documents-container')) {
            e.stopPropagation();
            batchDeleteContainer.classList.remove('hidden')
        }
        if (e.target.classList.contains('open-re-run-documents-container')) {
            e.stopPropagation();
            batchReRunContainer.classList.remove('hidden')
        }
        if (e.target.classList.contains('open-re-run-validations-container')) {
            e.stopPropagation();
            batchReRunValidationsContainer.classList.remove('hidden')
        }
    })
}

const batchDeleteContainer = document.querySelector('.delete-documents-container');
const closeBatchDeleteContainer = document.querySelector('.close-delete-documents-container');

if (closeBatchDeleteContainer) {
    closeBatchDeleteContainer.addEventListener('click', () => {
        batchDeleteContainer.classList.add('hidden')
    })
}

const batchReRunContainer = document.querySelector('.re-run-documents-container');
const closeBatchReRunContainer = document.querySelector('.close-re-run-documents-container');

if (closeBatchReRunContainer) {
    closeBatchReRunContainer.addEventListener('click', () => {
        batchReRunContainer.classList.add('hidden')
    })
}

const batchReRunValidationsContainer = document.querySelector('.re-run-validations-container');
const closeBatchReRunValidationsContainer = document.querySelector('.close-re-run-validations-container');

if (closeBatchReRunValidationsContainer) {
    closeBatchReRunValidationsContainer.addEventListener('click', () => {
        batchReRunValidationsContainer.classList.add('hidden')
    })
}

// Batch Delete Documents

const confirmBatchDeleteButton = document.querySelector('#batch-delete-confirm');
if (confirmBatchDeleteButton) {
    confirmBatchDeleteButton.addEventListener('click', async () => {
        confirmBatchDeleteButton.classList.add('pointer-events-none', 'opacity-50', 'w-20', 'text-center')
        confirmBatchDeleteButton.innerHTML = `
            <span class="">
            <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_P7sC{transform-origin:center;animation:spinner_svv2 .75s infinite linear}@keyframes spinner_svv2{100%{transform:rotate(360deg)}}</style><path d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z" fill="#fff" class="spinner_P7sC "/></svg>
            </span>
        `
        let checkedDocuments = document.querySelectorAll('.single-checkbox:checked');
        let checkedDocumentsIDs = [];
        checkedDocuments.forEach((checkbox) => {
            checkedDocumentsIDs.push(checkbox.getAttribute('attr-id'))
        })
        if (checkedDocumentsIDs.length > 0) {
            const requestData = {
                documents: checkedDocumentsIDs
            }
            const response = await fetch('/batch/delete_documents/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                },
                body: JSON.stringify(requestData)
            })
            const data = await response.json()
            if (data.status == 'success') {
                window.location.reload()
            } else {
                batchDeleteContainer.classList.add('hidden');
                confirmBatchDeleteButton.classList.remove('pointer-events-none', 'opacity-50', 'w-20', 'text-center');
                confirmBatchDeleteButton.innerHTML = 'Delete';
                generateNotification(data.status, data.message, (Math.random() + 1).toString(36).substring(7));
            }
        }
    })
}

// Batch Re Run Validations

const confirmBatchReRunValidations = document.querySelector('#batch-rerun-validation-confirm');
if (confirmBatchReRunValidations) {
    confirmBatchReRunValidations.addEventListener('click', async () => {
        confirmBatchReRunValidations.classList.add('pointer-events-none', 'opacity-50', 'w-20', 'text-center')
        confirmBatchReRunValidations.innerHTML = `
            <span class="">
            <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_P7sC{transform-origin:center;animation:spinner_svv2 .75s infinite linear}@keyframes spinner_svv2{100%{transform:rotate(360deg)}}</style><path d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z" fill="#fff" class="spinner_P7sC "/></svg>
            </span>
        `
        let checkedDocuments = document.querySelectorAll('.single-checkbox:checked');
        let checkedDocumentsIDs = [];
        checkedDocuments.forEach((checkbox) => {
            checkedDocumentsIDs.push(checkbox.getAttribute('attr-id'))
        })
        if (checkedDocumentsIDs.length > 0) {
            const requestData = {
                documents: checkedDocumentsIDs
            }
            const response = await fetch('/batch/rerun_validation_documents/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                },
                body: JSON.stringify(requestData)
            })
            const data = await response.json()
            if (data.status == 'success') {
                window.location.reload()
            } else {
                batchReRunValidationsContainer.classList.add('hidden');
                confirmBatchReRunValidations.classList.remove('pointer-events-none', 'opacity-50', 'w-20', 'text-center');
                confirmBatchReRunValidations.innerHTML = 'Re Run';
                generateNotification(data.status, data.message, (Math.random() + 1).toString(36).substring(7))
            }
        }
    })
}

// Batch Re Run Documents

const confirmBatchReRunDocuments = document.querySelector('#batch-rerun-documents-confirm');
if (confirmBatchReRunDocuments) {
    confirmBatchReRunDocuments.addEventListener('click', async () => {
        confirmBatchReRunDocuments.classList.add('pointer-events-none', 'opacity-50', 'w-20', 'text-center')
        confirmBatchReRunDocuments.innerHTML = `
            <span class="">
            <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_P7sC{transform-origin:center;animation:spinner_svv2 .75s infinite linear}@keyframes spinner_svv2{100%{transform:rotate(360deg)}}</style><path d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z" fill="#fff" class="spinner_P7sC "/></svg>
            </span>
        `
        let checkedDocuments = document.querySelectorAll('.single-checkbox:checked');
        let checkedDocumentsIDs = [];
        checkedDocuments.forEach((checkbox) => {
            checkedDocumentsIDs.push(checkbox.getAttribute('attr-id'))
        })
        if (checkedDocumentsIDs.length > 0) {
            const requestData = {
                documents: checkedDocumentsIDs
            }
            const response = await fetch('/batch/rerun_documents/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                },
                body: JSON.stringify(requestData)
            })
            const data = await response.json()
            if (data.status == 'success') {
                window.location.reload()
            } else {
                batchReRunContainer.classList.add('hidden');
                confirmBatchReRunDocuments.classList.remove('pointer-events-none', 'opacity-50', 'w-20', 'text-center');
                confirmBatchReRunDocuments.innerHTML = 'Re Run';
                generateNotification(data.status, data.message, (Math.random() + 1).toString(36).substring(7))
            }
        }
    })
}