// Functions related to labels.

import { view, menus, to_opts } from "./gui.js";
import { draw_tree, get_class_name } from "./draw.js";

export { label_expression, label_property, colorize_labels, add_label_to_menu };


// Put a label in the nodes and redraw the tree (with the new label too).
async function label_expression() {
    const result = await Swal.fire({
        input: "text",
        position: "top-end",
        inputPlaceholder: "Enter expression",
        showConfirmButton: false,
        preConfirm: text => {
            if (!text)
                return false;
        },
    });

    if (result.isConfirmed) {
        add_label_to_menu(result.value);
        draw_tree();
    }
}


function label_property() {
    const prop = view.current_property;

    if (prop === "name" || prop === "length")
        add_label_to_menu(prop);
    else
        add_label_to_menu(`p.get('${prop}', '')`);

    draw_tree();
}


function add_label_to_menu(expression, nodetype="any", position="top",
                           color=undefined, column=0, anchor=undefined,
                           font="sans-serif", max_size=15) {
    const folder_labels = menus.labels;

    if (folder_labels.children.map(x => x.title).includes(expression)) {
        Swal.fire({
            html: "Label already exists", icon: "warning", timer: 5000,
            toast: true, position: "top-end",
        });
        return;
    }

    const folder = folder_labels.addFolder({title: expression, expanded: false});

    const colors = ["#0A0", "#A00", "#00A", "#550", "#505", "#055", "#000"];
    const nlabels = view.labels.size;

    view.labels.set(expression, {
        nodetype: nodetype,
        position: position,
        column: column,
        anchor: anchor ? anchor : default_anchor(position),
        color: color || colors[nlabels % colors.length],
        font: font,
        max_size: max_size,
    });

    view.labels.get(expression).remove = function() {
        view.labels.delete(expression);
        folder.dispose();
        draw_tree();
    }

    const label = view.labels.get(expression);

    folder.addBinding(label, "nodetype",
        {options: to_opts(["leaf", "internal", "any"])}).on("change", draw_tree);

    const positions = ["top", "bottom", "left", "right", "aligned"];
    folder.addBinding(label, "position", {options: to_opts(positions)})
        .on("change", ({value: pos}) => {
            label.anchor = default_anchor(pos);
            label.nodetype = ["right", "aligned"].includes(pos) ? "leaf" : label.nodetype;
            folder.refresh();  // to reflect the new values in the gui
            draw_tree();
        });

    folder.addBinding(label, "column", {min: 0, max: 20, step: 1})
        .on("change", draw_tree);

    folder.addBinding(label, "anchor", {x: {min: -1, max: 1}, y: {min: -1, max: 1}})
        .on("change", draw_tree);

    folder.addBinding(label, "color").on("change",
        () => colorize_label(expression));

    folder.addBinding(label, "font", {options: to_opts(
        ["sans-serif", "serif", "monospace"])}).on("change",
        () => colorize_label(expression));

    folder.addBinding(label, "max_size", {label: "max size", min: 1, max: 100})
        .on("change", draw_tree);

    folder.addButton({title: "remove"}).on("click", label.remove);
}

function default_anchor(position) {
    const p = position;  // shortcut
    return p === "top"     ? {x: -1, y: 1} :   // left, bottom
           p === "bottom"  ? {x: -1, y: -1} :  // left, top
           p === "right"   ? {x: -1, y: 0} :   // left, middle
           p === "left"    ? {x:  1, y: 0} :   // right, middle
           p === "aligned" ? {x: -1, y: 0} :   // left, middle
                             {x: null, y: null};
}
// See also default_anchors in faces.py.

function colorize_label(expression) {
    const label = view.labels.get(expression);

    const clabel = get_class_name("label_" + expression);
    Array.from(div_tree.getElementsByClassName(clabel)).forEach(e => {
        e.style.fill = label.color;
        e.style.fontFamily = label.font;
    });
    Array.from(div_aligned.getElementsByClassName(clabel)).forEach(e => {
        e.style.fill = label.color;
        e.style.fontFamily = label.font;
    });
}


function colorize_labels() {
    view.labels.forEach((label, expression) => colorize_label(expression));
}
