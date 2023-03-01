import { view } from "./gui.js";
import { cartesian_shifted } from "./draw.js";

export { draw_pixi, clear_pixi, apps };


// Globals
const apps = {};  // pixi "applications" per container
let app;
let textures;
let textures_loaded = false;

// Codes for amino acids, nucleotides (DNA and RNA), and gaps.
// See for example https://en.wikipedia.org/wiki/FASTA_format#Sequence_representation
const aa = [
    'A', 'R', 'N',
    'D', 'C', 'Q',
    'E', 'G', 'H',
    'I', 'L', 'K',
    'M', 'F', 'P',
    'S', 'T', 'W',
    'Y', 'V', 'B',
    'Z', 'X', '.',
    '-'
];


// Load texture atlas
PIXI.Loader.shared
    .add(aa.map(a => ({name: `aa_notext_${a}`, url: `images/aa_notext/${a}.png`})))
    .add(aa.map(a => ({name: `aa_text_${a}`,   url: `images/aa_text/${a}.png`})))
    .add("block", "images/block.png")
    .load(() => {
        const resources = PIXI.Loader.shared.resources;  // shortcut

        const textures_notext = {};
        const textures_text = {};
        for (const a of aa) {
            textures_notext[a] = resources[`aa_notext_${a}`].texture;
            textures_text[a] = resources[`aa_text_${a}`].texture;
        }

        textures = {
            aa_notext: textures_notext,
            aa_text: textures_text,
            shapes: {
                block: resources.block.texture,
            }
        }

        textures_loaded = true;
    });

function clear_pixi(container) {
    // Remove all items from stage
    app = apps[container.id];

    if (app)
        app.stage.children = [];
}

function draw_pixi(container, items, tl, zoom) {
    app = apps[container.id] = apps[container.id] || new PIXI.Application({
        transparent: true,
        resolution: 1,
    });

    // Resize canvas based on container
    app.renderer.resize(container.clientWidth, container.clientHeight);

    // Remove all items from stage
    app.stage.children = [];

    if (textures_loaded && items.length > 0)
        draw(items, tl, zoom);

    return app.view;
}


function draw(items, tl, zoom) {
    items.forEach(seq => {
        const [ el, box ] = [ seq[0], seq[1] ];
        const type = el.split("-")[1]
        const [ zx, zy ] = [ zoom.x, zoom.y ];
        if (["aa_notext", "aa_text", "nt_notext", "nt_text"].includes(type))
            draw_msa(seq[2], type, box, tl, zx, zy);
        else
            draw_shape(type, box, tl, zx, zy)
    })
}


function addSprite(sprite, box, tl, zx, zy, tooltip) {
    const [ x, y, dx, dy ] = box;

    let [ sx, sy ] = [ x, y ];
    const [ sw, sh ] = [ dx * zx, dy * zy ];

    if (view.drawer.type === "rect")
        [ sx, sy ] = [ (sx - tl.x) * zx, (sy - tl.y) * zy ];
    else {
        ({x:sx, y:sy} = cartesian_shifted(sx + dx/2, sy + dy/2, tl, zx));
        sprite.anchor.set(0.5, 0.5);
        sprite.rotation = y + dy/2;
    }
    sprite.x = sx;
    sprite.y = sy;
    sprite.width = sw;
    sprite.height = sh;

    if (tooltip) {
        sprite.accessibleTitle = tooltip;
    }

    // Add to stage
    app.stage.addChild(sprite);
}


function draw_msa(sequence, type, box, tl, zx, zy) {
    const MIN_MSA_POSWIDTH = 12;

    const [ x0, y, width, posh ] = box;

    const posw = width / sequence.length;

    if (view.aligned.adjust_zoom)
        view.aligned.max_zoom = MIN_MSA_POSWIDTH / posw;
    else
        view.aligned.max_zoom = undefined;

    sequence.split("").forEach((s, i) => {
        if (s != "-") {
            const sprite = new PIXI.Sprite(textures[type][s])
            const x = x0 + i * posw;
            const tooltip = `Residue: ${s}\nPosition: ${i}`
            addSprite(sprite, [x, y, posw, posh], tl, zx, zy, tooltip);
        }
    })
}


function draw_shape(shape, box, tl, zx, zy) {
    const sprite = new PIXI.Sprite(textures.shapes[shape])
    addSprite(sprite, box, tl, zx, zy);
}
