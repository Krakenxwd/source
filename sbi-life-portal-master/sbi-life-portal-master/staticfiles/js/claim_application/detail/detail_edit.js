
/* global console */
/* global $ */
/* jshint esversion: 6 */

let thisScript = document.currentScript;

let url = '';
let scale = 1;

let preprocessed_file = thisScript.getAttribute('preprocessed-file');
let file_url = thisScript.getAttribute('file-url');
let doc_id = thisScript.getAttribute('document-id');

if (preprocessed_file) {
    url = preprocessed_file;
    scale = 0.4;
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


$(document).on('focus', '.set-active-item', function () {
    activeItem = $(this).attr('id').slice(0, -6);
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
});


function change_triggers_refresh(i, t) {
    i.off('change');
    i.change(function (event) {
        let elemId = event.target.getAttribute('id');
        let tokens = elemId.split('-');
        tokens = tokens.slice(0, tokens.length - 1);
        tokens.push('changed');
        elemId = '#' + tokens.join('-');
        $(elemId).val(1);
        $('#save-btn').show();
    });
    t.off('change');
    t.change(function (event) {
        let elemId = event.target.getAttribute('id');
        let tokens = elemId.split('-');
        tokens = tokens.slice(0, tokens.length - 1);
        tokens.push('changed');
        elemId = '#' + tokens.join('-');
        $(elemId).val(1);
        $('#save-btn').show();
    });
}

$(document).on('keyup', 'input[type=number]', function () {
    this.setAttribute('value', this.value);
    this.step = this.value.replace(/[^.]/g, "0").replace(/\d$/, "1");
});


$(document).ready(function () {
    let config = {
        container: document.getElementById("pdf-container"),
        file: url,
        labels: [],
        theme: "light"
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

        anno.on("createAnnotation", (a, annotation) => {
            if (annotation.id === 'highlight') return;
            if (activeItem !== null) {
                let w_min = annotation.normalize.wmin;
                let h_min = annotation.normalize.hmin;
                let w_max = annotation.normalize.wmax;
                let h_max = annotation.normalize.hmax;

                w_max = w_min + w_max;
                h_max = h_min + h_max;

                let findTextURL = '/' + doc_id + '/' + currentPage.toString() + '/find_text/';
                findTextURL = findTextURL + '?w_min=' + w_min;
                findTextURL = findTextURL + '&w_max=' + w_max;
                findTextURL = findTextURL + '&h_min=' + h_min;
                findTextURL = findTextURL + '&h_max=' + h_max;
                findTextURL = findTextURL + '&page_plus_field=' + activeItem;
                $.get(findTextURL, function (data) {
                    let text = data['text'];
                    let textElem = '#' + activeItem + '-value';
                    $(textElem).attr('value', text);
                    $(textElem).val(text);
                    if ($(textElem + '[type=number]').length > 0) {
                        $(textElem + '[type=number]').attr('step', $(textElem + '[type=number]').val().replace(/[^.]/g, "0").replace(/\d$/, "1"))
                    }


                    let inputElem = '#' + activeItem + '-wmin';
                    $(inputElem).val(w_min);

                    inputElem = '#' + activeItem + '-hmin';
                    $(inputElem).val(h_min);

                    inputElem = '#' + activeItem + '-wmax';
                    $(inputElem).val(w_max);

                    inputElem = '#' + activeItem + '-hmax';
                    $(inputElem).val(h_max);

                    inputElem = '#' + activeItem + '-changed';
                    $(inputElem).val(1);
                    activeItem = null;
                    anno.clearAnnotation();
                    $('#save-btn').show();
                });

            }
        });


    });


    showPageData(currentPage);
    change_triggers_refresh($('input[data-item]'), $('textarea[data-item]'))
    $('#save-btn').hide();
    $('select[data-item]').change(function (event) {
        let elemId = event.target.getAttribute('id');
        let tokens = elemId.split('-');
        tokens = tokens.slice(0, tokens.length - 1);
        tokens.push('changed');
        elemId = '#' + tokens.join('-');
        $(elemId).val(1);
        $('#save-btn').show();
    });

});