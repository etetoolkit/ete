// Zoom-related functions.

import { view, menus } from "./gui.js";
import { update, draw_aligned } from "./draw.js";
import { draw_minimap, update_minimap_visible_rect } from "./minimap.js";

export { zoom_around, zoom_into_box, zoom_towards_box, zoom_aligned };


const zooming = {qz: {x: 1, y: 1, a: 1}, timeout: undefined};

// Zoom the current view into the area defined by the given box, with a border
// marking the fraction of zoom-out (to see a bit the surroundings).
function zoom_into_box(box, border=0.10) {
    tooltip.style.display = "none";
    if (view.drawer.type === "rect") {
        const [x, y, w, h] = box;
        view.tl.x = x - border * w;
        view.tl.y = y - border * h;
        view.zoom.x = div_tree.offsetWidth / (w * (1 + 2 * border));
        view.zoom.y = div_tree.offsetHeight / (h * (1 + 2 * border));
    }
    else if (view.drawer.type === "circ") {
        const [r, a, dr, da] = box;
        const points = [[r, a], [r, a+da], [r+dr, a], [r+dr, a+da]];
        const xs = points.map(([r, a]) => r * Math.cos(a)),
              ys = points.map(([r, a]) => r * Math.sin(a));
        const [x, y] = [Math.min(...xs), Math.min(...ys)];
        const [w, h] = [Math.max(...xs) - x, Math.max(...ys) - y];
        const [zx, zy] = [div_tree.offsetWidth / w, div_tree.offsetHeight / h];
        if (zx < zy) {
            view.tl.x = x - border * w;
            view.zoom.x = view.zoom.y = zx / (1 + 2 * border);
            view.tl.y = y - (div_tree.offsetHeight / zx - h) / 2 - border * h;
        }
        else {
            view.tl.y = y - border * h;
            view.zoom.x = view.zoom.y = zy / (1 + 2 * border);
            view.tl.x = x - (div_tree.offsetWidth / zy - w) / 2 - border * w;
        }
    }
    update();
}

window.zoom_into_box = zoom_into_box;  // exposed so it can be called in onclick


// Zoom maintaining the given point on the screen.
function zoom_around(point, deltaY, do_zoom={x:true, y:true}, qz=undefined) {
    tooltip.style.display = "none";

    if (!qz) { // quotient zoom (how much to change the zoom) not given?
        const factor = Math.exp(-deltaY/1000);
        qz = {x: factor, y: factor};  // zoom change (quotient)
    }

    if (view.drawer.type === "rect") {
        zoom_xy(point, qz, do_zoom);
    }
    else if (view.drawer.type === "circ") {
        if (do_zoom.x) {
            do_zoom.y = true;  // both dimensions zoom together in circular
            zoom_xy(point, qz, do_zoom);
        }
        else if (do_zoom.y) {
            zoom_angular(point, qz);
        }
    }
}


// Zoom around given point changing the x and y zoom by a factor qz.x and qz.y.
function zoom_xy(point, qz, do_zoom) {
    if (do_zoom.x) {
        const zoom_new = qz.x * view.zoom.x;
        view.tl.x += (1 / view.zoom.x - 1 / zoom_new) * point.x;
        view.zoom.x = zoom_new;
        zooming.qz.x *= qz.x;
    }

    if (do_zoom.y) {
        const zoom_new = qz.y * view.zoom.y;
        view.tl.y += (1 / view.zoom.y - 1 / zoom_new) * point.y;
        view.zoom.y = zoom_new;
        zooming.qz.y *= qz.y;
    }

    if (do_zoom.x || do_zoom.y)
        smooth_zoom(point);
}


// Zoom (around given point and by a factor qz.y) by changing the angular limits.
function zoom_angular(point, qz) {
    const x = view.tl.x + point.x / view.zoom.x,
          y = view.tl.y + point.y / view.zoom.y;
    const angle = Math.atan2(y, x) * 180 / Math.PI;

    view.angle.min = angle + qz.y * (view.angle.min - angle);
    view.angle.max = angle + qz.y * (view.angle.max - angle);

    if (zooming.timeout)
        window.clearTimeout(zooming.timeout);

    zooming.timeout = window.setTimeout(() => {
        zooming.timeout = undefined;
        draw_minimap();
        update();
    }, 50);  // 50 ms until we actually update (if not cancelled before!)
}


function zoom_aligned(point, zoom_in) {
    const x0 = div_tree.offsetWidth * view.aligned.pos / 100;
    point.x -= x0;
    const qz = { a: 1 + (zoom_in ? view.zoom.delta.in * 0.5
                                 : view.zoom.delta.out * 0.5) };
    let zoom_new = qz.a * view.zoom.a;

    if (view.aligned.adjust_zoom) {
        // min
        zoom_new = Math.max(zoom_new, 1);
        // max
        zoom_new = view.aligned.max_zoom ?
            Math.min(view.aligned.max_zoom, zoom_new) : zoom_new;
    }

    view.aligned.x += (1 / view.zoom.a - 1 / zoom_new) * point.x;
    view.zoom.a = zoom_new;
    zooming.qz.a *= qz.a;

    smooth_zoom_aligned(point)
}


// Zoom adaptatively so the given box tends to occupy a fraction of the screen.
function zoom_towards_box(box, point, deltaY, do_zoom) {
    tooltip.style.display = "none";

    const [dx, dy] = [box[2], box[3]];
    const dist = deltaY / 1000;  // distance moved, in convenient units

    // Screen size in terms of dx, dy (how many times bigger it is).
    const ssx = div_tree.offsetWidth  / (dx * view.zoom.x),
          ssy = div_tree.offsetHeight / (dy * view.zoom.y);

    const qz = (dist < 0) ?  // zoom in : zoom out
          {x: Math.min(1.5,             sigmoid(-dist, 0.80 * ssx)),    // 80%
           y: Math.min(1.5,             sigmoid(-dist, 0.80 * ssy))} :  // 80%
          {x: Math.max(0.7, Math.min(1, sigmoid( dist, 0.10 * ssx))),   // 10%
           y: Math.max(0.7, Math.min(1, sigmoid( dist, 0.01 * ssy)))};  //  1%

    zoom_xy(point, qz, do_zoom);
}

function sigmoid(x, lim) {  // helper function: s(0) = 1, and s(inf) = lim
    const a = Math.atan(x) / (Math.PI / 2);  // a goes between 0 and 1
    return 1 + a * (lim - 1);
}


function smooth_zoom_aligned(point) {
    if (zooming.timeout)
        window.clearTimeout(zooming.timeout);

    const toTransform = Array.from(div_aligned.children[0].children);
    toTransform.push(div_aligned.children[1].children[0])  // pixi canvas

    zooming.timeout = window.setTimeout(() => {
        zooming.qz.x = zooming.qz.y = zooming.qz.a = 1;
        zooming.timeout = undefined;
        draw_aligned();
    }, 50);  // 50 ms until we actually update (if not cancelled before!)
}


// Zoom by scaling the svg, and really update it only after a timeout.
function smooth_zoom(point) {
    if (zooming.timeout)
        window.clearTimeout(zooming.timeout);

    Array.from(div_tree.children[0].children).forEach(g =>
        g.setAttribute("transform",
            `scale(${zooming.qz.x}, ${zooming.qz.y}) ` +
            `translate(${(1 / zooming.qz.x - 1) * point.x}
                    ${(1 / zooming.qz.y - 1) * point.y})`));

    if (view.minimap.show)
        update_minimap_visible_rect();

    zooming.timeout = window.setTimeout(() => {
        zooming.qz.x = zooming.qz.y = zooming.qz.a = 1;
        zooming.timeout = undefined;
        update();
    }, 50);  // 50 ms until we actually update (if not cancelled before!)
}
