const aside_menu = document.querySelector(".aside-menu");
const menu_item_text = document.getElementsByClassName("menu-item-text");
const menu_item = document.getElementsByClassName("menu-item");

const vendor_menu_item_title_text = document.querySelector(
    ".vendor-menu-item-title-text"
);

const nested_menu = document.querySelector(".nested-menu-item");
const nested_menu_item_title = document.querySelector(
    ".nested-menu-item-title"
);
const vendors_svg = document.querySelector(".vendors-svg");

const nested_menu_settings = document.querySelector(
    ".nested-menu-item-settings"
);
const nested_menu_item_title_settings = document.querySelector(
    ".nested-menu-item-title-settings"
);
const settings_svg = document.querySelector(".settings-svg");

const logo_with_text = document.querySelector(".logo-with-text");
const logo_without_text = document.querySelector(".logo-without-text");

const main_vendor_submenu = document.querySelector(".main-vendor-submenu");
const main_settings_submenu = document.querySelector(".main-settings-submenu");
const vendor_menu_item = document.querySelectorAll(".vendor-menu-item");
const settings_menu_item = document.querySelectorAll(".settings-menu-item");

if (menu_item_text) {
    Array.from(menu_item_text).forEach((item) => {
        item.style.display = "none";
    });
}
if (aside_menu) {
    aside_menu.style.padding = "0.5rem";
}
if (logo_with_text) {
    logo_with_text.style.display = "none";
}
aside_menu?.addEventListener("mouseenter", function () {
    document.querySelector(".backdrop").classList.remove("hidden");
    settings_menu_item.forEach((item) => {
        if (item.classList.contains("menu-item-active")) {
            main_settings_submenu.classList.add("px-3");
            main_settings_submenu.classList.add("w-64");
        }
    });
    vendor_menu_item.forEach((item) => {
        if (item.classList.contains("menu-item-active")) {
            main_vendor_submenu.classList.add("px-3");
            main_vendor_submenu.classList.add("w-64");
        }
    });
    logo_without_text.style.display = "none";
    logo_with_text.style.display = "block";
    aside_menu.style.width = "17rem";
    aside_menu.style.transition = "width 0.2s";
    if (nested_menu) {
        nested_menu.classList.remove("mx-auto");
    }
    if (nested_menu_settings) {
        nested_menu_settings.classList.remove("mx-auto");
    }
    if (menu_item_text) {
        Array.from(menu_item_text).forEach((item) => {
            item.style.display = "block";
            Array.from(menu_item).forEach((item) => {
                item.classList.remove("justify-center");
                item.classList.add("pl-5");
                item.classList.add("justify-start");
            });
        });
    }
});

aside_menu?.addEventListener("mouseleave", function mouseLeaveFn() {
    logo_without_text.style.display = "block";
    if (main_settings_submenu) {
        if (main_settings_submenu.classList.contains("w-64")) {
            main_settings_submenu.classList.remove("px-3");
            main_settings_submenu.classList.remove("w-64");
        }
    }
    if (main_vendor_submenu) {
        if (main_vendor_submenu.classList.contains("w-64")) {
            main_vendor_submenu.classList.remove("px-3");
            main_vendor_submenu.classList.remove("w-64");
        }
    }
    document.querySelector(".backdrop").classList.add("hidden");
    logo_with_text.style.display = "none";
    aside_menu.style.width = "4rem";
    if (nested_menu) {
        nested_menu.classList.add("mx-auto");
    }
    if (nested_menu_settings) {
        nested_menu_settings.classList.add("mx-auto");
    }
    if (menu_item_text) {
        Array.from(menu_item_text).forEach((item) => {
            item.style.display = "none";
        });
        Array.from(menu_item).forEach((item) => {
            item.classList.add("justify-center");
            item.classList.remove("pl-5");
            item.classList.remove("justify-start");
        });
        if (settings_svg) {
            settings_svg.style.transform = "rotate(0deg)";
        }
        if (vendors_svg) {
            vendors_svg.style.transform = "rotate(0deg)";
        }
    }
});

if (nested_menu_settings) {
    nested_menu_settings.addEventListener("click", () => {
        if (main_vendor_submenu) {
            if (main_vendor_submenu.classList.contains("w-64")) {
                main_vendor_submenu.classList.remove("px-3");
                main_vendor_submenu.classList.remove("w-64");
            }
        }
        main_settings_submenu.classList.toggle("px-3");
        main_settings_submenu.classList.toggle("w-64");
    });
}

if (nested_menu_item_title) {
    nested_menu_item_title.addEventListener("click", () => {
        if (main_settings_submenu.classList.contains("w-64")) {
            main_settings_submenu?.classList.remove("px-3");
            main_settings_submenu?.classList.remove("w-64");
        }
        main_vendor_submenu.classList.toggle("px-3");
        main_vendor_submenu.classList.toggle("w-64");
    });
}