const dropdownToggle = document.querySelector('.dropdown-toggle');
const dropdownMenu = document.querySelector('.dropdown-download-menu');

if (dropdownMenu && dropdownToggle) {
    dropdownToggle.addEventListener('click', function () {
        dropdownMenu.style.transition = 'width 0.5s';
        dropdownMenu.classList.toggle('hidden');
    });
    document.addEventListener('click', function (e) {
        if (!dropdownMenu.contains(e.target) && !dropdownToggle.contains(e.target)) {
            dropdownMenu.classList.add('hidden');
        }
    });
}