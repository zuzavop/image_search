const welcome_page = {
    /**
     * Initializes the welcome page
     */
    init: function () {
        if (navigator.cookieEnabled) {
            // set cookies
            utils.setCookies(0, 0, "", "");
        } else {
            welcome_page.showCookiesWarning();
        }
    },

    /**
     * Shows warning message if cookies are not enabled
     */
    showCookiesWarning: function () {
        const startButton = document.getElementById("start-button");
        if (startButton) {
            startButton.style.display = "none";
        }

        // show warning about cookies
        const warning = document.createElement("div");
        warning.id = "warning";
        warning.textContent = text.warning;

        document.body.appendChild(warning);
    },
};

document.addEventListener('DOMContentLoaded', welcome_page.init);