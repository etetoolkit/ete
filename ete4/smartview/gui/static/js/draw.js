// Functions related to updating (drawing) the view.

import { view, get_tid, on_box_click, on_box_wheel, get_active_layouts } from "./gui.js";
import { update_minimap_visible_rect } from "./minimap.js";
import { colorize_searches, get_search_class } from "./search.js";
import { colorize_selections, get_selection_class } from "./select.js";
import { on_box_contextmenu } from "./contextmenu.js";
import { api } from "./api.js";
import { draw_pixi } from "./pixi.js";

export { update, draw_tree, draw_tree_scale, draw, get_class_name, cartesian_shifted };


// Update the view of all elements (gui, tree, minimap).
async function update() {
    await draw_tree();

    if (view.minimap.show)
        update_minimap_visible_rect();
}


var align_timeout; // Do not constantly render aligned panel (too costly) when scrolling
var align_drawing = false;
// Ask the server for a tree in the new defined region, and draw it.
async function draw_tree() {
    const [zx, zy] = [view.zoom.x, view.zoom.y];
    const [x, y] = [view.tl.x, view.tl.y];
    const [w, h] = [div_tree.offsetWidth / zx, div_tree.offsetHeight / zy];

    div_tree.style.cursor = "wait";
    
    const layouts = JSON.stringify(get_active_layouts());

    const params_rect = {  // parameters we have to pass to the drawer
        "drawer": view.drawer.name, "min_size": view.min_size,
        "zx": zx, "zy": zy, "x": x, "y": y, "w": w, "h": h,
        "collapsed_ids": JSON.stringify(Object.keys(view.collapsed_ids)),
        "layouts": layouts, "ultrametric": view.ultrametric ? 1 : 0,
    };

    const params_circ = {  // parameters to the drawer, in circular mode
        ...params_rect,  // all the parameters in params_rect, plus:
        "rmin": view.rmin, "amin": view.angle.min, "amax": view.angle.max,
    };

    const params = view.drawer.type === "rect" ? params_rect : params_circ;
    const qs = new URLSearchParams(params).toString();  // "x=...&y=..."

    try {
        clearTimeout(align_timeout);

        const items = await api(`/trees/${get_tid()}/draw?${qs}`);

        draw(div_tree, items, view.tl, view.zoom);

        clearTimeout(align_timeout);

        view.nnodes = div_tree.getElementsByClassName("node").length;
        colorize_searches();
        colorize_selections();

        const drawer_info = await api(`/drawers/${view.drawer.name}/${get_tid()}`);
        view.drawer.npanels = drawer_info.npanels; // type has already been set

        // Toggle aligned panel
        if (drawer_info.type === "rect" && drawer_info.npanels > 1)
            div_aligned.style.display = "initial";  // show aligned panel
        else
            div_aligned.style.display = "none";  // hide aligned panel

        if (view.drawer.npanels > 1) {
            align_timeout = setTimeout(async () => { 
                if (!align_drawing)
                    await draw_aligned(params);
                clearTimeout(align_timeout);
            }, 200);
        }

        if (view.drawer.type === "circ") {
            fix_text_orientations();

            if (view.angle.min < -180 || view.angle.max > 180)
                draw_negative_xaxis();
        }

        draw_tree_scale();
    }
    catch (ex) {
        Swal.fire({
            html: `When drawing: ${ex.message}`,
            icon: "error",
        });
    }

    div_tree.style.cursor = "auto";
}


// Draw tree scale depending on the horizontal zoom level
function draw_tree_scale() {
    function create_hz_line() {
        const [ x1, y1 ] = [ x0, y0 ];
        const [ x2, y2 ] = [ x1 + length, y1 ];
        return create_svg_element("line", {
            "x1": x1, "y1": y1,
            "x2": x2, "y2": y2,
            "stroke": view.tree_scale.color,
            "stroke-width": view.tree_scale.width,
        });
    }

    function create_vt_line(pos="right") {
        const x = x0 + ( pos === "right" ? length : 0 );
        const [ x1, y1 ] = [ x, y0 - height / 2];
        const [ x2, y2 ] = [ x, y0 + height / 2 ];
        return create_svg_element("line", {
            "x1": x1, "y1": y1,
            "x2": x2, "y2": y2,
            "stroke": view.tree_scale.color,
            "stroke-width": view.tree_scale.width,
        });
    }
    
    function create_text(text) {
        const t = create_svg_element("text", { 
            "font-size": view.tree_scale.fsize,
            "fill": view.tree_scale.color,
            x: x0 + length + 10,
            y: y0 + height / 2,
        });
        t.appendChild(document.createTextNode(text));
        return t;
    }

    // Only show when required
    if (view.tree_scale.show)
        tree_scale.style.display = "block";
    else {
        tree_scale.style.display = "none";
        return
    }

    const length = view.tree_scale.length;
    const height = view.tree_scale.height;
    const [ x0, y0 ] = [ 15, 15 ];

    const g = create_svg_element("g");
    g.appendChild(create_hz_line());
    g.appendChild(create_vt_line("left"));
    g.appendChild(create_vt_line("right"));

    // Text
    const value = view.tree_scale.length / view.zoom.x;
    const rounded = value < 0.001 ? value.toExponential(1) : value.toFixed(3);
    g.appendChild(create_text(String(rounded)));


    replace_child(tree_scale.children[0], g);
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

    const svg_items = items.filter(i => !i[0].includes("pixi-"));
    svg_items.forEach(item => g.appendChild(create_item(g, item, tl, zoom)));
    
    const pixi_items = items.filter(i => i[0].includes("pixi-"));
    const pixi = draw_pixi(pixi_items, tl, zoom)
    const pixi_container = view.drawer.type === "rect" ? div_aligned : div_tree;
    replace_child(pixi_container.querySelector(".div_pixi"), pixi);

    put_nodes_in_background(g);

    if (replace)
        replace_svg(element);

    const svg = element.children[0];
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
        e.style.opacity = null; // Remove bg_node styles
        e.style.fill = null;
        g.insertBefore(bg_node, first);
    });
    Array.from(g.getElementsByClassName("box")).forEach(e => g.insertBefore(e, first));
}

function replace_child(element, child) {
    if (element.children.length)
        element.children[0].replaceWith(child);
    else
        element.appendChild(child);
}

// Replace the svg that is a child of the given element (or just add if none).
function replace_svg(element) {
    const svg = create_svg_element("svg", {
        "width": element.offsetWidth,
        "height": element.offsetHeight,
    });

    if (element.children.length > 0)
        element.children[0].replaceWith(svg);
    else
        element.appendChild(svg);
}


// Draw elements that belong to panels above 0.
async function draw_aligned(params) {
    const panels = { 
        1: div_aligned, 
        2: div_aligned_header_top, 
        3: div_aligned_header_bottomn 
    };

    if (view.drawer.type === "rect") {
        for (let panel = 1; panel < view.drawer.npanels; panel++) {
            const qs = new URLSearchParams({...params, "panel": panel}).toString();

            align_drawing = true;

            const items = await api(`/trees/${get_tid()}/draw?${qs}`);

            draw(panels[panel], items, {x: 0, y: view.tl.y}, view.zoom);

            align_drawing = false;

            // NOTE: Only implemented for panel=1 for the moment. We just need to
            //   decide where the graphics would go for panel > 1 (another div? ...)
            
        }
    }
    else {
        for (let panel = 1; panel < view.drawer.npanels; panel++) {
            const qs = new URLSearchParams({
                ...params, "panel": panel,
                "rmin": view.rmin + panel * view.tree_size.width
            }).toString();

            const items = await api(`/trees/${get_tid()}/draw?${qs}`);

            const replace = false;
            draw(div_tree, items, view.tl, view.zoom, replace);
        }
    }
}


// Return the graphical (svg) element corresponding to a drawer item.
function create_item(g, item, tl, zoom) {
    // item looks like ["line", ...] for a line, etc.

    const [zx, zy] = [zoom.x, zoom.y];  // shortcut 
    if (item[0] === "nodebox") {
        const [ , box, name, properties, node_id, result_of, style] = item;

        const b = create_box(box, tl, zx, zy, "", style);

        b.id = "node-" + node_id.join("_");

        b.classList.add("node");

        if (result_of.length === 1) {
            const t = result_of[0];
            const cnode = Object.keys(view.searches).includes(t)
                ? get_search_class(t) : get_selection_class(t);
            b.classList.add(cnode);
        } else if (result_of.length > 1) {
            const [ x, y, width, dy ] = box;
            const dx = width / result_of.length;
            result_of.forEach((t, i) => {
                const box = [ x + dx * i, y, dx, dy ];
                const b = create_box(box, tl, zx, zy, "", style);
                style_nodebox(b, style);
                const cnode = Object.keys(view.searches).includes(t) 
                    ? get_search_class(t) : get_selection_class(t);
                b.classList.add(cnode);
                g.appendChild(b);
            })
        }

        style_nodebox(b, style);

        b.addEventListener("click", event =>
            on_box_click(event, box, node_id));
        b.addEventListener("contextmenu", event =>
            on_box_contextmenu(event, box, name, properties, node_id));
        b.addEventListener("wheel", event =>
            on_box_wheel(event, box), {passive: false});

        if (name.length > 0 || Object.entries(properties).length > 0)
            b.appendChild(create_tooltip(name, properties));

        return b;
    }
    else if (item[0] === "outline") {
        const [ , sbox, style] = item;

        const outline = create_outline(sbox, tl, zx, zy);

        style_outline(outline, style);

        return outline
    }
    else if (item[0] === "line") {
        const [ , p1, p2, type, parent_of, style] = item;

        const line = create_line(p1, p2, tl, zx, zy, type, parent_of);

        style_line(line, style);

        return line;
    }
    else if (item[0] === "arc") {
        const [ , p1, p2, large, type, style] = item;

        const arc = create_arc(p1, p2, large, tl, zx, type);

        style_line(arc, style);

        return arc;
    }
    else if (item[0] === "circle") {
        const [ , center, radius, type, style] = item;

        const circle = create_circle(center, radius, tl, zx, zy, type);

        style_ellipse(circle, style); // same styling as ellipse

        return circle
    }
    else if (item[0] === "ellipse") {
        const [ , center, rx, ry, type, style] = item;

        const ellipse = create_ellipse(center, rx, ry, tl, zx, zy, type);

        if (view.drawer.type == "circ") {
            const {x: cx, y: cy} = cartesian_shifted(center[0], center[1], tl, zx);
            const angle = Math.atan2(zy * tl.y + cy, zx * tl.x + cx) * 180 / Math.PI;
            addRotation(ellipse, angle, cx, cy);
        }
        
        style_ellipse(ellipse, style);

        return ellipse;
    }
    else if (item[0] === "triangle") {
        const [ , box, tip, type, style] = item;

        const triangle = create_triangle(box, tip, tl, zx, zy, type);

        const [r, a, dr, da] = box;
        if (view.drawer.type === "circ" 
            && ["top", "bottom"].includes(tip)
            && (Math.abs(a + da) > Math.PI / 2)) {
            const {x: cx, y: cy} = cartesian_shifted(r + dr / 2,
                                                     a + da / 2, 
                                                     tl, zx);
            addRotation(triangle, 180, cx, cy);
        }

        style_polygon(triangle, style);

        return triangle;
    }
    else if (item[0] === "text") {
        const [ , box, txt, type, rotation, anchor, style] = item;

        const text = create_text(box, rotation, txt, style.max_fsize,
            tl, zx, zy, get_class_name(type), anchor, style);

        style_text(text, style);

        return text;
    }
    else if (item[0] === "rect") {
        const [ , box, type, style] = item;

        const rect = create_box(box, tl, zx, zy, type, style);

        style_polygon(rect, style);

        return rect;
    }
    else if (item[0] === "rhombus") {
        const [ , points, type, style] = item;

        const rhombus = create_polygon(points, tl, zx, zy, "rhombus " + type);

        style_polygon(rhombus, style);

        return rhombus;
    }
    else if (item[0] === "polygon") {
        const [ , points, type, style] = item;

        const polygon = create_polygon(points, tl, zx, zy, "polygon " + type);

        style_polygon(polygon, style);

        return polygon;
    }
    else if (item[0] === "array") {
        const [ , box, array] = item;
        const [x0, y0, dx0, dy0] = box;
        const dx = dx0 / array.length / zx;

        const [y, dy] = pad(y0, dy0, view.array.padding);

        const g = create_svg_element("g");
        for (let i = 0, x = x0; i < array.length; i++, x+=dx) {
            const r = view.drawer.type === "rect" ?
                create_rect([x, y, dx, dy], tl, zx, zy) :
                create_asec([x, y, dx, dy], tl, zx);
            r.style.stroke = `hsl(${array[i]}, 100%, 50%)`;
            g.appendChild(r);
        }

        return g;
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
function create_box(box, tl, zx, zy, type, style) {
    const b = view.drawer.type === "rect" ?
                    create_rect(box, tl, zx, zy, type, style) :
                    create_asec(box, tl, zx, type, style);
    b.classList.add("box");
    return b;
}


function create_rect(box, tl, zx, zy, type, style) {
    const [x, y, w, h] = box;

    const r = (is_style_property(style.rounded)) ? 4 : 0;

    return create_svg_element("rect", {
        "x": zx * (x - tl.x), "y": zy * (y - tl.y),
        "width": zx * w, "height": zy * h,
        "rx": r, "ry": r,
        "class": "rect " + type,
    });
}


// Return a svg annular sector, described by box and with zoom z.
function create_asec(box, tl, z, type, style) {
    const [r, a, dr, da] = box;
    const large = da > Math.PI ? 1 : 0;
    const p00 = cartesian_shifted(r, a, tl, z),
          p01 = cartesian_shifted(r, a + da, tl, z),
          p10 = cartesian_shifted(r + dr, a, tl, z),
          p11 = cartesian_shifted(r + dr, a + da, tl, z);

    const element =  {
        "d": `M ${p00.x} ${p00.y}
              L ${p10.x} ${p10.y}
              A ${z * (r + dr)} ${z * (r + dr)} 0 ${large} 1 ${p11.x} ${p11.y}
              L ${p01.x} ${p01.y}
              A ${z * r} ${z * r} 0 ${large} 0 ${p00.x} ${p00.y}`,
    };

    if (type)
        element.class = type;

    if (is_style_property(style.id))
        element.id = style.id;
    
    return create_svg_element("path", element);
}


function cartesian_shifted(r, a, tl, z) {
    return {x: z * (r * Math.cos(a) - tl.x),
            y: z * (r * Math.sin(a) - tl.y)};
}


// Return an outline (collapsed version of a box).
function create_outline(sbox, tl, zx, zy) {
    if (view.drawer.type === "rect")
        return create_rect_outline(sbox, tl, zx, zy);
    else
        return create_circ_outline(sbox, tl, zx);
}


// Return a svg horizontal outline.
function create_rect_outline(sbox, tl, zx, zy) {
    const [x, y, dx_min, dx_max, dy] = transform_sbox(sbox, tl, zx, zy);

    const dx = view.outline.slanted ? dx_min : dx_max;

    return create_svg_element("path", {
        "class": "outline",
        "d": `M ${x} ${y + dy/2}
              L ${x + dx_max} ${y}
              L ${x + dx} ${y + dy}
              L ${x} ${y + dy/2}`,
    });
}

// Return the box translated (from tl) and scaled.
function transform_box(box, tl, zx, zy) {
    const [x, y, dx, dy] = box;
    return [zx * (x - tl.x), zy * (y - tl.y), zx * dx, zy * dy];
}

// Return the sbox translated (from tl) and scaled.
function transform_sbox(sbox, tl, zx, zy) {
    const [x, y, dx_min, dx_max, dy] = sbox;
    return [zx * (x - tl.x), zy * (y - tl.y), zx * dx_min, zx * dx_max, zy * dy];
}


// Return a svg outline in the direction of an annular sector.
function create_circ_outline(sbox, tl, z) {
    const [r, a, dr_min, dr_max, da] = sbox;

    const dr = view.outline.slanted ? dr_min : dr_max;

    const large = da > Math.PI ? 1 : 0;
    const p0 = cartesian_shifted(r, a + da/2, tl, z),
          p10 = cartesian_shifted(r + dr_max, a, tl, z),
          p11 = cartesian_shifted(r + dr, a + da, tl, z);

    return create_svg_element("path", {
        "class": "outline",
        "d": `M ${p0.x} ${p0.y}
              L ${p10.x} ${p10.y}
              A ${z * (r + dr_max)} ${z * (r + dr)} 0 ${large} 1 ${p11.x} ${p11.y}
              L ${p0.x} ${p0.y}`,
    });
}


// Return an element that, appended to a svg element (normally a box), will
// make it show a tooltip showing nicely the given name and properties.
function create_tooltip(name, properties) {
    const title = create_svg_element("title", {});
    const text = (name ? name : "(unnamed)") + "\n" +
        Object.entries(properties).map(x => x[0] + ": " + x[1]).join("\n");
    title.appendChild(document.createTextNode(text));
    return title;
}


function create_line(p1, p2, tl, zx, zy, type="", parent_of=[]) {
    const [x1, y1] = [zx * (p1[0] - tl.x), zy * (p1[1] - tl.y)],
          [x2, y2] = [zx * (p2[0] - tl.x), zy * (p2[1] - tl.y)];

    const classes = "line " + type + " " +
        parent_of.map(text => Object.keys(view.searches).includes(text)
            ? get_search_class(text, "parents")
            : get_selection_class(text, "parents")).join(" ");

    return create_svg_element("line", {
        "class": classes,
        "x1": x1, "y1": y1,
        "x2": x2, "y2": y2,
        "stroke": view.line.color,
    });
}


function create_arc(p1, p2, large, tl, z, type="") {
    const [x1, y1] = p1,
          [x2, y2] = p2;
    const r = z * Math.sqrt(x1*x1 + y1*y1);
    const n1 = {x: z * (x1 - tl.x), y: z * (y1 - tl.y)},
          n2 = {x: z * (x2 - tl.x), y: z * (y2 - tl.y)};

    return create_svg_element("path", {
        "class": "line " + type,
        "d": `M ${n1.x} ${n1.y} A ${r} ${r} 0 ${large} 1 ${n2.x} ${n2.y}`,
        "stroke": view.line.color,
    });
}


function create_circle(center, radius, tl, zx, zy, type="") {
    // Could be merged with create_ellipse()
    const [cx, cy] = center;
    if (view.drawer.type === "rect") 
        var [x, y] = [zx * (cx - tl.x), zy * (cy - tl.y)]
    else 
        var {x, y} = cartesian_shifted(cx, cy, tl, zx);

    return create_svg_element("circle", {
        "class": "circle " + type,
        "cx": x, "cy": y, "r": radius, // view.node.dot.radius,
    });
}


function create_ellipse(center, rx, ry, tl, zx, zy, type="") {
    const [cx, cy] = center;
    if (view.drawer.type === "rect") 
        var [x, y] = [zx * (cx - tl.x), zy * (cy - tl.y)]
    else 
        var {x, y} = cartesian_shifted(cx, cy, tl, zx);

    return create_svg_element("ellipse", {
        "class": "ellipse " + type,
        "cx": x, "cy": y, "rx": rx, "ry": ry,
    });
}


function create_polygon(points, tl, zx, zy, type="") {
    points.forEach((point, idx, arr) => {
        if (view.drawer.type === "rect") {
            // Translate and scale
            const [x, y] = point;
            point = [zx * (x - tl.x), zy * (y - tl.y)];
        }
        else if (view.drawer.type === "circ") {
            // Polar to translated cartesian coordinates
            const [r, a] = point;
            const {x: px, y: py} = cartesian_shifted(r, a, tl, zx);
            point = [px, py];
        };
        arr[idx] = point; // reassign to point in array
    });

    return create_svg_element("polygon", {
        "class": type,
        "points": points.join(" "),
    });
}


function create_triangle(box, tip, tl, zx, zy, type="") {
    const points = [];
    const [x, y, dx, dy] = view.drawer.type === "rect"
        ? transform_box(box, tl, zx, zy)
        : box;

    if (tip === "top")
        points.push(
            [x + dx/2, y], 
            [x, y + dy], 
            [x + dx, y + dy]);
    if (tip === "right")
        points.push(
            [x, y],
            [x, y + dy],
            [x + dx, y + dy/2]);
    if (tip === "bottom")
        points.push(
            [x, y],
            [x + dx/2, y + dy], 
            [x + dx, y]);
    if (tip === "left")
        points.push(
            [x, y + dy/2], 
            [x + dx, y + dy],
            [x + dx, y]);

    if (view.drawer.type === "circ") 
        points.forEach((point, idx, arr) => {
            const [r, a] = point;
            const {x: px, y: py} = cartesian_shifted(r, a, tl, zx);
            arr[idx] = [px, py];
        });

    return create_svg_element("polygon", {
        "class": "triangle " + type,
        "points": points.join(" "),
    });
}


function create_text(box, rotation, text, fs, tl, zx, zy, type="", anchor, style) {

    const element = {
        "class": "text " + type,
        "text-anchor": (style && style.text_anchor 
                        ? style.text_anchor : "left"),
        "font-size": `${fs}px`,
    }

    if (anchor) {
        const dr = box[2] * zx;
        element.dy = dr - (dr - 0.6 * fs) / 2; // place inside rect
        const t = create_svg_element("text", element);
        const textPath = create_svg_element("textPath", {
            "href": anchor,
            "startOffset": style.offset, // calculated in backend
        });
        textPath.appendChild(document.createTextNode(text));
        t.appendChild(textPath);
        return t;
    }

    const [x, y] = view.drawer.type === "rect" ?
        get_text_placement_rect(box, text, fs, tl, zx, zy) :
        get_text_placement_circ(box, text, fs, tl, zx);
    element.x = x;
    element.y = y;
    let t;
    if (rotation) {
        element.y = y - fs
        t = create_svg_element("text", element);
        addRotation(t, rotation, x, y - fs)
    } else
        t = create_svg_element("text", element);

    t.appendChild(document.createTextNode(text));

    if (view.drawer.type === "circ") {
        const angle = Math.atan2(zy * tl.y + y, zx * tl.x + x) * 180 / Math.PI;
        addRotation(t, angle, x, y);
    }

    return t;
}


// Return position to draw text when box is a rect.
function get_text_placement_rect(box, text, fs, tl, zx, zy) {
    if (text.length === 0)
        throw new Error("please do not try to place empty texts :)")
        // We could, but it's almost surely a bug upstream!

    const [x, y, , ] = box;

    const y_in_tree = y + 0.9 * fs / zy;
    // We give the position as the bottom-left point, the same convention as in
    // svgs. We go a bit up (0.9 instead of 1.0) because of the baseline.

    return [zx * (x - tl.x), zy * (y_in_tree - tl.y)];
}


// Return position to draw text when box is an asec.
function get_text_placement_circ(box, text, fs, tl, z) {
    if (text.length === 0)
        throw new Error("please do not try to place empty texts :)");
        // We could, but it's almost surely a bug upstream!

    const [r, a, , ] = box;
    const a_in_tree = a + 0.8 * (fs / r) / z;
    // We give the position as the bottom-left point, the same convention as in
    // svgs. We go a bit up (0.8 instead of 1.0) because of the baseline.

    const x = r * Math.cos(a_in_tree),
          y = r * Math.sin(a_in_tree);

    return [z * (x - tl.x), z * (y - tl.y)];
}


// Flip all the texts in circular representation that look upside-down.
// NOTE: getBBox() is very expensive and requires text to be already in the DOM.
async function fix_text_orientations() {
    const texts = Array.from(div_tree.getElementsByClassName("text"))
        .filter(is_upside_down);

    texts.sort((a, b) => get_font_size(b) - get_font_size(a));

    texts.slice(0, 500).forEach(t => flip_with_bbox(t, t.getBBox()));
    texts.slice(500).forEach(t => flip_with_bbox(t, get_approx_BBox(t)));
}

function is_upside_down(element) {
    try {
        const angle = element.transform.baseVal[0].angle;
        return angle < -90 || angle > 90;
    } catch { return false }; // texts in asec may cause exceptions
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
    if (angle && (-360 < angle < 360))
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


// Chech whether style property exists and is not empty
function is_style_property(property) {
    return property != undefined && property != null && property != ""
}

// Style created items with information from backend
function style_nodebox(nodebox, style){
    if (is_style_property(style.fill))
        nodebox.style.fill = style.fill;
    
    if (is_style_property(style.opacity))
        nodebox.style.opacity = style.opacity;

    return nodebox;
}


function style_line(line, style) {
    if (is_style_property(style.type))
        line.style["stroke-dasharray"] = style.type === "solid" 
            ? null : style.type == "dotted"
            ? 2 : 5;

    if (is_style_property(style["stroke-width"]))
        line.style["stroke-width"] = style["stroke-width"];

    if (is_style_property(style.stroke))
        line.style.stroke = style.stroke;

    return line;
}


function style_outline(outline, style) {
    if (is_style_property(style.fill))
        outline.style.fill = style.fill;

    if (is_style_property(style["fill-opacity"]))
        outline.style["fill-opacity"] = style["fill-opacity"];

    if (is_style_property(style.stroke))
        outline.style.stroke = style.stroke;

    if (is_style_property(style["stroke-width"]))
        outline.style["stroke-width"] = style["stroke-width"];

    return outline;
}


function style_ellipse(ellipse, style) {
    if (is_style_property(style.fill))
        ellipse.style.fill = style.fill;
    return ellipse;
}


function style_text(text, style) {
    if (is_style_property(style.fill))
        text.style.fill = style.fill;

    if (is_style_property(style.ftype))
        text.style["font-family"] = style.ftype;

    if (is_style_property(style.linked_path)) {
        const textPath = create_svg_element("textPath", {
            "xlink:href": style.linked_path,
        })
        text.appendChild(textPath);
    }

    return text;
}


function style_polygon(polygon, style) {
    if (is_style_property(style.fill))
        polygon.style.fill = style.fill;

    if (is_style_property(style.opacity))
        polygon.style.opacity = style.opacity;

    return polygon
}
