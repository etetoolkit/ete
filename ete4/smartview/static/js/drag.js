// Drag-related functions.

import { view, menus } from "./gui.js";
import { update_minimap_visible_rect } from "./minimap.js";
import { draw_tree } from "./draw.js";

export { drag_start, drag_stop, drag_move };


// Object with the current state of the thing being dragged.
const dragging = {
    element: undefined,  // DOM element where we are dragging
    moved: false,  // has it actually moved? (to avoid redrawing if not)
    p0: {x: 0, y: 0},  // cursor position at the start of the dragging
    p_last: {x: 0, y: 0},  // cursor position since the last drag_move() call
};



function drag_start(point, element) {
    dragging.p0 = dragging.p_last = point;
    dragging.element = element;
}


function drag_stop() {
    if (dragging.element === undefined)
        return;

    if ([div_tree, div_aligned, div_legend].includes(dragging.element))
        dragging.element.style.cursor = "auto";
    else if (dragging.element === div_visible_rect)
        dragging.element.style.cursor = "grab";

    if (dragging.moved) {
        draw_tree();
        dragging.moved = false;
    }

    dragging.element = undefined;
}


function drag_move(point) {
    if (!dragging.element)
        return;

    if ([div_tree, div_visible_rect, div_legend].includes(dragging.element))
        dragging.element.style.cursor = "grabbing";
    else if (dragging.element === div_aligned)
        dragging.element.style.cursor = "ew-resize";

    const movement = {x: point.x - dragging.p_last.x,
                      y: point.y - dragging.p_last.y};
    dragging.p_last = point;

    if (dragging.element === div_aligned_grabber) {
        view.align_bar += 100 * movement.x / div_tree.offsetWidth;
        view.align_bar = Math.min(Math.max(view.align_bar, 1), 99);  // clip
        div_aligned.style.width = `${100 - view.align_bar}%`;

        dragging.moved = true;  // so it updates after drag stops
        view.pixi_app_aligned.resizeTo = div_aligned;  // otherwise it forgets

        menus.pane.refresh();  // update the info box
    }
    else if (dragging.element === div_aligned) {
        dragging.moved = true;

        const [scale_x, ] = get_drag_scale();
        view.aligned.origin += scale_x * movement.x;

        if (view.aligned.origin > 0) {
            const dx = point.x - dragging.p0.x;
            Array.from(div_aligned.children[1].children).forEach(g =>
                g.setAttribute("transform", `translate(${dx} 0)`));
        }
        else {
            view.aligned.origin = 0;
        }
    }
    else if (dragging.element === div_legend) {
        const x = div_legend.offsetLeft + movement.x;
        const y = div_legend.offsetTop  + movement.y;
        const xmax = div_tree.offsetWidth  - div_legend.offsetWidth;
        const ymax = div_tree.offsetHeight - div_legend.offsetHeight;
        div_legend.style.left = `${Math.max(0, Math.min(x, xmax))}px`;
        div_legend.style.top  = `${Math.max(0, Math.min(y, ymax))}px`;
    }
    else {
        dragging.moved = true;

        const [scale_x, scale_y] = get_drag_scale();
        view.tl.x += scale_x * movement.x;
        view.tl.y += scale_y * movement.y;

        let dx = point.x - dragging.p0.x,
            dy = point.y - dragging.p0.y;

        if (dragging.element === div_visible_rect) {
            dx *= -view.zoom.x / view.minimap.zoom.x;
            dy *= -view.zoom.y / view.minimap.zoom.y;
        }

        Array.from(div_tree.children[0].children).forEach(g =>
            g.setAttribute("transform", `translate(${dx} ${dy})`));

        menus.pane.refresh();  // update the info box on the menu

        if (view.minimap.show)
            update_minimap_visible_rect();
    }
}

function get_drag_scale() {
    if (dragging.element === div_tree)
        return [-1 / view.zoom.x, -1 / view.zoom.y];
    else if (dragging.element === div_aligned)
        return [-1 / view.aligned.zoom, 0];
    else // dragging.element === div_visible_rect
        return [1 / view.minimap.zoom.x, 1 / view.minimap.zoom.y];
}
