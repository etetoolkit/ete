export { draw_alignment }

//Aliases
const Application = PIXI.Application;
const loader = PIXI.loader;
const textureCache = PIXI.utils.TextureCache;
const resources = PIXI.loader.resources;
const Sprite = PIXI.Sprite;

const app_options = {
    width: div_aligned.innerWidth,
    height: div_aligned.innerHeight,
    transparent: true,
    resolution: 1,
};
    

function draw_msa(items, seq_type="aa", draw_text=true) {
    const app = new Application(app_options);
    
    // Load texture atlas
    loader.add(`../images/${seq_type}_${draw_text ? text : notext}.json`)
          .load(setup);


}

function draw_alignment(box, sequence, sequence_type="aa", draw_text=true) {
}
