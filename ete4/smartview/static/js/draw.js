// Functions related to updating (drawing) the view.

import { view, menus, get_tid, on_box_click, on_box_wheel, tree_command, reset_view }
    from "./gui.js";
import { create_seq_pixi, clear_pixi } from "./pixi.js";
import { update_minimap_visible_rect } from "./minimap.js";
import { colorize_searches, get_search_class } from "./search.js";
import { on_box_contextmenu } from "./contextmenu.js";
import { colorize_tags } from "./tag.js";
import { colorize_labels } from "./label.js";
import { api } from "./api.js";

export { update, draw_tree, draw, get_class_name, get_items_per_panel,
         tree2rect, tree2circ, pad };


// Update the view of all elements (gui, tree, minimap).
function update() {
    menus.pane.refresh();  // update the info box on the top-right

    draw_tree();

    if (view.minimap.show)
        update_minimap_visible_rect();
}


// Ask the server for a tree in the new defined region, and draw it.
async function draw_tree() {
    if (div_tree.offsetWidth <= 0 || view.zoom.x === Infinity) {
        const w = div_tree.offsetWidth / view.zoom.x;
        suggest_width_change("error", `Cannot draw tree with width ${w}`);
        return;
    }

    div_tree.style.cursor = "wait";  // so the user knows we are drawing

    const scale = 100 / view.zoom.x;  // the line is 100 pixels (see gui.html)
    text_scale.textContent = format_float(scale);  // show scale

    try {
        const qs = build_draw_query_string();

        // Get the drawing commands.
        const commands = await api(`/trees/${get_tid()}/draw?${qs}`);

        // Separate them per panel (xmaxs is the farthest x drawn per panel).
        const [items, xmaxs] = get_items_per_panel(commands);

        // Clear any graphics from pixi that there may be first.
        clear_pixi();

        // Make sure we have the aligned panel if (and only if) necessary.
        if (view.shape === "circular" ||
            (Object.keys(items).length === 1 && 0 in items)) {
            div_aligned.style.display = "none";  // hide aligned panel
        }
        else {
            div_aligned.style.display = "flex";  // show aligned panel
            replace_svg(div_aligned);  // so we swap the main svg (faster to draw)
        }

        // Draw all the items, in the main div_tree and in the aligned panel.
        const panels = Object.keys(items).sort((x, y) => Number(x) > Number(y));
        const panels_headers = panels.filter(x => x < 0).reverse();
        const panels_aligned = panels.filter(x => x > 0);

        if (0 in items)  // panel 0 has the items for div_tree
            draw(div_tree, items[0], view.tl, view.zoom);

        let xmax = view.shape === "circular" && 0 in xmaxs ? xmaxs[0] : 0;

        for (const panel of panels_aligned) {
            draw_aligned(items[panel].map(item => translate(item, xmax)));
            xmax += xmaxs[panel];
        }

        xmax = view.shape === "circular" && 0 in xmaxs ? xmaxs[0] : 0;  // reset

        if (view.shape === "rectangular") {  // TODO: headers in circular too
            for (const panel of panels_headers) {  // negative panels are headers
                draw_header_background(xmax);
                draw_header(items[panel].map(item => translate(item, xmax)));
                xmax += xmaxs[-panel];  // the xmax of the *positive* panel
            }
        }

        // Update variable that shows the number of visible nodes in the menu.
        view.nnodes_visible = div_tree.getElementsByClassName("nodebox").length;

        colorize_labels();
        colorize_tags();
        colorize_searches();

        if (view.shape === "circular") {
            fix_text_orientations();

            if (view.angle.min < -180 || view.angle.max > 180)
                draw_negative_xaxis();
        }
    }
    catch (ex) {
        Swal.fire({
            html: `When drawing: ${ex.message}`,
            icon: "error",
        });
    }

    div_tree.style.cursor = "auto";  // show that we finished drawing
}

// Return float x as a nice string (with approximately n precision digits).
function format_float(x, n=2) {
    if (x < Math.pow(10, -n) || x > Math.pow(10, n))
        return x.toExponential(n);
    else
        return x.toFixed(n);
}


// Notify message and allow changing tree distances to ultrametric or dendogram.
async function suggest_width_change(icon, message) {
    const result = await Swal.fire({
        icon: icon,
        html: message,
        confirmButtonText: "Convert to ultrametric (equidistant leaves)",
        showDenyButton: true,
        denyButtonText: "Convert to dendrogram (remove all distances)",
        showCancelButton: true,
    });

    if (result.isConfirmed) {
        await tree_command("to_ultrametric", []);
        reset_view();
    }
    else if (result.isDenied) {
        await tree_command("to_dendrogram", []);
        reset_view();
    }
}


// Return a query string with all that we need to use the "draw" api call.
function build_draw_query_string() {
    const [zx, zy] = [view.zoom.x, view.zoom.y];
    const [x, y] = [view.tl.x, view.tl.y];
    const [w, h] = [div_tree.offsetWidth / zx, div_tree.offsetHeight / zy];

    const layouts = JSON.stringify(Object.entries(view.layouts)
        .filter( ([name, status]) => status["active"] )
        .map( ([name, status]) => name));

    const labels = JSON.stringify([... view.labels.entries()].map( ([expression, label]) =>
        [expression, label.nodetype, label.position, label.column,
         [label.anchor.x, label.anchor.y], label.max_size]));

    const params_rect = {  // parameters we have to pass to the drawer
        "shape": view.shape,
        "node_height_min": view.node_height_min,
        "content_height_min": view.content_height_min,
        "zx": zx, "zy": zy, "x": x, "y": y, "w": w, "h": h,
        "collapsed_shape": view.collapsed.shape,
        "collapsed_ids": JSON.stringify(Object.keys(view.collapsed_ids)),
        "layouts": layouts,
        "labels": labels,
    };

    const params_circ = {  // parameters to the drawer, in circular mode
        ...params_rect,  // all the parameters in params_rect, plus:
        "rmin": view.rmin, "amin": view.angle.min, "amax": view.angle.max,
    };

    const params = view.shape === "rectangular" ? params_rect : params_circ;

    return new URLSearchParams(params).toString();  // "x=...&y=..."
}


// Return two objects whose keys are panel numbers (0, 1, ...) and their
// values are a list of graphics to draw on them, and their maximum x value.
function get_items_per_panel(commands) {
    const items = {};
    let xmaxs = {};

    let current_panel = 0;
    commands.forEach(c => {
        if (c[0] === "panel") {  // we got a "change panel" command
            current_panel = c[1];
        }
        else if (c[0] === "xmaxs") {  // we got a "set xmaxs" command
            xmaxs = c[1];
        }
        else {  // we got a normal drawing command
            if (!(current_panel in items))
                items[current_panel] = [];
            items[current_panel].push(c);
        }
    });

    return [items, xmaxs];
}


// Draw items in the aligned position.
function draw_aligned(items, padding_x=15) {
    if (view.shape === "rectangular") {
        const zoom = {x: view.zoom.x * view.aligned.zoom,
                      y: view.zoom.y};
        const tl = {x: view.aligned.origin - padding_x / zoom.x,
                    y: view.tl.y};  // relative "top-left" point
        const replace = false;
        draw(div_aligned, items, tl, zoom, replace);
    }
    else if (view.shape === "circular") {
        const replace = false;
        draw(div_tree, items, view.tl, view.zoom, replace);
    }
}


// Draw a white box and a line to clean the space where the headers will go.
function draw_header_background(xmax, padding_x=15) {
    const zoom = {x: view.zoom.x * view.aligned.zoom,
                  y: view.zoom.y};
    // Position where to put the header (in screen coordinates).
    const px = zoom.x * (xmax - view.aligned.origin) + padding_x,
          py = Math.max(40, - view.zoom.y * view.tl.y - 20);

    const g = create_svg_element("g");

    // Put a white rectangle on the background of the header.
    g.appendChild(create_svg_element("rect", {
        "x": px - 10,
        "y": 0,
        "width": div_aligned.offsetWidth - px + 2 * 10,
        "height": py + 20,
        "fill": "white",
    }));

    // Add a line separating the header from the content below.
    const line = create_svg_element("line", {
        "x1": px,
        "y1": py + 15,
        "x2": div_aligned.offsetWidth,
        "y2": py + 15,
    });
    add_style(line, {
        stroke: "#e0e0e0",
        strokeWidth: "3px",
    });

    g.appendChild(line);

    const svg = div_aligned.getElementsByTagName("svg")[0];
    svg.appendChild(g);
}


// Draw items in the header position.
function draw_header(items, padding_x=15) {
    if (view.shape === "rectangular") {
        const zoom = {x: view.zoom.x * view.aligned.zoom,
                      y: view.zoom.y};
        const tl = {x: view.aligned.origin - padding_x / zoom.x,
                    y: Math.min(-50 / zoom.y, view.tl.y + 10 / zoom.y)};

        const replace = false;
        draw(div_aligned, items, tl, zoom, replace);
    }
    else if (view.shape === "circular") {
        const replace = false;
        draw(div_tree, items, view.tl, view.zoom, replace);
    }
}


// Translate the position of the given item.
function translate(item, shift) {
    if (item[0] === "text") {
        const [ , box,  anchor, text, fs_max, rotation, style] = item;
        return ["text", tbox(box, shift), anchor, text, fs_max, rotation, style];
    }
    else if (item[0] == "textarray") {
        const [ , box,  anchor, text, fs_max, rotation, style] = item;
        return ["textarray", tbox(box, shift), anchor, text, fs_max, rotation, style];
    }
    else if (item[0] === "circle") {
        const [ , [x, y], radius, style] = item;
        return ["circle", [x + shift, y], radius, style];
    }
    else if (item[0] === "polygon") {
        const [ , [x, y], radius, shape, style] = item;
        return ["polygon", [x + shift, y], radius, shape, style];
    }
    else if (item[0] === "box") {
        const [ , box, style] = item;
        return ["box", tbox(box, shift), style];
    }
    else if (item[0] === "rect") {
        const [ , box, style] = item;
        return ["rect", tbox(box, shift), style];
    }
    else if (item[0] === "image") {
        const [ , box, href, style] = item;
        return ["image", tbox(box, shift), href, style];
    }
    else if (item[0] === "seq") {
        const [ , box, seq, seqtype, draw_text, fs_max, style, render] = item;
        return ["seq", tbox(box, shift), seq, seqtype, draw_text, fs_max,
                style, render];
    }
    else if (item[0] === "heatmap") {
        const [ , box, values, value_range, color_range] = item;
        return ["heatmap", tbox(box, shift), values, value_range, color_range];
    }
    else if (item[0] === "header") {
        const [ , x, text, fs_max, rotation, style] = item;
        return ["header", x + shift, text, fs_max, rotation, style];
    }
    else {
        // We are not translating anything else for the moment, including
        // nodeboxes or nodedots.
        return item;
    }
}

// Translate box by the given shift amount in x.
function tbox(box, shift) {
    if (shift === undefined)
        throw new Error("missing shift argument");  // it happened
    const [x, y, w, h] = box;
    return [x + shift, y, w, h];
}


// Add a line to the svg in div_tree marking the -x axis.
// Useful when we represent circular trees with angles < -180 or > 180.
function draw_negative_xaxis() {
    // x position where the line should end (a bit left of the tree size)
    const x = -view.rmin - view.tree_size.width * 1.2;

    const style = {
        stroke: "#A008",
        strokeWidth: "10px",
        strokeLinecap: "round",
    };
    const line1 = ["line", [0, 0], [x, 0], style];  // round fuzzy line
    const line2 = ["line", [0, 0], [x, 0], ""];  // thin black line

    const replace = false;
    draw(div_tree, [line1, line2], view.tl, view.zoom, replace);
}


// Add graphics to the given element, with all the items in the list drawn.
// The svg inside the element will be either used or replaced.
function draw(element, items, tl, zoom, replace=true) {
    // The pixi app that we need to draw on element.
    const app = element === div_tree    ? view.pixi_app_tree :
                element === div_aligned ? view.pixi_app_aligned : null;

    const wmax = element.offsetWidth;

    // The global svg element where all the created svgs will be.
    const g = create_svg_element("g");

    // The legend(s) that there may be.
    const legends = [];

    // Add graphics from items.
    items.forEach(item_as_list => {
        if (item_as_list[0] === "legend") {  // we deal with these separately
            legends.push(item_as_list.slice(1));
            return;
        }

        const item = create_item(item_as_list, tl, zoom, wmax);
        if (item === null) {  // we decided not to draw the element
            ;  // do nothing
        }
        else if (item.worldTransform !== undefined) {  // pixi
            app.stage.addChild(item);  // add item to pixi stage
        }
        else {  // svg
            g.appendChild(item);  // add item to global svg element
        }
    });

    // Add legends.
    if (element === div_tree)  // legends should just appear in the main div
        add_legends(legends);

    // Extra operations that we need for the svgs.

    put_nodes_in_background(g);  // so they don't cover other graphics

    if (replace)
        replace_svg(element);  // so we swap the main svg (faster to draw)

    const svg = element.getElementsByTagName("svg")[0];
    svg.appendChild(g);  // add our global g element to the svg
}


function add_legends(legends) {
    if (legends.length === 0 || !view.show_legend) {  // nothing to show?
        div_legend.style.visibility = "hidden";  // hide
        return;
    }

    const hr = '<hr style="margin: 10px; background-color: gray">';

    const legend = ('<div style="padding: 10px; font-size: 0.8rem">' +
                    legends.map(legend2html).join(hr) +  // where the action is
                    '</div>');

    if (legend !== div_legend.innerHTML) {  // update only if needed
        div_legend.innerHTML = legend;
        div_legend.style.visibility = "visible";  // show in case it was hidden
    }
}

function legend2html(legend) {
    const [title, variable, colormap, vrange, crange] = legend;

    const header = `<div style="text-align: center;
        font-weight: bold; font-family: sans">${title}</div>`;

    if (variable === "discrete") {  // use color map
        const lines = Object.entries(colormap).map(([name, color]) =>
            `<span style="color: ${color}">●</span> ${name}<br>`);
        return header + lines.join("\n");
    }
    else {  // variable continuous: use value range and color range
        const [vmin, vmax] = vrange.map(format_number);  // values
        return header +
            `${vmax}
             <span style="display: block;
                 min-width: 20px; max-width: 50px; min-height: 100px;
                 background-image:linear-gradient(${crange.join(",")})">
             </span>
             ${vmin}`;
    }
}

// Return number (int or float) looking relatively good for the legend.
function format_number(x) {
    const s = x.toString();
    return s.length < 5 ? s : x.toPrecision(3);
}


// Make a copy of the nodeboxes and put them before all the other elements,
// so if they stop being transparent (because they are tagged, or the result
// of a search, or the user changes the node opacity), they do not cover the
// rest of the tree elements.
// The original elements stay transparent in the foreground so the user can
// interact with them (highlighting, opening their contextmenu, etc.).
function put_nodes_in_background(g) {
    const first = g.children[0];  // first svg element, for reference
    Array.from(g.getElementsByClassName("nodebox")).forEach(e => {
        const bg_node = e.cloneNode();
        e.id = "foreground-" + bg_node.id;  // avoid id collisions
        e.removeAttribute("style");  // in case it is set
        e.classList = ["fg_node"];  // avoid being wrongly selected as a node
        g.insertBefore(bg_node, first);
    });
}


// Replace the svg that is a child of the given element (or just add if none).
function replace_svg(element) {
    const svg = create_svg_element("svg", {
        "width": element.offsetWidth,
        "height": element.offsetHeight,
    });

    const existing_svg = element.getElementsByTagName("svg")[0];

    if (existing_svg)
        existing_svg.replaceWith(svg);
    else
        element.appendChild(svg);
}


// Return the graphical (svg or pixi) element corresponding to a graphical item.
function create_item(item, tl, zoom, wmax) {
    // item looks like ["line", ...] for a line, etc.

    const [zx, zy] = [zoom.x, zoom.y];  // shortcut

    if (item[0] === "nodebox") {
        const [ , box, name, props, node_id, result_of, style] = item;

        const styles = ["nodebox", add_ns_prefix(style)];
        const b = create_box(box, tl, zx, zy, styles);

        b.id = "node-" + node_id.join("_");  // used in tags

        result_of.forEach(t => b.classList.add(get_search_class(t, "results")));

        b.addEventListener("mousedown", event =>
            b.dataset.mousepos = `${event.pageX} ${event.pageY}`);
        b.addEventListener("mouseup", event =>
            on_box_click(event, box, node_id));
        // NOTE: Instead of a "click", we store the position at mousedown (to
        // later check if it moved), and trigger the click on the mouseup.

        b.addEventListener("contextmenu", event =>
            on_box_contextmenu(event, box, name, props, node_id));
        b.addEventListener("wheel", event =>
            on_box_wheel(event, box), {passive: false});

        // Save information in the box as a data attribute string (.dataset).
        // This will be used for the "tooltip" in on_box_click().
        if (name || Object.entries(props).length > 0)
            b.dataset.info = (name ? `<i>${name}</i> ` : "") + "<br>" +
                Object.entries(props).map(([k, v]) => `<b>${k}:</b> ${v}`).join("<br>");

        return b;
    }
    else if (item[0] === "nodedot") {
        const [ , point, dy_max, style] = item;

        const styles = ["nodedot", add_ns_prefix(style)];
        return create_dot(point, dy_max, tl, zx, zy, styles);
    }
    else if (item[0] === "hz-line") {
        const [ , p1, p2, parent_of, style] = item;

        const styles = ["hz_line",
            parent_of.map(text => get_search_class(text, "parents")),
            add_ns_prefix(style)];
        return create_line(p1, p2, tl, zx, zy, styles);
    }
    else if (item[0] === "vt-line") {
        const [ , p1, p2, style] = item;

        const styles = ["vt_line", add_ns_prefix(style)];
        return view.shape === "rectangular" ?
            create_line(p1, p2, tl, zx, zy, styles) :
            create_arc(p1, p2, tl, zx, styles);
    }
    else if (item[0] === "skeleton") {
        const [ , points] = item;

        return create_skeleton(points, tl, zx, zy);
    }
    else if (item[0] === "outline") {
        const [ , box] = item;

        return create_outline(box, tl, zx, zy);
    }
    else if (item[0] === "line") {
        const [ , p1, p2, style] = item;

        return create_line(p1, p2, tl, zx, zy, add_ns_prefix(style));
    }
    else if (item[0] === "arc") {
        const [ , p1, p2, style] = item;

        return create_arc(p1, p2, tl, zx, add_ns_prefix(style));
    }
    else if (item[0] === "circle") {
        const [ , center, radius, style] = item;

        return create_circle(center, radius, tl, zx, zy, add_ns_prefix(style));
    }
    else if (item[0] === "polygon") {
        const [ , center, radius, shape, style] = item;

        return create_polygon(center, radius, shape, tl, zx, zy,
                              add_ns_prefix(style), true);
    }
    else if (item[0] === "box") {
        const [ , box, style] = item;

        return create_box(box, tl, zx, zy, add_ns_prefix(style));
    }
    else if (item[0] === "rect") {
        const [ , box, style] = item;

        return create_rect(box, tl, zx, zy, add_ns_prefix(style));
    }
    else if (item[0] === "text") {
        const [ , box, anchor, text, fs_max, rotation, style] = item;

        return create_text(box, anchor, text, fs_max, rotation, tl, zx, zy,
                           add_ns_prefix(style));
    }
    else if (item[0] === "textarray") {
        const [ , box, anchor, texts, fs_max, rotation, style] = item;

        const [x0, y0, dx0, dy0] = box;
        const dx = dx0 / texts.length;

        const imin = Math.max(0, Math.floor((tl.x - x0) / dx));
        const imax = view.shape === "rectangular" ?
              Math.min(texts.length, (wmax / zx + tl.x - x0) / dx) :
              texts.length;

        const [y, dy] = pad(y0, dy0, view.array.padding);

        const container = create_svg_element("g");
        for (let i = imin, x = x0 + imin * dx; i < imax; i++, x+=dx) {
            const text = create_text([x, y, dx, dy], anchor, texts[i], fs_max,
                                     rotation, tl, zx, zy, add_ns_prefix(style));
            container.appendChild(text);
        }

        return container;
    }
    else if (item[0] === "image") {
        const [ , box, href, style] = item;

        return create_image(box, href, tl, zx, zy, add_ns_prefix(style));
    }
    else if (item[0] === "heatmap") {
        const [ , box, values, value_range, color_range] = item;
        const [x0, y0, dx0, dy0] = box;
        const dx = dx0 / values.length;

        const [vmin, vmax] = value_range;
        const [[rmin, gmin, bmin, amin],
               [rmax, gmax, bmax, amax]] = color_range;

        const imin = Math.max(0, Math.floor((tl.x - x0) / dx));
        const imax = view.shape === "rectangular" ?
              Math.min(values.length, (wmax / zx + tl.x - x0) / dx) :
              values.length;

        const [y, dy] = pad(y0, dy0, view.array.padding);

        const container = create_svg_element("g");
        for (let i = imin, x = x0 + imin * dx; i < imax; i++, x+=dx) {
            const f = (values[i] - vmin) / (vmax - vmin);  // 0 <= f <= 1

            const r = Math.round(rmin + f * (rmax - rmin));  // min <= c <= max
            const g = Math.round(gmin + f * (gmax - gmin));
            const b = Math.round(bmin + f * (bmax - bmin));
            const a = Math.round(amin + f * (amax - amin));

            const tile = view.shape === "rectangular" ?
                create_rect([x, y, dx, dy], tl, zx, zy) :
                create_asec([x, y, dx, dy], tl, zx);

            tile.style.fill = `rgba(${r},${g},${b},${a})`;

            container.appendChild(tile);
        }

        return container;
    }
    else if (item[0] === "seq") {
        const [ , box, seq, seqtype, draw_text, fs_max, style, render] = item;

        return create_seq(box, seq, seqtype, draw_text, fs_max, tl, zx, zy,
                          add_ns_prefix(style), render, wmax);
    }
    else {
        console.log(`Unrecognized item: ${item}`);
    }
}


// Return a valid class name from a description of a type of element.
function get_class_name(type) {
    return type.replace(/[^A-Za-z0-9_-]/g, '');
}


// Transform the interval [y0, y0+dy0] into one padded with the given fraction.
function pad(y0, dy0, fraction) {
    const dy = dy0 * (1 - fraction);
    return [y0 + (dy0 - dy)/2, dy]
}


function create_svg_element(name, attrs={}) {
    const element = document.createElementNS("http://www.w3.org/2000/svg", name);
    for (const [attr, value] of Object.entries(attrs))
        element.setAttributeNS(null, attr, value);
    return element;
}


// Return a box (rectangle or annular sector).
function create_box(box, tl, zx, zy, style="") {
    const b = view.shape === "rectangular" ?
                    create_rect(box, tl, zx, zy, style) :
                    create_asec(box, tl, zx, style);
    return b;
}


function create_rect(box, tl, zx, zy, style="") {
    let element;

    if (view.shape === "rectangular") {
        const [x, y, w, h] = box;
        const p = tree2rect([x, y], tl, zx, zy);

        element = create_svg_element("rect", {
            "x": p.x, "y": p.y,
            "width": zx * w, "height": zy * h,
        });
    }
    else {  // circular
        const [r, a, dr, da] = box;
        const z = zy;
        const p00 = tree2circ([r, a], tl, z),
              p01 = tree2circ([r, a + da], tl, z),
              p10 = tree2circ([r + dr, a + da/2 * dr / (r + dr)], tl, z),
              p11 = tree2circ([r + dr, a + da - da/2 * dr / (r + dr)], tl, z);

        element = create_svg_element("path", {
            "d": `M ${p00.x} ${p00.y}
                  L ${p10.x} ${p10.y}
                  L ${p11.x} ${p11.y}
                  L ${p01.x} ${p01.y}
                  L ${p00.x} ${p00.y}`,
        });
    }

    add_style(element, style);

    return element;
}


// Return a svg annular sector, described by box and with zoom z.
function create_asec(box, tl, z, style="") {
    const [r, a, dr, da] = box;
    const large = da > Math.PI ? 1 : 0;
    const p00 = tree2circ([r, a], tl, z),
          p01 = tree2circ([r, a + da], tl, z),
          p10 = tree2circ([r + dr, a], tl, z),
          p11 = tree2circ([r + dr, a + da], tl, z);

    const element = create_svg_element("path", {
        "d": `M ${p00.x} ${p00.y}
              L ${p10.x} ${p10.y}
              A ${z * (r + dr)} ${z * (r + dr)} 0 ${large} 1 ${p11.x} ${p11.y}
              L ${p01.x} ${p01.y}
              A ${z * r} ${z * r} 0 ${large} 0 ${p00.x} ${p00.y}`,
    });

    add_style(element, style);

    return element;
}


function create_image(box, href, tl, zx, zy, style="") {
    let element;

    if (view.shape === "rectangular") {
        const [x, y, w, h] = box;
        const p = tree2rect([x, y], tl, zx, zy);

        element = create_svg_element("image", {
            "href": href,
            "x": p.x, "y": p.y,
            "width": zx * w, "height": zy * h,
        });
    }
    else {  // circular
        const [r, a, dr, da] = box;
        const z = zy;  // which is equal to zx too

        const p = tree2circ([r, a], tl, z);

        element = create_svg_element("image", {
            "href": href,
            "x": p.x, "y": p.y,
            "width": z * dr, "height": zy * r * da,
        });

        const angle = (a + da/2) * 180 / Math.PI;
        add_rotation(element, angle, p.x, p.y);
    }

    add_style(element, style);

    return element;
}


// Return a nodedot.
function create_dot(point, dy_max, tl, zx, zy, styles) {
    const shape = pop_style(styles, "shape") || view.node.dot.shape;
    if (shape === "none")
        return null;

    // Radius of the dot in pixels.
    const r_max = zy * dy_max * (view.shape === "circular" ? point[0] : 1);
    const r = Math.min(r_max, pop_style(styles, "radius") || view.node.dot.radius);

    if (shape === "circle")
        return create_circle(point, r, tl, zx, zy, styles);
    else
        return create_polygon(point, r, shape, tl, zx, zy, styles);
}


// Return a shape summarizing collapsed nodes (skeleton).
function create_skeleton(points, tl, zx, zy) {
    if (view.shape === "rectangular")
        return create_rect_skeleton(points, tl, zx, zy);
    else
        return create_circ_skeleton(points, tl, zx);
}


// Return a svg horizontal approximation to the collapsed nodes.
function create_rect_skeleton(points, tl, zx, zy) {
    const ps = points.map(p => tree2rect(p, tl, zx, zy));

    return create_svg_element("path", {
        "class": "collapsed",
        "d": (`M ${ps[0].x} ${ps[0].y} ` +
              ps.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')),
    });
}


// Return a svg collapsed representation in the direction of an annular sector.
function create_circ_skeleton(points, tl, z) {
    const das = [];  // list of angle differences
    for (let i = 1; i < points.length; i++)
        das.push(points[i][1] - points[i-1][1]);

    const ps = points.map(p => tree2circ(p, tl, z));

    const arc = (p, i) => {
        if (das[i] === 0)  // if previous point was at the same angle
            return `L ${p.x} ${p.y}`;  // draw just a line

        const large = Math.abs(das[i]) > Math.PI ? 1 : 0;
        const sweep = das[i] > 0 ? 1 : 0;
        const r = z * points[i+1][0];
        return `A ${r} ${r} 0 ${large} ${sweep} ${p.x} ${p.y}`;
    }

    return create_svg_element("path", {
        "class": "collapsed",
        "d": (`M ${ps[0].x} ${ps[0].y} ` +
              ps.slice(1).map(arc).join(' ')),
    });
}


// Return an outline (collapsed version of a box).
function create_outline(box, tl, zx, zy) {
    if (view.shape === "rectangular")
        return create_rect_outline(box, tl, zx, zy);
    else
        return create_circ_outline(box, tl, zx);
}


// Return a svg horizontal outline.
function create_rect_outline(box, tl, zx, zy) {
    const [x, y, dx, dy] = box;

    const p0 = tree2rect([x, y + dy/2], tl, zx, zy),
          p10 = tree2rect([x + dx, y], tl, zx, zy),
          p11 = tree2rect([x + dx, y + dy], tl, zx, zy);

    return create_svg_element("path", {
        "class": "collapsed",
        "d": `M ${p0.x} ${p0.y}
              L ${p10.x} ${p10.y}
              L ${p11.x} ${p11.y}
              L ${p0.x} ${p0.y}`,
    });
    // NOTE: Symmetrical to create_circ_outline(). Otherwise, we could just do:
    //   create_svg_element("polygon", {
    //       "points": [p0, p10, p11].map(p => `${p.x},${p.y}`).join(" "),
    //   });
}


// Return a svg outline in the direction of an annular sector.
function create_circ_outline(box, tl, z) {
    const [r, a, dr, da] = box;

    const large = da > Math.PI ? 1 : 0;
    const p0 = tree2circ([r, a + da/2], tl, z),
          p10 = tree2circ([r + dr, a], tl, z),
          p11 = tree2circ([r + dr, a + da], tl, z);

    return create_svg_element("path", {
        "class": "collapsed",
        "d": `M ${p0.x} ${p0.y}
              L ${p10.x} ${p10.y}
              A ${z * (r + dr)} ${z * (r + dr)} 0 ${large} 1 ${p11.x} ${p11.y}
              L ${p0.x} ${p0.y}`,
    });
}


function create_line(p1, p2, tl, zx, zy, style="") {
    // Transform points to screen coordinates.
    const [pt1, pt2] = view.shape === "rectangular" ?
        [tree2rect(p1, tl, zx, zy), tree2rect(p2, tl, zx, zy)] :
        [tree2circ(p1, tl, zx),     tree2circ(p2, tl, zx)];

    const element = create_svg_element("line", {
        "class": "line",
        "x1": pt1.x, "y1": pt1.y,
        "x2": pt2.x, "y2": pt2.y,
    });

    add_style(element, style);

    return element;
}


function create_arc(p1, p2, tl, z, style="") {
    // NOTE: We use this only for  view.shape === "circular"  for the moment.
    const n1 = tree2circ(p1, tl, z),
          n2 = tree2circ(p2, tl, z);
    const r = z * p1[0];
    const large = p2[1] - p1[1] > Math.PI ? 1 : 0;

    const element = create_svg_element("path", {
        "class": "line",
        "d": `M ${n1.x} ${n1.y} A ${r} ${r} 0 ${large} 1 ${n2.x} ${n2.y}`,
    });

    add_style(element, style);

    return element;
}


function create_circle(center, radius, tl, zx, zy, style="") {
    const c = view.shape === "rectangular" ?
        tree2rect(center, tl, zx, zy) :
        tree2circ(center, tl, zx);

    const element = create_svg_element("circle", {
        "class": "circle",
        "cx": c.x,
        "cy": c.y,
        "r": radius,
    });

    add_style(element, style);

    return element;
}


// Create a polygon.
function create_polygon(center, r, shape, tl, zx, zy, style="", resize=false) {
    const n = typeof shape === "number" ? shape :
          {"triangle": 3,
           "square":   4,
           "pentagon": 5,
           "hexagon":  6,
           "heptagon": 7,
           "octogon":  8}[shape];

    if (n === undefined)
        throw new Error(`unknown dot shape ${shape}`);

    const c = view.shape === "rectangular" ?  // center point in screen coords
        tree2rect(center, tl, zx, zy) :
        tree2circ(center, tl, zx);

    // When we put a polygon as a nodedot we don't need the correction,
    // but when used as a face it would look bad without it.
    const correction = resize ? Math.atan(n - 2) * 2 / Math.PI : 1;

    const s = 2 * r * Math.tan(Math.PI / n) * correction; // side length
    let p = {x: c.x - s/2,  // starting point
             y: c.y + r};

    const ps = [p];  // polygon points, adding a rotated (s, 0)
    for (let i = 0; i < n - 1; i++) {
        p = {x: p.x + s * Math.cos(i * 2 * Math.PI / n),
             y: p.y - s * Math.sin(i * 2 * Math.PI / n)}
        ps.push(p);
    }

    const element = create_svg_element("polygon", {
        "points": ps.map(p => `${p.x},${p.y}`).join(" "),
    });

    if (view.shape === "circular") {
        const angle = 180 / Math.PI * Math.atan2(zy * tl.y + c.y,
                                                 zx * tl.x + c.x);
        add_rotation(element, angle, c.x, c.y);
    }

    add_style(element, style);

    return element;
}


function create_text(box, anchor, text, fs_max, rotation,
                     tl, zx, zy, style="") {
    const [x, y, fs, text_anchor] = view.shape === "rectangular" ?
        get_text_placement_rect(box, anchor, text, fs_max, rotation, tl, zx, zy, style) :
        get_text_placement_circ(box, anchor, text, fs_max, rotation, tl, zx, style);

    const dx = (style === "name") ? view.name.padding.left * fs / 100 : 0;

    const t = create_svg_element("text", {
        "class": "text",
        "x": x + dx,
        "y": y,
        "font-size": `${fs}px`,
        "text-anchor": text_anchor,
    });

    t.appendChild(document.createTextNode(text));

    if (rotation != 0)
        add_rotation(t, rotation, x, y);

    if (view.shape === "circular") {
        const angle = Math.atan2(zy * tl.y + y, zx * tl.x + x) * 180 / Math.PI;
        add_rotation(t, angle, x, y);
    }

    add_style(t, style);

    return t;
}


function create_seq(box, seq, seqtype, draw_text, fs_max,
                    tl, zx, zy, style, render, wmax) {
    if (!["aa", "nt"].includes(seqtype))
        throw new Error(`unknown sequence type ${seqtype}`);

    if (view.render === "force raster" ||
        view.render === "auto" && (render === "raster" || render === "auto"))
        return create_seq_pixi(box, seq, seqtype, draw_text, fs_max,
                               tl, zx, zy, style, wmax);
    else if (view.render === "force svg" || render === "svg")
        return create_seq_svg(box, seq, seqtype, draw_text, fs_max,
                              tl, zx, zy, style, wmax);
    else
        throw new Error(`unknown render type ${render}`);
}


// With svg.
// NOTE: Much of this code is similar to the one in pixi.js. Maybe merge?
function create_seq_svg(box, seq, seqtype, draw_text, fs_max,
                        tl, zx, zy, style, wmax) {
    const colors = seqtype === "aa" ? aa_colors : nt_colors;

    const [x0, y0, dx0, dy0] = box;
    const dx = dx0 / seq.length;

    const imin = Math.max(0, Math.floor((tl.x - x0) / dx));
    const imax = view.shape === "rectangular" ?
          Math.min(seq.length, (wmax / zx + tl.x - x0) / dx) :
          seq.length;

    const [y, dy] = pad(y0, dy0, view.array.padding);

    const g = create_svg_element("g");
    for (let i = imin, x = x0 + imin * dx; i < imax; i++, x+=dx) {
        const r = view.shape === "rectangular" ?
            create_rect([x, y, dx, dy], tl, zx, zy) :
            create_asec([x, y, dx, dy], tl, zx);

        r.style.fill = colors[seq[i]];

        g.appendChild(r);

        if (draw_text)  // draw a letter too
            if (dx * zx > 5)  // but only if there's space
                g.appendChild(create_text([x, y, dx, dy], [0.5, 0.5],
                                          seq[i], fs_max, 0, tl, zx, zy));
    }

    return g;
}

// Colors taken so they are the same as the ones used in the pixi images.
const aa_colors = {  // amino acids
    "-": "white",
    A: "#c8c8c8",
    B: "#ff69b4",
    C: "#e6e600",
    D: "#e60a0a",
    E: "#e60a0a",
    F: "#3232aa",
    G: "#ebebeb",
    H: "#8282d2",
    I: "#0f820f",
    K: "#145aff",
    L: "#0f820f",
    M: "#e6e600",
    N: "#00dcdc",
    P: "#dc9682",
    Q: "#00dcdc",
    R: "#145aff",
    S: "#fa9600",
    T: "#fa9600",
    V: "#0f820f",
    W: "#b45ab4",
    X: "#bea06e",
    Y: "#3232aa",
    Z: "#ff69b4",
}

const nt_colors = {  // nucleotides
    "-": "white",
    A: "#a0a0ff",
    C: "#ff8c4b",
    G: "#ff7070",
    T: "#a0ffa0",
    U: "#ff8080",
    I: "#80ffff",
}

// Alternatively:
//   const code = (seq.charCodeAt(i) - 65) * 9;  // 'A' -> 65, and 26 letters vs 256 hs
//   const fill = seq[i] === "-" ? "white" : `hsl(${code}, 100%, 50%)`;
// TODO: see if we want instead colors following some "standards" like:
// https://acces.ens-lyon.fr/biotic/rastop/help/colour.htm
// https://www.dnastar.com/manuals/MegAlignPro/17.2/en/topic/change-the-analysis-view-color-scheme
// http://yulab-smu.top/ggmsa/articles/guides/Color_schemes_And_Font_Families.html


// "From tree coordinates to screen coordinates (for rectangular mode)".
// Return the {x, y} corresponding to the given point coordinates in the tree.
// The point is translated (from the top-left point tl) and scaled (by zx, zy).
function tree2rect(point, tl, zx, zy) {
    const [x, y] = point;

    return {
        x: zx * (x - tl.x),
        y: zy * (y - tl.y),
    };
}


// "From tree coordinates to screen coordinates (for circular mode)".
// Return the {x, y} corresponding to the given point coordinates in the tree.
// The point is rotated, translated, and scaled.
function tree2circ(point, tl, z) {
    const [r, a] = point;  // point specified as [radius, angle]
    const p = [r * Math.cos(a), r * Math.sin(a)];  // point as [x, y]
    return tree2rect(p, tl, z, z);
}


// Add "ns_" prefix to the style. A "style" can be a string with class name(s),
// an object with the individual properties to set, or a list of styles.
// This is useful when referring to classes in the css that come from the
// tree style (in its aliases).
function add_ns_prefix(style) {
    if (typeof style === "string") {  // string with class name(s).
        const styles = [];

        for (const name of style.split(" ").filter(x => x)) { // nonempty names
            // We define the "ns_" styles in the css (in
            // gui.js:set_tree_style()), and the "label_" styles with the gui.
            const prefix = name.startsWith("label_") ? "" : "ns_";
            // draw.py sends labels styles with the "label_" prefix, and
            // label.js:colorize_label() expects their class start as "label_".
            // This may not be the clearest way to prefix things...

            styles.push(prefix + name);
        }

        return styles.join(" ");
    }
    else if (style.length === undefined) {  // object with individual properties
        return style;
    }
    else {  // list of styles to combine
        return style.map(s => add_prefix(s));
    }
}


// Add to the given element a style. It can be a string with class name(s),
// an object with the individual properties to set, or a list of styles.
function add_style(element, style, exclude=["shape", "radius"]) {
    if (typeof style === "string") {  // string with class name(s).
        for (const name of style.split(" ").filter(x => x)) {  // nonempty names
            element.classList.add(name);
        }
    }
    else if (style.length === undefined) {  // object with individual properties
        for (const [prop, value] of Object.entries(style)) {
            if (!exclude.includes(prop))
                element.style[prop] = value;
        }
    }
    else {  // list of styles to combine
        style.forEach(s => add_style(element, s, exclude));
    }
}


// Return the value in style associated with the given property prop,
// and remove it from the style,
function pop_style(style, prop) {
    if (typeof style === "string") {  // string with class name(s).
        return undefined;
    }
    else if (style.length === undefined) {  // object with individual properties
        const value = style[prop];
        delete style[prop];  // remove it from the style if it is there
        return value;  // possibly undefined
    }
    else {  // list of styles to combine
        for (let s of style) {
            const value = pop_style(s, prop);
            if (value !== undefined)
                return value;
        }
        return undefined;
    }
}


// Return position, font size and text anchor to draw text when box is a rect.
function get_text_placement_rect(box, anchor, text, fs_max, rotation,
                                 tl, zx, zy, type="") {
    if (text.length === 0)
        throw new Error("please do not try to place empty texts :)")
        // We could, but it's almost surely a bug upstream!

    const [x, y, dx, dy] = box;

    const a = rotation * Math.PI / 180;
    const [c, s] = [Math.abs(Math.cos(a)), Math.abs(Math.sin(a))];

    const w_h = text.length / 1.5;  // text width over its height
    const fs_box = dx * zx / (s + w_h * c);  // font size so it fits in box
    const fs = font_adjust(Math.min(fs_box, fs_max), type);

    const scale = fs / (zy * dy);
    const [ax, ay] = anchor;
    const x_in_tree = x + ax * (1 - scale) * dx,
          y_in_tree = y + ay * (1 - scale) * dy + 0.9 * fs / zy;
    // We give the position as the bottom-left point, the same convention as in
    // svgs. We go a bit up (0.9 instead of 1.0) because of the baseline.

    const dx_in_tree = scale * dx;
    const [x_anchor, text_anchor] =
          anchored_position(x_in_tree, c * dx_in_tree, s * fs / zx, ax);

    const corner = tree2rect([x_anchor, y_in_tree], tl, zx, zy);

    return [corner.x, corner.y, fs, text_anchor];
}


// Return position, font size and text anchor to draw text when box is an asec.
function get_text_placement_circ(box, anchor, text, fs_max, rotation, tl, z, type="") {
    if (text.length === 0)
        throw new Error("please do not try to place empty texts :)");
        // We could, but it's almost surely a bug upstream!

    const [r, a, dr, da] = box;
    if (r === 0)
        throw new Error("r cannot be 0 (text would have 0 font size)");

    // Find the font size, according to fs_max. "width" (dr), and "heigth" (da).
    const dr_char = dr / text.length;  // ~ dr of 1 char (in tree units)
    fs_max = Math.min(fs_max, z * dr_char * 1.6, z * r * da);
    const fs = font_adjust(fs_max, type);

    // Find the coordinates where it would go in the tree.
    const scale = fs / (z * r * da);
    const [ar, aa] = anchor;
    const r_in_tree = r + ar * (1 - scale) * dr,
          a_in_tree = a + aa * (1 - scale) * da + 0.8 * (fs / r) / z;
    // We give the position as the bottom-left point, the same convention as in
    // svgs. We go a bit up (0.8 instead of 1.0) because of the baseline.

    // Convert to in-screen values and return those.
    const dr_in_tree = scale * dr;
    const [r_anchor, text_anchor] = anchored_position(r_in_tree, dr_in_tree, 0, ar);

    const corner = tree2circ([r_anchor, a_in_tree], tl, z);

    return [corner.x, corner.y, fs, text_anchor];
}


// Return the x position and the svg text-anchor to place the text for a given
// original in-tree x text position, dx width, dx_rot extra width coming from
// a rotation, and ax anchor. This is useful to fine-tune the placement (since
// dx is just an approximation to the exact width of the text).
function anchored_position(x, dx, dx_rot, ax) {
    if (ax < 0.3)
        return [x + dx_rot, "start"];
    else if (ax < 0.6)
        return [x + dx/2, "middle"];
    else
        return [x + dx - dx_rot, "end"];
}


// Flip all the texts in circular representation that look upside-down.
// NOTE: getBBox() is very expensive and requires text to be already in the DOM.
function fix_text_orientations() {
    const texts = Array.from(div_tree.getElementsByClassName("text"))
        .filter(is_upside_down);

    texts.sort((a, b) => get_font_size(b) - get_font_size(a));

    texts.slice(0, 500).forEach(t => flip_with_bbox(t, t.getBBox()));
    texts.slice(500).forEach(t => flip_with_bbox(t, get_approx_BBox(t)));
}

function is_upside_down(text) {
    const angle = text.transform.baseVal[0].angle;
    return angle < -90 || angle > 90;
}

function get_font_size(text) {
    return Number(text.getAttribute('font-size').slice(0, -2));  // "px"
}


// Apply svg transformation to flip the given text (bounded by bbox).
function flip_with_bbox(text, bbox) {
    add_rotation(text, 180, bbox.x + bbox.width/2, bbox.y + bbox.height/2);
}


// Add rotation to element, with angle in degrees and centered around (cx, cy).
function add_rotation(element, angle, cx=0, cy=0) {
    const svg = div_tree.children[0];
    const tr = svg.createSVGTransform();
    tr.setRotate(angle, cx, cy);
    element.transform.baseVal.appendItem(tr);
}


// Return an approximate bounding box for the given svg text.
function get_approx_BBox(text) {
    const height = get_font_size(text);
    const x = Number(text.getAttribute("x"));
    const y = Number(text.getAttribute("y")) - height;
    const width = text.childNodes[0].length * height / 1.5;
    return {x, y, width, height};
}


// Return the font size adjusted for the given type of text.
function font_adjust(fs, type) {
    for (const [expression, label] of view.labels)
        if (type === get_class_name("label_" + expression))
            return Math.min(label.max_size, fs);
            // Since the label may specify a smaller font size than fs.

    return fs;
}
