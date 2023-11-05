// Download-related functions.

import { view, menus, get_tid } from "./gui.js";
import { api } from "./api.js";
import { apps } from "./pixi.js";

export { download_newick, download_seqs, download_svg, download_pdf };



// Download a file with the newick representation of the tree.
async function download_newick(node_id) {
    const nid = get_tid() + (node_id.length > 0 ? ("," + node_id) : "");
    const newick = await api(`/trees/${nid}/newick`);
    download(view.tree + ".tree", "data:text/plain;charset=utf-8," + newick);
}


async function download_seqs(node_id) {
    const nid = get_tid() + (node_id.length > 0 ? ("," + node_id) : "");
    const fasta = await api(`/trees/${nid}/seq`);
    download(view.tree + ".fasta", "data:text/plain;charset=utf-8," + fasta);
}


// Get clone of the current view to be downloaded as svg/pdf
function getElementToDownload() {
    const element = div_viz.cloneNode(true);
    // Remove aligned panel grabber
    element.querySelector("#div_aligned_grabber").remove();
    element.querySelector("#div_aligned").style.overflow = "hidden";
    // Add pixi images to clone (canvas not downloadable)
    Object.entries(apps).forEach(([id, app]) => {
        const img = app.renderer.plugins.extract.image(app.stage);
        const container = element.querySelector(`#${id} .div_pixi`);
        container.style.top = app.stage._bounds.minY + "px";
        container.style.left = `${app.stage._bounds.minX}px`;
        container.style.width = "auto";
        container.replaceChild(img, container.children[0]);
    });

    // Remove foreground nodeboxes for faster rendering
    // (Background nodes not excluded as they are purposely styled)
    Array.from(element.getElementsByClassName("fg_node")).forEach(e => e.remove());

    return element;
}


// Download a file with the current view of the tree as a svg+xml,
// and another file with the legend.
function download_svg() {
    // Download tree
    const tree_svg = getElementToDownload();
    apply_css(tree_svg);
    const tree_xml = (new XMLSerializer()).serializeToString(tree_svg);
    const tree_content = "data:image/svg+xml;base64," + btoa(tree_xml);
    download(view.tree + ".svg", tree_content);

    // Download legend
    const legend_svg = div_legend.cloneNode(true);
    apply_css(legend_svg);
    const legend_xml = (new XMLSerializer()).serializeToString(legend_svg);
    const legend_content = "data:image/svg+xml;base64," + btoa(legend_xml);
    download(view.tree + "_legend.svg", legend_content);
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

    function addAlignedBackground() {
        const x = aligned_x * 3/4
        const w = aligned_box.width
        doc.rect(x, 0, w, view.tree_size.height / view.zoom.y);
        doc.fill("white").strokeColor("white");
        doc.stroke();
    }

    function addPixiBackground() {
        const x = (aligned_x - 5) * 3/4
        const w = view.aligned.x * 3/4
        doc.rect(x - w, 0, w, view.tree_size.height / view.zoom.y);
        doc.fill("white").strokeColor("white");
        doc.stroke();
    }

    function addPixi() {
        element.querySelectorAll(".div_pixi").forEach(container => {
            const img = container.children[0];
            if (img)
                addImg(img, aligned_x - (view.drawer.type === "rect" ? view.aligned.x : 0),
                      +container.style.top.slice(0,-2),
                       img.width, img.height);
        });
        if (view.aligned.x > 0)
            addPixiBackground()
    };

    function addLegend() {
        const legend = toDownload.select(".legend");

        previousWidth += 15
        let y = 50;
        const title = legend.select(".legend-title").text();
        doc.text(title, previousWidth, 10);
        [...legend.selectAll(".lgnd-entry")].forEach(el => {
            const clone = select(el);
            const circle = clone.select("circle");
            doc.addSVG(circle.node(), previousWidth, y - 1.5);

            const title = clone.select(".form-check-label > *").node();
            doc.text(title.text, previousWidth + 20, y);

            const description = clone.select(".lgnd-entry-description");
            const [conservation, descText] = description.text().trim()
                .split("                    ");
            doc.text(conservation, previousWidth + 20, y + 15);
            doc.text(descText, previousWidth + 20, y + 30, {
                width: 130,
                height: 50,
            });

            y += 80;
        });
    }

    const element = getElementToDownload();

    // Add legend
    element.appendChild(div_legend.cloneNode(true));
    // NOTE: We may want to simplify this. Maybe we prefer to have the legend
    // in a separate file, as we do for download_svg().

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
    if (view.drawer.type === "circ") {
        [...tree.querySelectorAll("path.childrenline")].forEach(el => {
            el.style["fill-opacity"] = 0
        })
        addSvg(tree)
    }


    const aligned_box = div_aligned.getBoundingClientRect();
    const aligned_x = view.drawer.type === "rect" ? aligned_box.x - menus_width : 0;
    if (view.drawer.type === "rect") {
        if (view.aligned.x <= 0)
            addSvg(tree)
        addAlignedBackground()
        const aligned = element.querySelector("#div_aligned svg");
        const aligned_header = element.querySelector("#div_aligned_header svg");
        const aligned_footer = element.querySelector("#div_aligned_footer svg");
        [ aligned, aligned_header, aligned_footer ].forEach(el => {
            if (+el.getAttribute("width") !== 0)
                addSvg(el, aligned_x)
        });

    }
    setTimeout(() => {
        // Pixi needs some time to render to img
        addPixi();
        if (view.aligned.x > 0)
            addSvg(tree)
        doc.end();
    }, 100);
}


// Apply CSS rules to the elements in the given container.
function apply_css(container) {
    const style = document.createElement("style");
    const rules = Array.from(document.styleSheets[0].rules);
    style.innerHTML = rules.map(r => r.cssText).join("\n");
    container.appendChild(style);
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
