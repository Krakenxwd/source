let el = document.querySelector('.items');
let sortedList = new Sortable(el, {
    group: {
        name: 'shared',
        pull: 'clone' // To clone: set pull to 'clone'
    },
    animation: 150,
    ghostClass: "sortable-ghost",
    onUpdate: function (evt) {
		// get current list of elements
        let items = sortedList.toArray()
        console.log(document.querySelector('#updated-order'));
        document.querySelector('#updated-order').value = items;
	},
});

// Style the layout for page labels and fields
let pageLabels = document.querySelectorAll('.master-page-label');
Array.from(pageLabels).forEach(pageLabel => {
    pageLabel.addEventListener('click', () => {
        Array.from(pageLabels).forEach(pageLabel => {
            pageLabel.classList.remove('bg-blue-700', 'text-white', 'font-medium');
        })
        let activeClasses = ['bg-blue-700', 'text-white', 'font-medium']
        pageLabel.classList.add(...activeClasses);
    })
})

let openFieldArrangerButton = document.querySelector('#open-field-arranger');
let fieldArrangerModal = document.querySelector('#field-arranger-modal');
let closeFieldArrangerButton = document.querySelector('#close-field-arranger');
openFieldArrangerButton.addEventListener('click', () => {
    fieldArrangerModal.classList.remove('hidden');
})
closeFieldArrangerButton.addEventListener('click', () => {
    fieldArrangerModal.classList.add('hidden');
})

let openScoreChangerButton = document.querySelector('#open-score-changer');
let scoreChangerModal = document.querySelector('#score-changer-modal');
let closeScoreChangerButton = document.querySelector('#close-score-changer-modal');
if (openScoreChangerButton) {
    openScoreChangerButton.addEventListener('click', () => {
        scoreChangerModal.classList.remove('hidden');
    })
}
if (closeScoreChangerButton) {
    closeScoreChangerButton.addEventListener('click', () => {
        scoreChangerModal.classList.add('hidden');
    })
}

