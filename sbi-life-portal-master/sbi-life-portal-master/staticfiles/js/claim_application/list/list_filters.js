const open_filters_modal = document.getElementById('open_filters_modal')
const filter_container = document.querySelector('.filter-container')
const close_filter_modal_btn = document.getElementById('close_filter_modal_btn')
const search_filters_count = document.getElementById('search_filters_count')
const filter_pills_container =  document.getElementById('filter-pills-container')
const filters_main_container = document.getElementById('filters-main-container')
const shift_filter_btn = document.querySelector('.shift-filter-btn')
const clear_filters_btn = document.getElementById('clear_filters_btn')

// Filter keys to be displayed in the filter pills
let filtersArray = ['search', 'status', 'mode', 'date_range', 'policy_no', 'claim_id', 'page']

shift_filter_btn.addEventListener('click', () => {
    filter_pills_container.scrollLeft += 20
})

open_filters_modal.addEventListener('click', () => {
    filter_container.classList.remove('hidden')
})

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('filter-container')) {
        filter_container.classList.add('hidden');
    
    }
})

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        filter_container.classList.add('hidden')
    
    }
})

document.addEventListener('keyup', (e) => {
    if (!filter_container.classList.contains('hidden')) {
        if (e.key === 'Enter') {
            document.getElementById('request').click()
        }
    }
})

close_filter_modal_btn.addEventListener('click', () => {
    filter_container.classList.add('hidden')
})

document.addEventListener('DOMContentLoaded', () => {  
    let filters_count = 0
    let url = window.location.href
    let urlValueObject = {}
    let dateParams = ['date_range']
    url.split('?')[1]?.split('&')?.forEach((param) => {
        let arr = param.split('=')
        if (!filtersArray.includes(arr[0])) {
            return;
        }
        if(arr[1] !== '') {
            if (dateParams.includes(arr[0])) {
                urlValueObject[arr[0]] = decodeURIComponent((arr[1] + '').replace(/\+/g, '%20'))
                filters_count++
            } else {
                urlValueObject[arr[0]] = arr[1]
                filters_count++
            }
        }
    })
    if (filters_count > 0) {
        search_filters_count.classList.remove('hidden')
        search_filters_count.innerHTML = filters_count ? filters_count : ''
        Object.keys(urlValueObject).forEach((key) => {
            let pill = document.createElement('div')
            pill.innerHTML = `
            <div class="flex filter-pill whitespace-nowrap flex-row-reverse items-center gap-2 px-3 py-2 text-sm w-min h-full bg-blue-700 rounded-md text-white select-none">
            <span class="remove-filter-button hover:bg-white hover:text-blue-700 rounded-full p-0.5 cursor-pointer" id="remove_${key}_filter">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
            </svg>																		  
            </span>
            <span class="flex gap-1">${convertCodeToText(key)}: <span class="text-white">${convertCodeToText(urlValueObject[key])}</span></span>
            </div>
            `
            filter_pills_container.appendChild(pill)
            document.getElementById('remove_' + key + '_filter').addEventListener('click', () => {
                filters_count--;
                restructureURL(key, url)
            })
        })
    } else {
        filters_main_container.classList.add('hidden')
    }
    if (filter_pills_container && filter_pills_container.childNodes.length > 1) {
        filter_pills_container.lastChild.style.marginRight = '4rem'
    }
    if (filter_pills_container.offsetWidth >= filters_main_container.offsetWidth) {
        shift_filter_btn.classList.remove('hidden')
    }
})

/**
 * Restructures the url and remove a the filter key.
 * @param {String} key The key of the filter to be removed
 * @param {String} url The url to be restructured
 */
function restructureURL(key, url) {
    let urlValueObject = {}
    url.split('?')[1]?.split('&')?.forEach((param) => {
        let arr = param.split('=')
        if(arr[1] !== '') {
            urlValueObject[arr[0]] = arr[1]
        }
    })
    if(key == 'search') {
        delete urlValueObject['search_type']
    }
    delete urlValueObject[key]
    let newUrl = url.split('?')[0]
    if (Object.keys(urlValueObject).length > 0) {
        newUrl = url.split('?')[0] + '?'
        Object.keys(urlValueObject).forEach((key) => {
            newUrl += `${key}=${urlValueObject[key]}&`
        })
    }
    if (newUrl.slice(-1) == '&') {
        newUrl = newUrl.slice(0, -1)
    }
    window.location.href = newUrl
}

/**
 * Convert code string to capitalized text
 * @param {String} code String to be formatted
 * @returns String
 */
function convertCodeToText(code) {
    return code.split('_').join(' ')
}