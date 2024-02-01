/* global console */
/* global $ */
/* jshint esversion: 6 */

let thisScript = document.currentScript;

let csrftoken = thisScript.getAttribute('csrf-token');
let $inviteEmail = $("#invite-email");
let $firstName = $("#first_name");
let $lastName = $("#last_name");

let inviteUserModal = document.querySelector('#invite_user_modal');
let inviteUserBtn = document.querySelector('#invite_user_btn');
let closeInviteUserModalBtn = document.querySelector('#close_invite_user_modal_btn');
inviteUserBtn.addEventListener('click', () => {
    inviteUserModal.classList.remove('hidden');
});
closeInviteUserModalBtn.addEventListener('click', () => {
    inviteUserModal.classList.add('hidden');
});

const openUserModalButtons = document.querySelectorAll('.open-user-role-modal');
const userRoleContainer = document.querySelector('.user-role-container');
const closeUserRoleModalBtn = document.querySelector('#close_user_modal_btn');
const assign_user_email = document.getElementById('assign_user_email');

const tableContainer = document.querySelector('.table-container');

tableContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('open-user-role-modal')) {
        let target_btn_id = e.target.getAttribute('attr-id');
        userRoleContainer.querySelector('[name="user-id"]').value = target_btn_id;
        userRoleContainer.classList.remove('hidden');
    }
});
closeUserRoleModalBtn.addEventListener('click', () => {
    userRoleContainer.classList.add('hidden');
});

$(document).ready(function () {

    $(".switch [type=checkbox]").click(function (evt) {
        evt.stopPropagation();
        let $target = $(evt.currentTarget);
        let userid = $target.attr('id');
        let is_checked = $target[0].checked;
        let url = window.location.href + 'change/status/';
        $.ajax({
            url: url, type: "GET", data: {
                user_id: userid, is_active: is_checked
            }
        }).done(function (data) {
            if (data.code === 1) {
                generateNotification("success", data.msg, "user");
            } else {
                generateNotification("failed", data.msg, "user");
            }
        }).catch((data) => {
            console.log(data);
        });
    });
});


window.onload = function check_status() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const searchTerm = urlParams.get('search');
    const groups = urlParams.get('groups')
    const isActive = urlParams.get('is_active')

    $('#search').val(searchTerm);
    $('#groups').val(groups);
    $('#is_active').val(isActive);
};