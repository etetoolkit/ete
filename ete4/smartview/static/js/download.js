// Download-related functions.

import { view, get_tid } from "./gui.js";
import { api } from "./api.js";

export { download_newick, download_image, download_svg };


// Download a file with the newick representation of the tree.
async function download_newick(node_id) {
    try {
        const tid = get_tid() + (node_id ? "," + node_id : "");
        const newick = await api(`/trees/${tid}/newick`);
        download(view.tree + ".tree", "data:text/plain;charset=utf-8," + newick);
    }
    catch (ex) {
        Swal.fire({html: `When downloading: ${ex.message}`, icon: "error"});
    }
}


// Download a file with the current view of the tree as a svg.
function download_svg() {
    const svg = div_tree.children[0].cloneNode(true);
    remove_unnecessary(svg);
    apply_css(svg);

    const svg_xml = (new XMLSerializer()).serializeToString(svg);
    const content = "data:image/svg+xml;base64," + btoa(svg_xml);

    download(view.tree + ".svg", content);
}


// Download a file with the current view of the tree as a png.
function download_image() {
    const canvas = document.createElement("canvas");
    canvas.width = div_tree.offsetWidth;
    canvas.height = div_tree.offsetHeight;

    const svg = div_tree.children[0].cloneNode(true);
    remove_unnecessary(svg);
    apply_css(svg);

    const svg_xml = (new XMLSerializer()).serializeToString(svg);
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.src = "data:image/svg+xml;base64," + btoa(svg_xml);
    img.addEventListener("load", () => {
        ctx.drawImage(img, 0, 0);
        download(view.tree + ".png", canvas.toDataURL("image/png"));
    });
}


// Make the browser download a file.
function download(fname, content) {
    const element = document.createElement("a");
    element.setAttribute("href", encodeURI(content));
    element.setAttribute("download", fname);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}


// Remove elements in container, the ones belonging to the given classes.
// For example, foreground nodeboxes, only useful for live mouse interaction.
function remove_unnecessary(container, unnecessary_classes=["fg_node"]) {
    unnecessary_classes.forEach(c =>
        Array.from(container.getElementsByClassName(c))
            .forEach(e => e.remove()));
}


// Apply CSS rules to the elements in the given container.
function apply_css(container) {
    const style = document.createElement("style");
    const rules = Array.from(document.styleSheets[0].cssRules);
    style.innerHTML = rules.map(r => r.cssText).join("\n");
    container.appendChild(style);
}
