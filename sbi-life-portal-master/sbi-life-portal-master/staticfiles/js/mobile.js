const hamburgerMenu = document.querySelector('.hamburger-menu');
const closeHamburgerMenu = document.querySelector('.close-hamburger-menu');
const openHamburgerMenu = document.querySelector('.open-hamburger-menu');

if (openHamburgerMenu) {
    openHamburgerMenu.addEventListener('click', () => {
        if (hamburgerMenu) {
            hamburgerMenu.classList.remove('hidden');
        }
    })
}

if (closeHamburgerMenu) {
    closeHamburgerMenu.addEventListener('click', () => {
        if (hamburgerMenu) {
            hamburgerMenu.classList.add('hidden');
        }
    })
}

