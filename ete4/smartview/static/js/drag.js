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
    div_tree.style.cursor = "grabbing";
    div_visible_rect.style.cursor = "grabbing";
    dragging.p0 = dragging.p_last = point;
    dragging.element = element;
}


function drag_stop() {
    if (dragging.element === undefined)
        return;

    div_tree.style.cursor = "auto";
    div_visible_rect.style.cursor = "grab";

    if (dragging.moved) {
        draw_tree();
        dragging.moved = false;
    }

    dragging.element = undefined;
}


function drag_move(point) {
    const movement = {x: point.x - dragging.p_last.x,
                      y: point.y - dragging.p_last.y};
    dragging.p_last = point;

    if (dragging.element === div_aligned) {
        view.align_bar += 100 * movement.x / div_tree.offsetWidth;
        view.align_bar = Math.min(Math.max(view.align_bar, 1), 99);  // clip
        menus.pane.refresh();  // update the info box
        div_aligned.style.width = `${100 - view.align_bar}%`;
    }
    else if (dragging.element) {
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
    else // dragging.element === div_visible_rect
        return [1 / view.minimap.zoom.x, 1 / view.minimap.zoom.y];
}
