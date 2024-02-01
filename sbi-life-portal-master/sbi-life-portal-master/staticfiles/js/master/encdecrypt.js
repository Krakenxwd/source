/* global console */
/* global $ */
/* jshint esversion: 6 */

let thisScript = document.currentScript;

let csrftoken = thisScript.getAttribute('csrf-token');

$('#encrypt-from, #decrypt-form').on('submit', async function (e) {
    e.preventDefault();

    try {
        const requestData = {
            simpleOutputTxt: $('#simpleOutputTxt').val(),
            encText: $('#dinputString').val()
        };

        const response = await $.ajax({
            url: '/master/ajax/encdryp/',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: requestData
        });
        if (response.code === 1) {
            const {encData, decrData} = response.data;
            $('#doutputString').val(decrData);
            $('#encOutputString').val(encData);
        } else {
            alert(response.msg);
        }
    } catch (error) {
        console.error(error);
    }

    return false;
});