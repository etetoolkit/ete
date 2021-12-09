// Drag-related functions.

import { view } from "./gui.js";
import { update_minimap_visible_rect } from "./minimap.js";
import { draw_tree, draw_aligned } from "./draw.js";

export { drag_start, drag_stop, drag_move };


const dragging = {
    element: undefined, moved: false,
    p0: {x: 0, y: 0},
    p_last: {x: 0, y: 0},
    timeout: undefined,
};


function drag_start(point, element, from_grabber=true) {
    if (element === div_aligned)
        div_aligned.style.cursor = "grabbing";
    else {
        div_tree.style.cursor = "grabbing";
        div_visible_rect.style.cursor = "grabbing";
    }
    dragging.from_grabber = from_grabber;
    dragging.element = element;
    point = get_point(point);
    dragging.p0 = dragging.p_last = point;
}


function drag_stop() {
    if (dragging.element === undefined)
        return;

    if (dragging.element === div_aligned)
        div_aligned.style.cursor = "auto";
    else {
        div_tree.style.cursor = "auto";
        div_visible_rect.style.cursor = "grab";
    }

    if (dragging.moved) {
        if (dragging.element == div_aligned)
            draw_aligned();
        else
            draw_tree();
        dragging.moved = false;
    }

    dragging.element = undefined;
}


function drag_move(point) {
    point = get_point(point);
    const movement = {x: point.x - dragging.p_last.x,
                      y: point.y - dragging.p_last.y};
    dragging.p_last = point;

    if (dragging.element) {
        dragging.moved = true;
        if (dragging.element === div_aligned && dragging.from_grabber) {
            view.aligned.pos += 100 * movement.x / div_tree.offsetWidth;
            view.aligned.pos = Math.min(Math.max(view.aligned.pos, 1), 99);  // clip
            div_aligned.style.width = `${100 - view.aligned.pos}%`;
        }
        else {
            const [scale_x, scale_y] = get_drag_scale();

            let dx = point.x - dragging.p0.x,
                dy = point.y - dragging.p0.y;

            if (dragging.element === div_visible_rect) {
                dx *= -view.zoom.x / view.minimap.zoom.x;
                dy *= -view.zoom.y / view.minimap.zoom.y;
            }

            if (dragging.element === div_aligned) {
                view.aligned.x += scale_x * movement.x;

                const toTranslate = [ 
                    //...div_aligned.children[0].children,
                    ...div_aligned_header.children[0].children,
                    ...div_aligned_footer.children[0].children,
                ];
                toTranslate.forEach(g =>
                    g.setAttribute("transform", `translate(${dx} 0)`));
                // pixi canvas
                //div_aligned.children[1].children[0].style.transform = `translate(${movement.x}px, 0)`;

                draw_aligned(undefined, 2);
            }

            else {
                view.tl.x += scale_x * movement.x;
                view.tl.y += scale_y * movement.y;
                Array.from(div_tree.children[0].children).forEach(g =>
                    g.setAttribute("transform", `translate(${dx} ${dy})`));

                if (view.minimap.show)
                    update_minimap_visible_rect();
            }
        }

        return 1
    } else
        return undefined
}


function get_drag_scale() {
    if (dragging.element === div_tree)
        return [-1 / view.zoom.x, -1 / view.zoom.y];
    else if (dragging.element === div_aligned)
        return [-1 / view.zoom.a, -1 / view.zoom.y];
    else // dragging.element === div_visible_rect
        return [1 / view.minimap.zoom.x, 1 / view.minimap.zoom.y];
}


function get_point(point) {
    if (dragging.element === div_aligned && !dragging.from_grabber)
        return { 
            x: point.x - div_tree.offsetWidth * view.aligned.pos / 100,
            y: point.y,
        }
    return point
}
