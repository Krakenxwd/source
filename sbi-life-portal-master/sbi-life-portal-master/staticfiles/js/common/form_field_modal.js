const successFormField = document.getElementById('success-form-field-modal');
const successFormFieldCloseBtn = document.getElementById('form-field-close-btn');
if (successFormField) {
    successFormFieldCloseBtn.addEventListener('click', () => {
        successFormField.classList.add('slide-out-slide');
        setTimeout(() => {
            successFormField.classList.add('slide-hidden');
        }, 200);
    });
    setTimeout(() => {
        successFormField.classList.add('slide-out-slide');
        setTimeout(() => {
            successFormField.classList.add('slide-hidden');
        }, 200);
    }, 5000);
}

const failedFormField = document.getElementById('failed-form-field-modal');
const failedFormFieldCloseBtn = document.getElementById('form-field-close-btn');
if (failedFormField) {
    failedFormFieldCloseBtn.addEventListener('click', () => {
        failedFormField.classList.add('slide-out-slide');
        setTimeout(() => {
            failedFormField.classList.add('slide-hidden');
        }, 200);
    });
    setTimeout(() => {
        failedFormField.classList.add('slide-out-slide');
        setTimeout(() => {
            failedFormField.classList.add('slide-hidden');
        }, 200);
    }, 5000);
}