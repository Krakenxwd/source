const notificationModal = document.getElementById('success-notification-modal');
const notificationCloseBtn = document.getElementById('notification-close-btn');
if (notificationModal) {
    notificationCloseBtn.addEventListener('click', () => {
        notificationModal.classList.add('slide-out-slide');
        setTimeout(() => {
            notificationModal.classList.add('slide-hidden');
        }, 200);
    });
    setTimeout(() => {
        notificationModal.classList.add('slide-out-slide');
        setTimeout(() => {
            notificationModal.classList.add('slide-hidden');
        }, 200);
    }, 5000);
}

const failednotificationModal = document.getElementById('failed-notification-modal');
const failednotificationCloseBtn = document.getElementById('failed-notification-close-btn');
if (failednotificationModal) {
    failednotificationCloseBtn.addEventListener('click', () => {
        failednotificationModal.classList.add('slide-out-slide');
        setTimeout(() => {
            failednotificationModal.classList.add('slide-hidden');
        }, 200);
    });
    setTimeout(() => {
        failednotificationModal.classList.add('slide-out-slide');
        setTimeout(() => {
            failednotificationModal.classList.add('slide-hidden');
        }, 200);
    }, 5000);
}

/**
 * 
 * @param {String} type Category of notification. Can be "success" or "failed"
 * @param {String} message Message to be displayed in the notification
 * @param {String} id Uniuqe ID for the notification
 */
function generateNotification(type="success", message = "", id="") {
  let notificationDiv = document.createElement("div");
  let notificationDivClasses = ["text-sm", "shadow-lg", "flex", "flex-col", "gap-1", "w-96", "h-42", "p-5", "border", "rounded-md", "bg-white", "slide-out", "transform", "translate-x-0", "transition-transform", "duration-300", "ease-in-out"]
  notificationDiv.classList.add( ...notificationDivClasses );
  notificationDiv.id = `success-notification-modal-${id}`;
  let success = type == "success";
  notificationDiv.innerHTML = `
    <div class="flex items-center justify-between">
    <span class="p-2 ${ success ? "bg-green-50" : "bg-red-50" } w-min rounded-full">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
             stroke="currentColor" class="w-5 h-5 ${ success ? "text-green-500" : "text-red-500" }">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"/>
        </svg>
    </span>
    <span id="notification-close-btn-${id}" class="p-2 hover:bg-gray-50 w-min rounded-full cursor-pointer">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
             stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
    </span>
    </div>
    <div class="font-semibold">Information</div>
    <div class="text-sm text-gray-500" id="success-msg">${message}</div>
    `;
    let notifcationHolder = document.querySelector('.notification-holder');
    notifcationHolder.appendChild(notificationDiv);
    let notificationCloseBtn = notificationDiv.querySelector(`#notification-close-btn-${id}`);
    notificationCloseBtn.addEventListener('click', () => {
        notificationDiv.classList.add('slide-out-slide');
        setTimeout(() => {
            notificationDiv.classList.add('slide-hidden');
        }, 200);
    });
    setTimeout(() => {
        notificationDiv.classList.add('slide-out-slide');
        setTimeout(() => {
            notificationDiv.classList.add('slide-hidden');
        }, 200);
    }, 5000);
}