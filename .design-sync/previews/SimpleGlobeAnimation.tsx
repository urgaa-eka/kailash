import { SimpleGlobeAnimation } from 'frontend';

// A page-level hero decoration. It anchors itself against a full-height page
// container and is centred on a point above its own box, so standalone its top
// edge sits outside any frame — a preview stage cannot recover that without
// re-laying-out the component, which would stop being the shipped component.
// The card gives it a hero-sized viewport and captures one frame; it is an
// animation, and it is cropped at the top by construction.
export const Default = () => <SimpleGlobeAnimation />;
