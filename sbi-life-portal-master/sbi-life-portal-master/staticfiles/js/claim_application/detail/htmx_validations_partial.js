let fieldValidationsButton = document.querySelector('#field-validations-button');
let pageValidationsButton = document.querySelector('#page-validations-button');
let fieldValidationsModal = document.querySelector('#field-wise-validations-modal');
let pageValidationsModal = document.querySelector('#page-wise-validations-modal');

fieldValidationsButton.addEventListener('click', () => {
    fieldValidationsModal.classList.remove('hidden');
    pageValidationsModal.classList.add('hidden');
    fieldValidationsButton.classList.add('validation-tab-active')
    pageValidationsButton.classList.remove('validation-tab-active')
})

pageValidationsButton.addEventListener('click', () => {
    pageValidationsModal.classList.remove('hidden');
    fieldValidationsModal.classList.add('hidden');
    fieldValidationsButton.classList.remove('validation-tab-active')
    pageValidationsButton.classList.add('validation-tab-active')
})