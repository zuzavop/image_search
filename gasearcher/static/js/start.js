const createMainWindow = {
    /**
     * Initializes main window
     */
    init: function () {
        if (!navigator.cookieEnabled) {
            if (confirm(text.cookies_warning)) {
                location.reload();
            }
        }

        // create button in context
        if (config.shiftInContextEnabled) {
            createMainWindow.createContext();
        }

        // hide similarity searcher button if similarity search isn't enable
        if (!config.similaritySearchEnabled) {
            document.getElementById("similarity-searcher").style.display = "none";
        }

        // load last text query to searcher
        if (config.showLastQuery) {
            document.getElementById("search-text").value = mainWindow.lastQuery;
        }

        // set sending query on enter press
        document.getElementById("search-text").addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                mainWindow.searching();
            }
        });

        // allow closing popup windows with escape
        document.addEventListener("keydown", e => {
            if (e.key === "Escape" || e.key === "Esc") {
                mainWindow.closeWindow();
                mainWindow.closeHelpWindow();
            }
            if (config.similaritySearchEnabled) {
                if (e.ctrlKey && e.key === 's') {
                    mainWindow.simSearch();
                }
            }
        });
    },

    /**
     * create table for images
     */
    createImageTable: function () {
        const tb = document.getElementsByClassName('div-table')[0];
        if (tb) {
            for (let i = 0; i < config.lines; i++) {
                const tr = document.createElement('tr');
                tr.id = i.toString() + 'tr';
                tb.appendChild(tr);
            }
        }
    },

    /**
     * create div containing an image and its classes
     * @param {string} id - id of the image
     * @param {string[]} values - classes of the image
     * @param {number} num - position of the image
     */
    createImageBlock: function (id, values, num) {
        let div = createMainWindow.createImage(parseInt(id), num);
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = "image-buttons";
        div.appendChild(buttonsDiv);
        createMainWindow.createButtons(buttonsDiv, values, id);
    },

    /**
     * create an image
     * @param {number} id - id of the image
     * @param {number} num - position of the image
     */
    createImage: function (id, num) {
        const div = document.createElement('td');
        div.className = 'img-div';
        document.getElementById(Math.floor(num / config.photosOnLine) + 'tr').appendChild(div);
        const image = utils.createImage(id, id.toString());
        div.appendChild(image);
        image.addEventListener("click", function (e) {
            if (e.ctrlKey) {
                mainWindow.controlAndSend(image.id);
            } else {
                mainWindow.select(image.id);
            }
        });
        return div;
    },

    /**
     * create buttons of classes
     * @param {HTMLDivElement} buttonsDiv - div to which buttons will be created
     * @param {string[]} values - labels of buttons
     * @param {string} id - id of image in given div
     */
    createButtons: function (buttonsDiv, values, id) {
        // create buttons with labels/classes
        let i = 1;
        for (let e in values) {
            const but = utils.createButton(classes[values[e]], (i > config.displayed_classes) ? "more-b hidden" : null, "b" + id);
            buttonsDiv.appendChild(but);
            but.style.background = utils.percToColor(percentClass[values[e]]);
            but.addEventListener("click", function () {
                mainWindow.addText(but.textContent, but.id.slice(1));
            });
            i++;
        }
        const but = utils.createButton('+', "plus-but");
        but.addEventListener("click", function () {
            createMainWindow.showMoreClasses(buttonsDiv, but);
        });
        buttonsDiv.appendChild(but);
    },

    /**
     * show or hide more classes in given div
     * @param {HTMLDivElement} buttonsDiv - div containing buttons of classes
     * @param {HTMLButtonElement} button - button which show or hide classes
     */
    showMoreClasses: function (buttonsDiv, button) {
        // create button for showing more labels
        const butt = buttonsDiv.getElementsByClassName("more-b");
        for (let b of butt) {
            b.classList.toggle("hidden");
        }
        if (button.textContent === "+") {
            button.textContent = "-";
        } else {
            button.textContent = "+";
        }
    },

    /**
     * create buttons for top classes
     * @param {string[]} topClasses - names of top classes
     */
    createTopClasses: function (topClasses) {
        // create buttons of most common classes in currently shown result
        for (let c in topClasses) {
            const button = utils.createButton(classes[parseInt(topClasses[c])]);
            button.addEventListener("click", function () {
                mainWindow.addText(button.textContent);
            });
            document.getElementById("search-text").after(button);
        }
        document.getElementById("search-text").after(document.createElement('br'));
    },

    /**
     * create window for context
     */
    createContext: function () {
        // create buttons for shifting context of image
        const buttPrev = utils.createButton('<', "previous cont-butt");
        buttPrev.addEventListener("click", function () {
            if (mainWindow.middleId - config.contextShift >= 0) {
                mainWindow.showContext(mainWindow.middleId - config.contextShift);
            }
        });
        document.getElementsByClassName("popup-window")[0].appendChild(buttPrev);

        const buttNext = utils.createButton('>', "next cont-butt");
        buttNext.addEventListener("click", function () {
            if (mainWindow.middleId + config.contextShift <= config.sizeDataset) {
                mainWindow.showContext(mainWindow.middleId + config.contextShift);
            }
        });
        document.getElementsByClassName("popup-window")[0].appendChild(buttNext);
    },

    /**
     * create div with currently searched image
     * @param {number} fin - id of currently search image
     */
    createWanted: function (fin) {
        // create image of currently search image
        const div = document.createElement("div");
        div.className = "find-img-div";
        const img = utils.createImage(fin, fin.toString() + 'r', "find-img");
        div.appendChild(img);

        // create button for skipping currently searching image
        const button = utils.createButton("Next", "bar-item", "next-button");
        button.addEventListener("click", function () {
            mainWindow.nextSearch();
        });
        div.appendChild(button)
        document.getElementsByClassName("sidebar")[0].appendChild(div);
    },

    /**
     * hide bar buttons except Next button
     */
    hideBarButtons: function () {
        // hide buttons used for search
        document.getElementById('search-text').style.visibility = 'hidden';
        document.getElementById('clear').style.visibility = 'hidden';
        document.getElementById('next-button').style.visibility = 'hidden';
        document.getElementById('similarity-searcher').style.visibility = 'hidden';
        document.getElementById('text-searcher').innerText = 'Next';
    },
};

document.addEventListener('DOMContentLoaded', createMainWindow.init);
