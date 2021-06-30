// Download-related functions.

import { view, get_tid } from "./gui.js";
import { api } from "./api.js";

export { download_newick, download_image, download_svg };


// Download a file with the newick representation of the tree.
async function download_newick(node_id) {
    const tid = get_tid() + (node_id ? "," + node_id : "");
    const newick = await api(`/trees/${tid}/newick`);
    download(view.tree + ".tree", "data:text/plain;charset=utf-8," + newick);
}


// Download a file with the current view of the tree as a svg.
function download_svg() {
    const svg = div_viz.cloneNode(true)
    // Remove foreground nodeboxes for faster rendering
    // (Background nodes not excluded as they are purposely styled)
    Array.from(svg.getElementsByClassName("fg_node")).forEach(e => e.remove());
    apply_css(svg, document.styleSheets[0]);
    const svg_xml = (new XMLSerializer()).serializeToString(svg);
    const content = "data:image/svg+xml;base64," + btoa(svg_xml);
    download(view.tree + ".svg", content);
}


// Download a file with the current view of the tree as a png.
function download_image() {
    // dom-to-image dependency
    domtoimage
        .toPng(div_viz, {
            filter: node =>
            // Remove foreground nodeboxes for faster rendering
            // (Background nodes not excluded as they are purposely styled)
            !(node.classList && [...node.classList].includes("fg_node"))
        })
        .then(content => download(view.tree + ".png", content));
}


// Apply CSS rules to elements contained in a (cloned) container
function apply_css(container, stylesheet) {
    let styles = [];
    Array.from(stylesheet.rules).forEach(r => {
        const style = r.cssText;
        if (style) 
            styles.push(style);
    })
    const style_element = document.createElement("style");
    style_element.innerHTML = styles.join("\n");
    container.appendChild(style_element);
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
