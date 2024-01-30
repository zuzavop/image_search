const mainWindow = {
    /**
     * @type {number}
     * @description index of currently selected
     */
    selectedId: -1,
    /**
     * @type {number}
     * @description index of middle image in context
     */
    middleId: -1,
    /**
     * @type {number}
     * @description index of currently search image
     */
    found: -1,
    /**
     * @type {number}
     * @description number of trying on current image
     */
    trying: -1,
    /**
     * @type {string}
     * @description text of last query
     */
    lastQuery: "",

    /**
     * initialize variables and set history
     */
    init: function () {
        // setting cookies and local variables about attempts
        document.cookie = 'activity=""';
        if (mainWindow.found === -1) {
            if (utils.getCookie("index") && utils.getCookie("trying")) {
                mainWindow.found = parseInt(utils.getCookie("index"));
                mainWindow.trying = parseInt(utils.getCookie("trying"));
                if (utils.getCookie("last_query")) {
                    mainWindow.lastQuery = utils.getCookie("last_query").slice(1, -1);
                } else {
                    document.cookie = 'last_query=""';
                    mainWindow.lastQuery = "";
                }
            } else {
                utils.setCookies(0, 0, "");
                mainWindow.found = 0;
                mainWindow.trying = 0;
            }
        }
    },

    /**
     * sends text query
     */
    searching: function () {
        // send text query
        let query = document.getElementById('search-text').value;
        if (mainWindow.trying === config.att) {
            utils.setCookies(mainWindow.found + 1, 0, "", "");
            location.href = '?s';
        } else if (query.length > 0) {
            if (mainWindow.trying === (config.att - 1)) { // display alert - last search
                if (!confirm(text.last_warning)) {
                    return;
                }
            }
            utils.setCookies(mainWindow.found, mainWindow.trying + 1, query);
            location.href = '?query="' + query + '"';
        }
    },

    /**
     * sends query for similarity search
     */
    simSearch: function () {
        // send query for similarity search
        if (mainWindow.selectedId !== -1) {
            if (mainWindow.trying === config.att) {
                utils.setCookies(mainWindow.found + 1, 0, "", "");
                location.href = '?s';
            } else {
                if (mainWindow.trying === (config.att - 1)) { // display alert - last search
                    if (!confirm(text.last_warning)) {
                        return;
                    }
                }
                utils.setCookies(mainWindow.found, mainWindow.trying + 1, "");
                location.href = '?sim_id=' + mainWindow.selectedId;
            }
        } else {
            alert(text.similarity_warning);
        }
    },

    /**
     * clear text query
     */
    clearSearch: function () {
        // clear text of search
        document.getElementById('search-text').value = '';
        document.cookie = 'activity=""';
    },

    /**
     * shows images in context of database
     * @param {number} id - id of selected image
     */
    showContext: function (id) {
        // show images in context of database
        mainWindow.middleId = id;
        document.getElementsByClassName("context")[0].innerHTML = '';
        let newId;
        for (let i of config.contextIds) {
            newId = id + i
            if (newId > 0 && newId < config.sizeDataset) {
                const image = utils.createImage(newId, "w" + (newId).toString());
                image.addEventListener("click", function (e) {
                    if (e.ctrlKey) {
                        if (id === parseInt(image.id.slice(1))) mainWindow.controlAndSend(image.id.slice(1));
                        else alert(text.context_warning)
                    } else {
                        mainWindow.select(image.id, false);
                    }
                });
                document.getElementsByClassName("context")[0].appendChild(image);
            }
        }
    },

    /**
     * selects image and shows its context if double click
     * @param {string} id - id of currently selected image
     * @param {boolean} [newContext=true] - if a shifting in context is allowed
     */
    select: function (id, newContext = true) {
        // select image and show it context
        if (mainWindow.selectedId !== -1) {
            document.getElementById(mainWindow.selectedId.toString()).setAttribute("class", "unselected");
        }

        // in context
        if (id.startsWith("w")) {
            return;
        }

        if (newContext && mainWindow.selectedId === parseInt(id)) {
            let parent = document.querySelector(".modal-parent");
            if (parent) {
                parent.style.display = "block";
            }

            if (config.shiftInContextEnabled) {
                document.getElementsByClassName('previous')[0].style.visibility = 'visible';
                document.getElementsByClassName('next')[0].style.visibility = 'visible';
            }
            mainWindow.showContext(parseInt(id));
        }

        mainWindow.selectedId = parseInt(id);
        document.getElementById(id).setAttribute("class", "selected");
    },

    /**
     * controls result and sends query for new image if correct
     * @param {string} id - id of image being checked
     */
    controlAndSend: function (id) {
        // control result and if correct send query for new image
        let findId = parseInt(document.getElementsByClassName("find-img")[0].id.slice(0, -1));
        if (parseInt(id) === findId) {
            alert(text.right_answer)
            utils.setCookies(mainWindow.found + 1, 0, "", "");
            location.href = '?answer=' + id;
        } else {
            alert(text.wrong_answer);
        }
    },

    /**
     * adds text to text query and sets focus to end
     * @param {string} text - text to be added to search text
     * @param {string} [id] - id of last selected image
     */
    addText: function (text, id) {
        // add text to text search and set focus to end
        const input = document.getElementById('search-text');
        if (input) {
            let end = input.value.length;
            if (end > 0) {
                input.value += config.connection + text;
            } else {
                input.value += text;
            }
            end = input.value.length;
            input.setSelectionRange(end, end);
            input.focus();
            if (id) {
                const last = utils.getCookie("activity");
                document.cookie = 'activity=' + last.slice(0, -1) + text + ":" + id + '|"';
            }
        }
    },

    /**
     * send request for next image to search
     */
    nextSearch: function () {
        // showing next image for search
        utils.setCookies(mainWindow.found + 1, 0, "", "");
        location.href = '?s';
    },

    /**
     * close window with context
     */
    closeWindow: function () {
        // closing of context window
        utils.openOrCloseWindow(".modal-parent", false);
    },

    /**
     * close help window
     */
    closeHelpWindow: function () {
        // closing of context window
        utils.openOrCloseWindow(".help-parent", false);
    },

    /**
     * show popup window with help
     */
    showHelp: function () {
        // display text of help
        utils.openOrCloseWindow(".help-parent", true);
    },

    /**
     * send query for bayes update
     */
    bayes : function () {
        if (mainWindow.selectedId !== -1) {
            if (mainWindow.trying === config.att) {
                utils.setCookies(mainWindow.found + 1, 0, "", "");
                location.href = '?s';
            } else {
                if (mainWindow.trying === (config.att - 1)) { // display alert - last search
                    if (!confirm(text.last_warning)) {
                        return;
                    }
                }
                utils.setCookies(mainWindow.found, mainWindow.trying + 1, "");
                location.href = '?b_id=' + mainWindow.selectedId;
            }
        } else {
            alert(text.similarity_warning);
        }
    },
};

document.addEventListener('DOMContentLoaded', mainWindow.init);
