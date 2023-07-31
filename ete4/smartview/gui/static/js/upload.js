// Functions for upload.html.

import { escape_html, hash, api_post } from "./api.js";


// Upload-related functions.

// When the upload button is pressed.
button_upload.addEventListener("click", async () => {
    try {
        assert(input_name.value || !check_metadata.checked, "Missing name");

        const name = check_metadata.checked ?
              input_name.value : hash(Date.now().toString());

        assert(!input_trees_file.disabled || !input_newick_string.disabled,
            "You need to supply a newick string or select a file");

        const data = new FormData();
        data.append("name", name);
        data.append("id", "13");  // FIXME: this needs to make some sense...
        data.append("internal", radio_name.checked ? "name" : "support");
        if (!input_newick_string.disabled)
            data.append("newick", input_newick_string.value.trim());
        else
            data.append("trees", await get_trees_file());

        const resp = await api_post("/trees", data);

        show_uploaded_trees(resp);
    }
    catch (ex) {
        Swal.fire({html: ex.message, icon: "warning",
                   toast: true, position: "top-end"});
    }
});


// Return the file containing the tree(s) as a newick or nexus.
async function get_trees_file() {
    assert(input_trees_file.files.length > 0, "Missing file");

    const size_MB = input_trees_file.files[0].size / 1e6;
    assert (size_MB < 30,
        `Sorry, the file is too big<br>` +
        `(${size_MB.toFixed(1)} MB, the maximum is 30 MB)`);

    return input_trees_file.files[0];
}


// Show the different added trees and allow to go explore them.
function show_uploaded_trees(resp) {
    const names = Object.keys(resp["ids"]);

    const link = name => `<a href="gui.html?` +
        `tree=${encodeURIComponent(name)}">${escape_html(name)}</a>`;

    if (names.length >= 1)
        Swal.fire({
            title: "Uploading Successful",
            html: "Added trees: " + names.map(link).join(", "),
            icon: "success",
            confirmButtonText: "Explore" + (names.length > 1 ? " the first" : ""),
            showCancelButton: true,
        }).then(result => {
            if (result.isConfirmed)
                window.location.href =
                    "gui.html?tree=" + encodeURIComponent(names[0]);
        });
    else
        Swal.fire({html: "Could not find any tree in file.", icon: "warning"});
}


// Load an example of a newick into the input text area.
function load_example() {
    radio_string.click();

    input_newick_string.value = `
    ((raccoon:19.19959,bear:6.80041):0.84600,((sea_lion:11.99700, seal:12.00300):7.52973,((monkey:100.85930,cat:47.14069):20.59201, weasel:18.87953):2.09460):3.87382,dog:25.46154);
    `.trim();
}
window.load_example = load_example;


// Radio buttons and checkboxes.

radio_file.addEventListener("click", () => {
    input_trees_file.disabled = false;
    input_newick_string.disabled = true;
});

radio_string.addEventListener("click", () => {
    input_newick_string.disabled = false;
    input_trees_file.disabled = true;
});

check_metadata.addEventListener("change", () => {
    div_metadata.style.display = check_metadata.checked ? "block" : "none";
});


// Error handling.

function assert(condition, message) {
    if (!condition)
        throw new Error(message);
}
