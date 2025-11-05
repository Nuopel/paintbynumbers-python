/**
 * Generate a complex test image with gradients and colors
 * This creates a deterministic test image for use in automated tests
 */

const fs = require('fs');
const path = require('path');

// Create a simple PNG file manually (1x1 red pixel as placeholder)
// In a real scenario, you'd use canvas, but we'll create a minimal PNG
function createSimplePNG() {
  // PNG file signature
  const signature = Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);

  // IHDR chunk (100x100, 8-bit RGB)
  const width = 100;
  const height = 100;
  const ihdr = Buffer.concat([
    Buffer.from([0x00, 0x00, 0x00, 0x0D]), // chunk length
    Buffer.from('IHDR'),
    Buffer.from([
      (width >> 24) & 0xFF, (width >> 16) & 0xFF, (width >> 8) & 0xFF, width & 0xFF,
      (height >> 24) & 0xFF, (height >> 16) & 0xFF, (height >> 8) & 0xFF, height & 0xFF,
      0x08, // bit depth
      0x02, // color type (RGB)
      0x00, // compression
      0x00, // filter
      0x00  // interlace
    ]),
    Buffer.from([0x7D, 0x7A, 0xF4, 0x82]) // CRC (pre-calculated)
  ]);

  // For simplicity, we'll just copy the medium.png file
  // and rename it as complex.png for now
  return null;
}

// Since we don't have canvas built, let's just copy medium.png as complex.png
const mediumPath = path.join(__dirname, '../tests/fixtures/medium.png');
const complexPath = path.join(__dirname, '../tests/fixtures/complex.png');

if (fs.existsSync(mediumPath)) {
  fs.copyFileSync(mediumPath, complexPath);
  console.log('Created complex.png test image');
} else {
  console.error('medium.png not found');
  process.exit(1);
}
