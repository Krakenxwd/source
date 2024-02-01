let detailCards = document.getElementsByClassName('detail-card');
let expandDetailCardButtons = document.getElementsByClassName('expand-detail-card-button');
let expandCollapseToggleButton = document.getElementById('expand_collapse_btn')

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


expandCollapseToggleButton?.addEventListener('click', () => {
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
        })
    }
})

document.addEventListener('click', (e) => {
    let expandedCards = document.getElementsByClassName('card-expanded');
    if (expandedCards.length > 0) {
        expandCollapseToggleButton.innerHTML = `
        <span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
            </svg>
        </span>
        <span class="hidden sm:!block">Collapse</span>
        `;
    } else {
        if (expandCollapseToggleButton) {
            expandCollapseToggleButton.innerHTML = `
            <span>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.2" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
                </svg>
            </span>
            <span class="hidden sm:!block">Expand</span>
            `;
        }
    }

    if (e.target.classList.contains('open-policy-entity')) {
        showAllPolicyEntityData();
    }
});

const openActionsMenuButton = document.getElementById('open_actions_btn');
const actionsDropdownMenu = document.getElementById('actions_dropdown_menu');

if (openActionsMenuButton) {
    openActionsMenuButton.addEventListener('click', () => {
        actionsDropdownMenu.classList.toggle('hidden');
    });
}

if (actionsDropdownMenu) {
    document.addEventListener('click', (e) => {
        if (!e.target.classList.contains('action-area')) {
            actionsDropdownMenu.classList.add('hidden');
        }
    });
}
$("#validation-button").on("click", function (e) {
    e.preventDefault()
    closeOpenedSlides()
    if ($("#validation-modal").attr('class').split(/\s+/).includes("translate-x-full")) {
        $("#validation-modal").removeClass("translate-x-full")
        $("#validation-modal").addClass("translate-x-0")
        // $("#validations-overlay").removeClass("hidden")
    } else {
        $("#validation-modal").removeClass("translate-x-0")
        $("#validation-modal").addClass("translate-x-full")
        // $("#validations-overlay").addClass("hidden")
    }
})
$(document).on("click", "#validation-modal .close", function (e) {
    $("#validation-modal").removeClass("translate-x-0")
    $("#validation-modal").addClass("translate-x-full")
})
$("#files-button").on("click", function (e) {
    e.preventDefault()
    closeOpenedSlides()
    if ($("#files-modal").attr('class').split(/\s+/).includes("translate-x-full")) {
        $("#files-modal").removeClass("translate-x-full")
        $("#files-modal").addClass("translate-x-0")
    } else {
        $("#files-modal").removeClass("translate-x-0")
        $("#files-modal").addClass("translate-x-full")
    }
})
$(document).on("click", "#files-modal .close", function (e) {
    $("#files-modal").removeClass("translate-x-0")
    $("#files-modal").addClass("translate-x-full")
})

$("#page-validation-button").on("click", function (e) {
    e.preventDefault()
    closeOpenedSlides()
    if ($("#page-validation-modal").attr('class').split(/\s+/).includes("translate-x-full")) {
        $("#page-validation-modal").removeClass("translate-x-full")
        $("#page-validation-modal").addClass("translate-x-0")
    } else {
        $("#page-validation-modal").removeClass("translate-x-0")
        $("#page-validation-modal").addClass("translate-x-full")
    }
})
$(document).on("click", "#page-validation-modal .close", function (e) {
    $("#page-validation-modal").removeClass("translate-x-0")
    $("#page-validation-modal").addClass("translate-x-full")
})

function showAllPolicyEntityData() {
    closeOpenedSlides()
    if ($("#policy-entity-modal").attr('class').split(/\s+/).includes("translate-x-full")) {
        $("#policy-entity-modal").removeClass("translate-x-full")
        $("#policy-entity-modal").addClass("translate-x-0")
    } else {
        $("#policy-entity-modal").removeClass("translate-x-0")
        $("#policy-entity-modal").addClass("translate-x-full")
    }
}

$(document).on("click", "#policy-entity-modal .close", function (e) {
    $("#policy-entity-modal").removeClass("translate-x-0")
    $("#policy-entity-modal").addClass("translate-x-full")
})


// Annotation part for summary to not allow values to be changes by rubberbanding.

let thisScript = document.currentScript;

let url = '';
let scale = 1;

let preprocessed_file = thisScript.getAttribute('preprocessed-file');
let file_url = thisScript.getAttribute('file-url');
let doc_id = thisScript.getAttribute('document-id');

if (preprocessed_file) {
    url = preprocessed_file;
} else {
    url = file_url;
}
let currentPage = thisScript.getAttribute('page-num');
if (!currentPage) {
    currentPage = 1;
}
let activeItem = null;
let annHandler = null;


let validationName = "";


function showPageData(number) {
    let elemId = '#page-' + number.toString();
    $(elemId).removeClass('hidden');
    $('#nav-current-page').text(number.toString());

    // change the page label
    $('#page-label-' + number.toString()).removeClass('hidden');


    // change a url of page based on changing page
    let url = new URL(window.location.href);
    url.searchParams.set('pagenumber', number);
    window.history.replaceState({}, '', url);
}

function hidePageData(number) {
    let elemId = '#page-' + number.toString();
    $(elemId).addClass('hidden');

    // change the page label
    $('#page-label-' + number.toString()).addClass('hidden');
}

function uuid() {
    return 'xxxxxxxx_xxxx_4xxx_yxxx_xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        let r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}


$(document).on('click', '.set-active-item', function () {
    let elemId = $(this).attr('id');
    activeItem = $(`[set-active-attr-id=${elemId}]`).attr('field-attr-id').slice(0, -6)
    if (!annHandler) {
        return;
    }

    annHandler.clearAnnotation();

    let pageNo = parseInt(activeItem.split('-')[1]);

    let inputElem = '#' + activeItem + '-wmin';
    let w_min = parseFloat($(inputElem).val());

    inputElem = '#' + activeItem + '-wmax';
    let w_max = parseFloat($(inputElem).val());

    inputElem = '#' + activeItem + '-hmin';
    let h_min = parseFloat($(inputElem).val());

    inputElem = '#' + activeItem + '-hmax';
    let h_max = parseFloat($(inputElem).val());
    if (pageNo) {
        let rect = {
            id: "highlight",
            page: pageNo,
            type: "rect",
            fillColor: "#ff0000",
            text: "",
            color: "#ffffff",
            normalize: {
                wmin: w_min,
                hmin: h_min,
                wmax: w_max - w_min,
                hmax: h_max - h_min,
            },

        }
        annHandler.addAnnotation(rect);
    }
});


$(document).ready(function () {
    let config = {
        container: document.getElementById("pdf-container"),
        file: url,
        labels: [],
        readOnly: true,
        theme: "light",
    };

    const changePageButtons = document.querySelectorAll('.change-page-btn');

    PdfAnnotation.init(config).then((anno) => {
        annHandler = anno;
        anno.changePage(parseInt(currentPage));
        anno.on("pageChange", (page) => {
            activeItem = null;
            hidePageData(currentPage);
            currentPage = page.page;
            showPageData(currentPage);
        });

        changePageButtons.forEach((btn) => {
            btn.addEventListener('click', () => {
                let page = parseInt(btn.getAttribute('data-page'));
                anno.changePage(page);
            });
        })


    });

    showPageData(currentPage);


});
let observer = null;
document.addEventListener('DOMContentLoaded', () => {

    let options = {
        root: document.getElementById("cards_container"),
        rootMargin: "0px",
        threshold: 0.3,
    };

    observer = new IntersectionObserver(callback, options);

    let allEntityCards = document.querySelectorAll(".entity-card");
    Array.from(allEntityCards).forEach((entityCard) => {
        observer.observe(entityCard);
    });

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute("href")).scrollIntoView({
                behavior: "smooth",
            });
        });
    });

    let lastEntry = null;

    function callback(entries, observer) {
        entries.forEach((entry) => {
            if (entry.isIntersecting && entry.intersectionRatio > options.threshold) {
                if (lastEntry !== entry) {
                    clearAllActiveTabLinks();
                    const target_id = entry.target.id;
                    document.querySelector(`[data-id="${target_id}"]`)?.classList.add("tab-active");
                    lastEntry = entry;
                }
            }
        });
    }
})

function clearAllActiveTabLinks() {
    let allTabLinks = document.querySelectorAll('.tab-link');
    Array.from(allTabLinks).forEach(tabLink => {
        tabLink.classList.remove('tab-active');
    })
}

function closeOpenedSlides() {
    let openedSlides = document.querySelectorAll('.translate-x-0');
    Array.from(openedSlides).forEach(openedSlide => {
        openedSlide.classList.remove('translate-x-0');
        openedSlide.classList.add('translate-x-full');
    })
}