export { draw_alignment }

//Aliases
const Application = PIXI.Application;
const loader = PIXI.loader;
const textureCache = PIXI.utils.TextureCache;
const resources = PIXI.loader.resources;
const Sprite = PIXI.Sprite;
const ParticleContainer = PIXI.particles.ParticleContainer;

const app_options = {
    width: div_aligned.innerWidth,
    height: div_aligned.innerHeight,
    transparent: true,
    resolution: 1,
};
    

function draw_msa(g, items, seq_type="aa", draw_text=true, tl, zoom) {
    // Create PIXI app
    const app = new Application(app_options);
    // High-performance container
    const container = new ParticleContainer();
    
    // Load texture atlas
    const texture_atlas = `../images/${seq_type}_${draw_text ? text : notext}.json`;
    loader.add(texture_atlas)
          .load(draw);

    function draw() {
        const textures = PIXI.loader.resources[texture_atlas].textures;
        items.forEach(item => {
            const [ , box, sequence, , ] = item;
            draw_sequence(container, textures, box, sequence, tl, zoom);
        });
        app.stage.addChild(container);
    }
}


function draw_sequence(container, textures, box, sequence, tl, zoom) {
    const [zx, zy] = [zoom.x, zoom.y];  // shortcut
    const [x0, y, total_w, h] = box;
    let x = x0;
    const w = total_w / sequence.length;

    sequence.forEach(pos => {
        const sprite = new Sprite(textures[pos + ".png"]);
        // Set sprite's x, y coordinates and widht, height
        sprite.position.set(zx * (x - tl.x), zy * (y - tl.y));
        sprite.size.set(w * zx, h * zy);

        // Add sequence position sprite to container
        container.addChild(sprite);

        x += w; // Increase to draw positions sequentially
    });
}
