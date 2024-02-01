const open_delete_btn = document.querySelectorAll('.delete-button')
const delete_container = document.querySelector('.delete-container')
const close_delete_modal_btn = document.getElementById('delete-close-btn')

const documentTable = document.getElementById('document_table')

if (documentTable) {
    documentTable.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-button')) {
            let recordID = e.target.getAttribute('attr-id');
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
        }
    })
}
