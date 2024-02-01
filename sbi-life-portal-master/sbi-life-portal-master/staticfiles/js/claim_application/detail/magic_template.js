/* global console */
/* global $ */
/* jshint esversion: 6 */


document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

Array.from(expandDetailCardButtons).forEach(expandDetailCardButton => {
    expandDetailCardButton.addEventListener('click', () => {
        let detailCardID = expandDetailCardButton.id.split('-')[2];
        let detailCard = document.getElementById(`detail-card-${detailCardID}`);
        detailCard.classList.toggle('invisible');
        detailCard.classList.toggle('h-0');
        detailCard.classList.remove('p-5');
        detailCard.classList.toggle('card-expanded');
        document.getElementById(`svg-${detailCardID}`).classList.toggle('rotate-180');
    });
})


expandCollapseToggleButton.addEventListener('click', () => {
    if (expandCollapseToggleButton.children[1].textContent === "Expand") {
        Array.from(detailCards).forEach(detailCard => {
            let detailCardID = detailCard.id.split('-')[2];
            detailCard.classList.toggle('invisible');
            detailCard.classList.toggle('h-0');
            detailCard.classList.toggle('card-expanded');
            document.getElementById(`svg-${detailCardID}`).classList.toggle('rotate-180');
        })
    } else {
        let expandedCards = document.getElementsByClassName('card-expanded');
        Array.from(expandedCards).forEach(expandedCard => {
            let expandedCardID = expandedCard.id.split('-')[2];
            expandedCard.classList.toggle('invisible');
            expandedCard.classList.toggle('h-0');
            expandedCard.classList.toggle('card-expanded');
            document.getElementById(`svg-${expandedCardID}`).classList.toggle('rotate-180');
        });
    }
});

document.addEventListener('click', () => {
    let expandedCards = document.getElementsByClassName('card-expanded');
    if (expandedCards.length > 0) {
        expandCollapseToggleButton.innerHTML = `
        <span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
            </svg>
        </span>
        <span>Expand</span>
        
        `;
    } else {
        expandCollapseToggleButton.innerHTML = `
                    <span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
            </svg>
        </span>
        <span>Collapse</span>
        `;
    }
});

document.querySelectorAll('.tab-link').forEach(tabLink => {
    tabLink.addEventListener('click', () => {
        document.querySelectorAll('.tab-link').forEach(tabLink => {
            tabLink.classList.remove('tab-active');
        });
        tabLink.classList.add('tab-active');
    });
});