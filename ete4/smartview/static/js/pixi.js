// Functions related to drawing raster graphics with pixi.

import { Application, Sprite, Assets, Container, Point }
    from '../external/pixi.min.mjs';

import { view } from "./gui.js";
import { tree2rect, tree2circ, pad } from "./draw.js";

export { init_pixi, create_seq_pixi, clear_pixi };


async function init_pixi() {
    // The application creates a WebGL renderer, or canvas if not possible.
    view.pixi_app_tree = new Application();
    view.pixi_app_aligned = new Application();

    await view.pixi_app_tree.init({  // wait for the renderer to be available
        backgroundAlpha: 0,  // transparent background so we see the tree
        resizeTo: div_tree,  // resize with div_tree
    });

    // If we don't make div_aligned visible, it won't resize properly
   div_aligned.style.display = "flex";

    await view.pixi_app_aligned.init({  // wait for the renderer to be available
        backgroundAlpha: 0,  // transparent background so we see the tree
        resizeTo: div_aligned,  // resize with div_aligned
    });

    div_aligned.style.display = "none";  // now we can make it invisible

    // We set the style of the pixi canvas so it is superimposed to the div.
    for (const app of [view.pixi_app_tree, view.pixi_app_aligned]) {
        const style = app.canvas.style;
        style.position = "absolute";
        style.top = "0";
        style.left = "0";
        style.zIndex = "1";  // make sure we are above the svg panel
        style.pointerEvents = "none";
    }

    // Insert canvases in the dom.
    div_tree.appendChild(view.pixi_app_tree.canvas);
    div_aligned.appendChild(view.pixi_app_aligned.canvas);

    view.pixi_sheet = await Assets.load('/static/images/spritesheet.json');
}


// Return a pixi container with an image for the sequence in box.
function create_seq_pixi(box, seq, seqtype, draw_text, fs_max, marks,
                         tl, zx, zy, style, wmax) {
    const [x0, y0, dx0, dy0] = box;
    const dx = dx0 / seq.length;
    const [y, dy] = pad(y0, dy0, view.array.padding);

    const container = new Container();

    if (view.shape === "rectangular") {
        const imin = Math.max(0, Math.floor((tl.x - x0) / dx)),
              imax = Math.min(seq.length, (wmax / zx + tl.x - x0) / dx);


        // Position and size of the sequence.
        const p = tree2rect([x0, y0], tl, zx, zy);
        container.x = p.x;
        container.y = p.y;
        container.setSize(zx * dx0, zy * dy);

        // Fill the container with sprites for the characters between imin and imax.
        for (let i = imin, x = imin * dx; i < imax; i++, x+=dx) {
            // Names starting with space identify sprites with only colors
            // (" A" is like "A", but no text, just the color for A).
            const name = (draw_text ? "" : " ") + seq[i].toUpperCase();
            const sprite = new Sprite(view.pixi_sheet.textures[name]);

            sprite.x = zx * x;
            sprite.setSize(zx * dx, zy * dy);
            container.addChild(sprite);

            if (marks.includes(i)) {
                const sprite_mark = new Sprite(view.pixi_sheet.textures["mark"]);
                sprite_mark.x = zx * x;
                sprite_mark.setSize(zx * dx, zy * dy);
                container.addChild(sprite_mark);
            }
        }
    }
    else {
        // From tree coordinates to pixels in screen.
        const p1 = tree2circ([x0, y], tl, zx),
              p2 = tree2circ([x0, y + dy], tl, zx),
              center = tree2circ([x0, y + dy/2], tl, zx);

        const h = dist(p1, p2);  // height

        // Position and size of the sequence.
        container.x = p1.x;
        container.y = p1.y;
        container.setSize(dx0, h);
        container.pivot = new Point(0, container.height / 2);
        container.rotation = Math.atan2(zy * tl.y + center.y,
                                        zx * tl.x + center.x);

        // Fill the container with sprites for the characters between imin and imax.
        for (let i = 0, x = 0; i < seq.length; i++, x+=zx*dx) {
            // Names starting with space identify sprites with only colors
            // (" A" is like "A", but no text, just the color for A).
            const name = (draw_text ? "" : " ") + seq[i].toUpperCase();
            const sprite = new Sprite(view.pixi_sheet.textures[name]);

            sprite.x = x;
            sprite.setSize(zx * dx, h);
            container.addChild(sprite);

            if (marks.includes(i)) {
                const sprite_mark = new Sprite(view.pixi_sheet.textures["mark"]);
                sprite_mark.x = zx * x;
                sprite_mark.setSize(zx * dx, h);
                container.addChild(sprite_mark);
            }
        }
    }

    return container;
}

function dist(p1, p2) {
    const dx = p2.x - p1.x,
          dy = p2.y - p1.y;
    return Math.sqrt(dx*dx + dy*dy);
}


// Clear the canvas by removing all the sprites.
function clear_pixi() {
    // NOTE: After heavy testing with/without this -> use to avoid memory leaks.
    view.pixi_app_tree.stage.children.forEach(c => c.destroy({children: true}));
    view.pixi_app_aligned.stage.children.forEach(c => c.destroy({children: true}));

    // The normal removal of everything.
    view.pixi_app_tree.stage.removeChildren();
    view.pixi_app_aligned.stage.removeChildren();
}
