// Mock canvas for jsdom
const { createCanvas } = require('canvas');

Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
  value: function(contextType) {
    if (contextType === '2d') {
      const canvas = createCanvas(this.width || 400, this.height || 400);
      return canvas.getContext('2d');
    }
    return null;
  }
});
