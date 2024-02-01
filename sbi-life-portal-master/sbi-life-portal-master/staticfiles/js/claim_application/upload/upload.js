/* global console */
/* global $ */
/* jshint esversion: 6 */

const gallery = document.getElementById("gallery");
const fileTempl = document.getElementById("file-template"), empty = document.getElementById("empty");
const $submitBtn = $('#submit-btn');
const $chooseFile = $('#choose-file');
const $cancel = $('#cancel');
const $uploadBox = $("#uploadBox");
let files = {};
let counter = 0;
let fileSize = 0;

function show_process_upload_btn_view(){
    $submitBtn.html(`<span><i class="fas fa-spin fa-atom mr-1"></i></span>Please wait while we uploading these files...`).addClass('rounded focus:outline-none cursor-default').removeClass('cursor-pointer').attr('disabled', true);
    return true;
}

function addFile(target, file) {
    
    let fileExtension = ['png', 'jpeg', 'tiff', 'tif', 'pdf', 'jpg'];
    const objectURL = URL.createObjectURL(file);
    const clone = fileTempl.cloneNode(true);
    if($.inArray(file.name.split('.').pop().toLowerCase(), fileExtension) !== -1){
        fileSize += file.size;
        clone.querySelector("#file-name").textContent = file.name;
        clone.querySelector("#file-name").title = file.name;
        clone.querySelector("#target-block").setAttribute('attr-url', objectURL);
        let fileSizeText = clone.querySelector("#file-size");
        if (file.size > 1024) {
            if (file.size > 1048576) {
                fileSizeText.textContent = Math.round(file.size / 1048576) + "mb";
            } else {
                fileSizeText.textContent = Math.round(file.size / 1024) + "kb";
            }
        } else {
            fileSizeText.textContent = file.size + "b";
        }
        empty.classList.add("hidden");
        target.prepend(clone.querySelector("#target-block"));
        files[objectURL] = file;
    }
}

$(document).on('click', '.remove-file', function (e){
    let target = e.target;
    let $closestTargetBlock = $(target).closest('#target-block');
    fileSize -= files[$closestTargetBlock.attr('attr-url')].size;
    delete files[$closestTargetBlock.attr('attr-url')];
    $closestTargetBlock.remove();
    if (Object.keys(files).length < 1 ) {
        $uploadBox.show();
        empty.classList.remove("hidden");
        $submitBtn.hide();
        $chooseFile.hide();
        $cancel.hide();
        return;
    }
    if(Math.round(fileSize / 1048576)<101){
        $submitBtn.show();
        $chooseFile.show();
        $cancel.show();
    }else{
        generateNotification("failed", "Selected files are larger than 100 MB.", "file");
    }
    $submitBtn.text(`Upload ${Object.keys(files).length} file`);
});

$(document).ready(function () {
    
    $submitBtn.hide();
    $("#id_file").on("change", function (e) {

        let elem = $('#id_file')[0];
        let is_file_size_gt_100 = false;
        for (const file of elem.files) {
            addFile(gallery, file);
        }
        if (Math.round(fileSize / 1048576) > 100) {
            is_file_size_gt_100 = true;
            generateNotification("failed", "Selected files are larger than 100 MB.", "file");
        }
        if (Object.keys(files).length > 0) {
            $submitBtn.show();
            if (Object.keys(files).length > 1) {
                $submitBtn.text(`Upload ${Object.keys(files).length} files`);
            } else {
                $submitBtn.text(`Upload ${Object.keys(files).length} file`);
            }
            $cancel.show();
            $uploadBox.hide();
            $chooseFile.show();
        }else {
            $submitBtn.hide();
            $uploadBox.show();
        }
        if (is_file_size_gt_100){
            $submitBtn.hide();
            $chooseFile.hide();
        }
    });
    $cancel.on("click", function (e) {
        e.preventDefault();
        window.location.href = "";
    });
    $('#uploadform').on('submit', function (){
        const dt = new DataTransfer();
        $('#id_file').val('');
        $.each(files, function(key, value) {
            dt.items.add(value);
        });
        $('#id_file')[0].files = dt.files;
    });
});

// Formset Handling JS

let childForm = document.querySelectorAll(".claim-formset")
let container = document.querySelector("#formset-form")
let addButton = document.querySelector("#add-form")
let totalForms = document.querySelector("#id_form-TOTAL_FORMS")

let formRegex = RegExp(`form-(\\d){1}-`,'g') //Regex to find all instances of the form number
let formNum = childForm.length-1

addButton.addEventListener('click', addForm)

function addForm(e) {
    e.preventDefault()
    let uniqueID = Math.random().toString(36).substring(2, 9)
    let newForm = childForm[0].cloneNode(true)
    newForm.id = `modal-${uniqueID}`
    let deleteButton = document.createElement('div');
    let classList = ['delete-button', 'absolute', '-right-2', '-top-2', 'p-2', 'border', 'cursor-pointer', 'hover:bg-red-50', 'hover:text-red-600', 'bg-white', 'rounded-full', 'shadow']
    deleteButton.classList.add(...classList)
    deleteButton.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 delete-button pointer-events-none">
            <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
        </svg>                                  
    `;
    deleteButton.id = `delete-${uniqueID}`
    newForm.appendChild(deleteButton)

    formNum++ //Increment the form number
    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formNum}-`) //Update the new form to have the correct form number
    container.insertBefore(newForm, addButton) //Insert the new form at the end of the list of forms

    totalForms.setAttribute('value', `${formNum+1}`) //Increment the number of total forms in the management form
}

document.getElementById('uploadform').addEventListener('click', (e) => {
    if (e.target.classList.contains('delete-button')) {
        let currentDeleteID = e.target.id.split('-')[1]
        document.getElementById(`modal-${currentDeleteID}`).remove()
        formNum--;
        totalForms.setAttribute('value', `${formNum+1}`)
        let allForms = document.querySelectorAll(".claim-formset")
        for(let i=0; i<allForms.length; i++){
            const elementsMatchingRegex = Array.from(allForms[i].querySelectorAll('[id^="id_form-"]')).filter(element => {
                const currentId = element.id;
                return currentId && currentId.match(formRegex);
            });
            Array.from(elementsMatchingRegex).forEach(element => {
                element.id = element.id.replace(formRegex, `form-${i}-`)
                element.name = element.name.replace(formRegex, `form-${i}-`)
            })
        }        
    }
})

document.querySelector('#uploadform').addEventListener('submit', (e) => {
    let allClaimantIDFormFields = document.querySelectorAll('.customer-id');
    let claimantIDs = [];
    Array.from(allClaimantIDFormFields).forEach((claimantIDFormField) => {
        claimantIDs.push(claimantIDFormField.value);
    })
    if (new Set(claimantIDs).size !== claimantIDs.length) {
        generateNotification("failed", "Customer IDs of any two policy entities cannot be same.", (Math.random() + 1).toString(36).substring(7))
        e.preventDefault()
        return false
    } else {
        show_process_upload_btn_view(); 
    }
})
