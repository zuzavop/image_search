const config = {
    /**
     * @type {number}
     * @description number of trying before next search image
     */
    att: 20,

    /**
     * @type {number}
     * @description number of lines in result table
     */
    lines: 60,

    /**
     * @type {number}
     * @description number of images in results
     */
    showingPhotos: 300,

    /**
     * @type {number}
     * @description number of classes shown under each image
     */
    displayed_classes: 3,

    /**
     * @type {boolean}
     * @description enable showing last send query
     */
    showLastQuery: true,

    /**
     * @type {boolean}
     * @description enable similarity search
     */
    similaritySearchEnabled: true,

    /**
     * @type {string}
     * @description address to database of images
     */
    photosAddress: '../static/data/sea_photos/',

    /**
     * @type {number}
     * @description number of images on each line
     */
    photosOnLine: 5,//12,

    /**
     * @type {number}
     * @description number of images for shift
     */
    contextShift: 3,

    /**
     * @type {boolean}
     * @description enable shifting in context
     */
    shiftInContextEnabled: true,

    /**
     * @type {number[]}
     * @description numbers for shifting
     */
    contextIds: [-2, -1, 0, 1, 2],

    /**
     * @type {number}
     * @description size of currently used dataset
     */
    sizeDataset: 22036, //176, // 20000 for v3c and 22036 for sea dataset

    /**
     * @type {string}
     * @description connection for text query
     */
    connection: ', ',

    /**
     * @type {number}
     * @description for scaling percentage of occurrence of classes
     */
    percGrow: 1.4, //2, // for sea dataset 1.4 and for v3c 9
};

const text_cz = {
    warning: "Povolte cookies, prosím! Následně načtěte znovu aktuální stránku.",
    last_warning: "Poslední dotaz před zobrazením dalšího hledané snímku.",
    similarity_warning: "Musí být vybrán nějaký snímek.",
    context_warning: "Kontext snímku nemůže být odeslán.",
    right_answer: "Správná odpověď. Nový hledaný snímek bude zobrazen.",
    wrong_answer: "Špatná odpověď. Zkuste to znovu.",
    cookies_warning: "Povolte cookies, prosím."
}

const text_en = {
    warning: "Enable cookies, please! Then refresh this page.",
    last_warning: "Last search before displaying new search image.",
    similarity_warning: "Some image must be chosen.",
    context_warning: "Context of image can't be sent.",
    right_answer: "Right answer. New image will be generate.",
    wrong_answer: "Wrong answer. Try again.",
    cookies_warning: "Enable cookies, please."
}

let text;
if (navigator.language === "cs-CZ") {
    text = text_cz;
} else {
    text = text_en;
}
