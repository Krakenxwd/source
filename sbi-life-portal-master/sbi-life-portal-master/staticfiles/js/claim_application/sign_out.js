const open_sign_out_modal = document.getElementById('open_sign_out_btn')
const sign_out_container = document.querySelector('.sign_out_container')
const close_sign_out_modal_btn = document.getElementById('signout-close-btn')
const mobile_open_sign_out_btn = document.getElementById('mobile_open_sign_out_btn')
const mobileMenu = document.querySelector('.hamburger-menu');
open_sign_out_modal.addEventListener('click', () => {
    sign_out_container.classList.remove('hidden')
})

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('sign_out_container')) {
        sign_out_container.classList.add('hidden');
    }
})

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        sign_out_container.classList.add('hidden')
    }
})

document.addEventListener('keyup', (e) => {
    if (!sign_out_container.classList.contains('hidden')) {
        if (e.key === 'Enter') {
            document.getElementById('request').click()
        }
    }
})

close_sign_out_modal_btn.addEventListener('click', () => {
    sign_out_container.classList.add('hidden')
})

mobile_open_sign_out_btn.addEventListener('click', () => {
    if (mobileMenu) {
        mobileMenu.classList.add('hidden');
    }
    sign_out_container.classList.remove('hidden')
})