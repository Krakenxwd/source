const tableContainer = document.querySelector('.table-container');
tableContainer.addEventListener('click', async (e) => {
    // Handle update field score event by firing a fetch request to the server
    if (e.target.classList.contains('update-field-score')) {
        const targetButton = e.target;
        const targetButtonID = targetButton.getAttribute('attr-id');
        const targetInput = document.querySelector(`input[attr-id="${targetButtonID}"]`);
        const requestData = {
            fieldId: targetButtonID,
            fieldValue: targetInput.value
        }
        const params = new URLSearchParams(requestData).toString()
        const url = `/settings/update_field_score?${params}`
        const data = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        const response = await data.json()
        if (response.code === 1) {
            generateNotification("success", response.message, "settings");
            document.getElementById(`field_score_${targetButtonID}`).innerText = targetInput.value;
        } else {
            generateNotification("failed", response.message, "settings");
        }
    }
    // Handle change status event by firing a fetch request to the server
    if ( e.target.classList.contains('change-field-status') ) {
        const targetInput = e.target;
        const targetInputID = targetInput.id;
        const requestData = {
            fieldId: targetInputID,
            fieldActive: targetInput.checked == '1' ? 'true' : 'false'
        }
        const params = new URLSearchParams(requestData).toString()
        const url = `/settings/update_field_status?${params}`
        const data = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        const response = await data.json()
        if (response.code === 1) {
            generateNotification("success", response.message, "settings");
        } else {
            generateNotification("failed", response.message, "settings");
            targetInput.checked = !targetInput.checked;
        }
    }
})