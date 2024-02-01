const open_delete_btn = document.querySelectorAll('.delete-button')
const delete_container = document.querySelector('.delete-container')
const close_delete_modal_btn = document.getElementById('delete-close-btn')

Array.from(open_delete_btn).forEach((delete_element) => {
    delete_element.addEventListener('click', () => {
        let recordID = delete_element.getAttribute('attr-id');
        let deleteModal = document.getElementById(`modal-${recordID}`);
        let closeDeleteModal = document.getElementById(`close-delete-modal-${recordID}`);
        deleteModal.classList.remove('hidden');
        closeDeleteModal.addEventListener('click', () => {
            deleteModal.classList.add('hidden')
        })
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                deleteModal.classList.add('hidden');
            }
        })
    })
})