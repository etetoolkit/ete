// Download-related functions.

import { view, menus, get_tid } from "./gui.js";
import { api } from "./api.js";
import { apps } from "./pixi.js";

export { download_newick, download_seqs, download_image, download_svg, download_pdf };



// Download a file with the newick representation of the tree.
async function download_newick(node_id) {
    const nid = get_tid() + (node_id ? "," + node_id : "");
    const newick = await api(`/trees/${nid}/newick`);
    download(view.tree + ".tree", "data:text/plain;charset=utf-8," + newick);
}

async function download_seqs(node_id) {
    const nid = get_tid() + (node_id ? "," + node_id : "");
    const fasta = await api(`/trees/${nid}/seq`);
    download(view.tree + ".fasta", "data:text/plain;charset=utf-8," + fasta);
}


// Get clone of the current view to be downloaded as svg/pdf
function getElementToDownload() {
    const element = div_viz.cloneNode(true);
    // Remove aligned panel grabber
    element.querySelector("#div_aligned_grabber").remove();
    // Add pixi images to clone (canvas not downloadable)
    Object.entries(apps).forEach(([id, app]) => {
        const img = app.renderer.plugins.extract.image(app.stage);
        const container = element.querySelector(`#${id} .div_pixi`);
        container.style.top = app.stage._bounds.minY + "px";
        container.style.left = "10px";
        container.replaceChild(img, container.children[0]);
    });
    
    // Remove foreground nodeboxes for faster rendering
    // (Background nodes not excluded as they are purposely styled)
    Array.from(element.getElementsByClassName("fg_node")).forEach(e => e.remove());
    return element;
}


// Download a file with the current view of the tree as a svg+xml.
function download_svg() {
    const svg = getElementToDownload();
    apply_css(svg, document.styleSheets[0]);
    const svg_xml = (new XMLSerializer()).serializeToString(svg);
    const content = "data:image/svg+xml;base64," + btoa(svg_xml);
    download(view.tree + ".html", content);
}


// Download a file with the current view of the tree as a pdf.
function download_pdf() {

    function addSvg(svg, x, y) {
        SVGtoPDF(doc, svg, x * 3/4, y * 3/4);
    };

    function addImg(img, x, y, width, height) {
        doc.image(img.src, {
            x: x * 3/4,
            y: y * 3/4,
            fit: [ width * 3/4, height * 3/4 ],
        });
    };

    function addPixi() {
        element.querySelectorAll(".div_pixi").forEach(container => {
            const img = container.children[0];
            if (img)
                addImg(img, aligned_x + 10, +container.style.top.slice(0,-2),
                       img.width, img.height);
        });
    };
    
    const element = getElementToDownload();
    const box = div_viz.getBoundingClientRect();
    const doc = new PDFDocument({ size: [ box.width * 3/4, box.height * 3/4 ] });

    doc.fontSize(8).fillColor("#5d5d5d");

    const chunks = [];
    doc.pipe({
        // writable stream implementation
        write: (chunk) => chunks.push(chunk),
        end: () => {
          const pdfBlob = new Blob(chunks, {
            type: 'application/octet-stream'
          });
          download(`${view.tree}.pdf`, false, pdfBlob)
        },
        // readable streaaam stub iplementation
        on: () => {},
        once: () => {},
        emit: () => {},
    });

    const menus_width = menus.show ? menus.width : 0;

    const tree = element.querySelector("#div_tree svg");
    addSvg(tree)
    const aligned_x = div_aligned.getBoundingClientRect().x - menus_width;
    const aligned = element.querySelector("#div_aligned svg");
    const aligned_header = element.querySelector("#div_aligned_header svg");
    const aligned_footer = element.querySelector("#div_aligned_footer svg");
    [ aligned, aligned_header, aligned_footer ].forEach(el => {
        if (+el.getAttribute("width") !== 0)
            addSvg(el, aligned_x)
    });

    setTimeout(() => {
        // Pixi needs some time to render to img
        addPixi();
        doc.end();
    }, 100);
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
function download(fname, content, blob) {
    const element = document.createElement("a");
    if (content)
        element.setAttribute("href", encodeURI(content));
    else if (blob)
        element.setAttribute("href", URL.createObjectURL(blob));
    element.setAttribute("download", fname);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}
