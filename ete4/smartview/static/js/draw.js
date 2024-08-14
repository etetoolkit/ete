// Functions related to updating (drawing) the view.

import { view, menus, get_tid, on_box_click, on_box_wheel, tree_command, reset_view }
    from "./gui.js";
import { update_minimap_visible_rect } from "./minimap.js";
import { colorize_searches, get_search_class } from "./search.js";
import { on_box_contextmenu } from "./contextmenu.js";
import { colorize_tags } from "./tag.js";
import { colorize_labels } from "./label.js";
import { api } from "./api.js";

export { update, draw_tree, draw, get_class_name };


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

        // Separate them per panel.
        const [items_per_panel, xmax] = get_items_per_panel(commands);

        // The main function: draw all received items on panel 0 in div_tree.
        draw(div_tree, items_per_panel[0], view.tl, view.zoom);

        // Add aligned panel items.
        draw_aligned(items_per_panel[1], xmax);  // items in panel 1 (aligned)

        // Update variable that shows the number of visible nodes in the menu.
        view.nnodes_visible = div_tree.getElementsByClassName("node").length;

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

// Return number x as a nice string (with approximately n precision digits).
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
        "min_size": view.min_size, "min_size_content": view.min_size_content,
        "zx": zx, "zy": zy, "x": x, "y": y, "w": w, "h": h,
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


// Return an object with keys the panel numbers (0, 1, ...), and
// values a list of graphics to draw on them.
function get_items_per_panel(commands) {
    const items = {};
    let xmax = 0;

    let current_panel = 0;
    commands.forEach(c => {
        if (c[0] === "panel") {  // we got a "change panel" command
            current_panel = c[1];
        }
        else if (c[0] === "xmax") {  // we got a "set xmax" command
            xmax = c[1];
        }
        else {  // we got a normal drawing command
            if (!(current_panel in items))
                items[current_panel] = [];
            items[current_panel].push(c);
        }
    });

    return [items, xmax];
}


// Draw items in the aligned position.
function draw_aligned(items, xmax) {
    if (view.shape === "rectangular") {
        if (items) {
            div_aligned.style.display = "flex";  // show aligned panel
            const tl = {x: 0, y: view.tl.y};  // relative "top-left" point
            draw(div_aligned, items, tl, view.zoom);
        }
        else {  // no items in aligned panel
            div_aligned.style.display = "none";  // hide aligned panel
        }
    }
    else if (view.shape === "circular") {
        div_aligned.style.display = "none";  // hide aligned panel (may be open)

        if (items) {
            // Translate  r -> r + rmax
            const translated_items = items.map(item => translate(item, xmax));

            const replace = false;
            draw(div_tree, translated_items, view.tl, view.zoom, replace);
        }
    }
}

// Translate the position of the given item.
function translate(item, shift) {
    if (item[0] === "text") {
        const [ , box, anchor, text, fs_max, style] = item;
        const [x, y, dx, dy] = box;
        const tbox = [x + shift, y, dx, dy];
        return ["text", tbox, anchor, text, fs_max, style];
    }
    else if (item[0] === "circle") {
        const [ , [x, y], radius, style] = item;
        return ["circle", [x + shift, y], radius, style];
    }
    else if (item[0] === "rect") {
        const [ , [x, y, w, h], style] = item;
        return ["rect", [x + shift, y, w, h], style];
    }
    else {
        return item;  // we are not translating anything else for the moment
    }
}


// Add a line to the svg in div_tree marking the -x axis.
// Useful when we represent circular trees with angles < -180 or > 180.
function draw_negative_xaxis() {
    const x1 = -view.rmin;
    const x2 = x1 - view.tree_size.width;
    const item = ["line", [x1, 0], [x2, 0], "negative_xaxis", []];
    const replace = false;
    draw(div_tree, [item], view.tl, view.zoom, replace);
}


// Append a svg to the given element, with all the items in the list drawn.
// The first child of element will be used or replaced as a svg.
function draw(element, items, tl, zoom, replace=true) {
    const g = create_svg_element("g");

    items.forEach(item => g.appendChild(create_item(item, tl, zoom)));

    put_nodes_in_background(g);

    if (replace)
        replace_svg(element);

    const svg = element.getElementsByTagName("svg")[0];
    svg.appendChild(g);
}


// Make a copy of the nodeboxes and put them before all the other elements,
// so if they stop being transparent (because they are tagged, or the result
// of a search, or the user changes the node opacity), they do not cover the
// rest of the tree elements.
// The original elements stay transparent in the foreground so the user can
// interact with them (highlighting, opening their contextmenu, etc.).
function put_nodes_in_background(g) {
    const first = g.children[0];  // first svg element, for reference
    Array.from(g.getElementsByClassName("node")).forEach(e => {
        const bg_node = e.cloneNode();
        e.id = "foreground-" + bg_node.id;  // avoid id collisions
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


// Return the graphical (svg) element corresponding to a graphical item.
function create_item(item, tl, zoom) {
    // item looks like ["line", ...] for a line, etc.

    const [zx, zy] = [zoom.x, zoom.y];  // shortcut

    if (item[0] === "nodebox") {
        const [ , box, name, props, node_id, result_of] = item;

        const b = create_box(box, tl, zx, zy);

        b.id = "node-" + node_id.join("_");  // used in tags

        b.classList.add("node");
        result_of.forEach(t => b.classList.add(get_search_class(t, "results")));

        b.addEventListener("click", event =>
            on_box_click(event, box, node_id));
        b.addEventListener("contextmenu", event =>
            on_box_contextmenu(event, box, name, props, node_id));
        b.addEventListener("wheel", event =>
            on_box_wheel(event, box), {passive: false});

        if (name || Object.entries(props).length > 0)
            b.appendChild(create_tooltip(name, props));

        return b;
    }
    else if (item[0] === "outline") {
        const [ , points] = item;

        return create_outline(points, tl, zx, zy);
    }
    else if (item[0] === "line") {
        const [ , p1, p2, style, kwargs] = item;

        return create_line(p1, p2, tl, zx, zy, style, kwargs);
    }
    else if (item[0] === "arc") {
        const [ , p1, p2, large, style, kwargs] = item;

        return create_arc(p1, p2, large, tl, zx, style, kwargs);
    }
    else if (item[0] === "circle") {
        const [ , center, radius, style] = item;

        return create_circle(center, radius, tl, zx, zy, style);
    }
    else if (item[0] === "rect") {
        const [ , box, style] = item;

        return create_box(box, tl, zx, zy, style);
    }
    else if (item[0] === "text") {
        const [ , box, anchor, text, fs_max, style] = item;
        const s = typeof style === "string" ? get_class_name(style) : style;
        return create_text(box, anchor, text, fs_max, tl, zx, zy, s);
    }
    else if (item[0] === "array") {
        const [ , box, array] = item;
        const [x0, y0, dx0, dy0] = box;
        const dx = dx0 / array.length / zx;

        const [y, dy] = pad(y0, dy0, view.array.padding);

        const g = create_svg_element("g");
        for (let i = 0, x = x0; i < array.length; i++, x+=dx) {
            const r = view.shape === "rectangular" ?
                create_rect([x, y, dx, dy], tl, zx, zy) :
                create_asec([x, y, dx, dy], tl, zx);
            r.style.fill = `hsl(${array[i]}, 100%, 50%)`;
            g.appendChild(r);
        }

        return g;
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
    b.classList.add("box");
    return b;
}


function create_rect(box, tl, zx, zy, style="") {
    const [x, y, w, h] = box;

    const p = tree2rect([x, y], tl, zx, zy);

    const element = create_svg_element("rect", {
        "x": p.x, "y": p.y,
        "width": zx * w, "height": zy * h,
    });

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


// Return an outline (collapsed version of a box).
function create_outline(points, tl, zx, zy) {
    if (view.shape === "rectangular")
        return create_rect_outline(points, tl, zx, zy);
    else
        return create_circ_outline(points, tl, zx);
}


// Return a svg horizontal outline.
function create_rect_outline(points, tl, zx, zy) {
    const ps = points.map(p => tree2rect(p, tl, zx, zy));

    return create_svg_element("path", {
        "class": "outline",
        "d": (`M ${ps[0].x} ${ps[0].y} ` +
              ps.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ')),
    });
}


// Return a svg outline in the direction of an annular sector.
function create_circ_outline(points, tl, z) {
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
        "class": "outline",
        "d": (`M ${ps[0].x} ${ps[0].y} ` +
              ps.slice(1).map(arc).join(' ')),
    });
}


// Return an element that, appended to a svg element (normally a box), will
// make it show a tooltip showing nicely the given name and properties.
function create_tooltip(name, props) {
    const title = create_svg_element("title", {});
    const text = (name ? name : "(unnamed)") + "\n" +
        Object.entries(props).map(x => x[0] + ": " + x[1]).join("\n");
    title.appendChild(document.createTextNode(text));
    return title;
}


function create_line(p1, p2, tl, zx, zy, style="", kwargs=null) {
    // Transform points to screen coordinates.
    const pt1 = tree2rect(p1, tl, zx, zy),
          pt2 = tree2rect(p2, tl, zx, zy);

    // Classes, including the ones that mark the line as leading to a search.
    const parent_of = kwargs?.parent_of || [];
    const classes = "line " +
        parent_of.map(text => get_search_class(text, "parents")).join(" ");

    const element = create_svg_element("line", {
        "class": classes,
        "x1": pt1.x, "y1": pt1.y,
        "x2": pt2.x, "y2": pt2.y,
    });

    add_style(element, style);

    return element;
}


function create_arc(p1, p2, large, tl, z, style="", kwargs=null) {
    const n1 = tree2rect(p1, tl, z, z),
          n2 = tree2rect(p2, tl, z, z);
    const r = z * Math.sqrt(p1[0]*p1[0] + p1[1]*p1[1]);

    const parent_of = kwargs?.parent_of || []
    const classes = "line " +
        parent_of.map(text => get_search_class(text, "parents")).join(" ");

    const element = create_svg_element("path", {
        "class": classes,
        "d": `M ${n1.x} ${n1.y} A ${r} ${r} 0 ${large} 1 ${n2.x} ${n2.y}`,
    });

    add_style(element, style);

    return element;
}


function create_circle(center, radius, tl, zx, zy, style="") {
    const c = view.shape === "rectangular" ?
        tree2rect(center, tl, zx, zy) :
        tree2circ(center, tl, zx);

    const is_nodedot = (typeof style === "string" &&
                        style.split(" ").includes("nodedot"));
    const r = is_nodedot ? view.node.dot.radius : radius;

    const element = create_svg_element("circle", {
        "class": "circle",
        "cx": c.x,
        "cy": c.y,
        "r": r,
    });

    add_style(element, style);

    return element;
}


function create_text(box, anchor, text, fs_max, tl, zx, zy, style="") {
    const [x, y, fs, text_anchor] = view.shape === "rectangular" ?
        get_text_placement_rect(box, anchor, text, fs_max, tl, zx, zy, style) :
        get_text_placement_circ(box, anchor, text, fs_max, tl, zx, style);

    const dx = (style === "name") ? view.name.padding.left * fs / 100 : 0;

    const t = create_svg_element("text", {
        "class": "text",
        "x": x + dx, "y": y,
        "font-size": `${fs}px`,
        "text-anchor": text_anchor,
    });

    t.appendChild(document.createTextNode(text));

    if (view.shape === "circular") {
        const angle = Math.atan2(zy * tl.y + y, zx * tl.x + x) * 180 / Math.PI;
        addRotation(t, angle, x, y);
    }

    add_style(t, style);

    return t;
}


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


// Add style to the given element.
function add_style(element, style) {
    if (typeof style === "string") {  // style refers to class name(s)
        for (const name of style.split(" ").filter(x => x)) { // nonempty names
            // We define the "layout_" styles in the css (in
            // gui.js:set_tree_style()), and the "label_" styles with the gui.
            const prefix = name.startsWith("label_") ? "" : "layout_";
            // draw.py sends labels styles with the "label_" prefix, and
            // label.js:colorize_label() expects their class start as "label_".
            // This may not be the clearest way to prefix things...

            element.classList.add(prefix + name);
        }
    }
    else {  // style is an object with the individual properties to set
        for (const [prop, value] of Object.entries(style)) {
            element.style[prop] = value;
        }
    }
}


// Return position, font size and text anchor to draw text when box is a rect.
function get_text_placement_rect(box, anchor, text, fs_max, tl, zx, zy, type="") {
    if (text.length === 0)
        throw new Error("please do not try to place empty texts :)")
        // We could, but it's almost surely a bug upstream!

    const [x, y, dx, dy] = box;

    const dx_char = dx / text.length;  // ~ width of 1 char (in tree units)
    fs_max = Math.min(zx * dx_char * 1.6, zy * dy, fs_max);
    const fs = font_adjust(fs_max, type);

    const scale = fs / (zy * dy);
    const [ax, ay] = anchor;
    const x_in_tree = x + ax * (1 - scale) * dx,
          y_in_tree = y + ay * (1 - scale) * dy + 0.9 * fs / zy;
    // We give the position as the bottom-left point, the same convention as in
    // svgs. We go a bit up (0.9 instead of 1.0) because of the baseline.

    const dx_in_tree = scale * dx;
    const [x_anchor, text_anchor] = anchored_position(x_in_tree, dx_in_tree, ax);

    const corner = tree2rect([x_anchor, y_in_tree], tl, zx, zy);

    return [corner.x, corner.y, fs, text_anchor];
}


// Return position, font size and text anchor to draw text when box is an asec.
function get_text_placement_circ(box, anchor, text, fs_max, tl, z, type="") {
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
    const [r_anchor, text_anchor] = anchored_position(r_in_tree, dr_in_tree, ar);

    const corner = tree2circ([r_anchor, a_in_tree], tl, z);

    return [corner.x, corner.y, fs, text_anchor];
}


// Return the x position and the svg text-anchor to place the text for a given
// original in-tree x text position, dx width, and ax anchor.
// This is useful to fine-tune the placement (since dx is just an approximation
// to the exact width of the text).
function anchored_position(x, dx, ax) {
    if (ax < 0.3)
        return [x, "start"];
    else if (ax < 0.6)
        return [x + dx/2, "middle"];
    else
        return [x + dx, "end"];
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
    addRotation(text, 180, bbox.x + bbox.width/2, bbox.y + bbox.height/2);
}


// Add rotation to element, with angle in degrees and centered around (cx, cy).
function addRotation(element, angle, cx=0, cy=0) {
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
