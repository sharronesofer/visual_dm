// scripts/generate_placeholder_assets.js
// Generates placeholder PNGs for overlays and sprites using the 'canvas' package
// Usage: npm install canvas && node scripts/generate_placeholder_assets.js

const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');

const assets = [
    { file: 'assets/overlays/overlay_dirty_01.png', color: '#888888', label: 'DIRTY', textColor: '#111' },
    { file: 'assets/overlays/overlay_dingy_01.png', color: '#cccccc', label: 'DINGY', textColor: '#111' },
    { file: 'assets/overlays/overlay_chipped_01.png', color: '#deb887', label: 'CHIPPED', textColor: '#111' },
    { file: 'assets/overlays/overlay_cracked_01.png', color: '#444444', label: 'CRACKED', textColor: '#fff' },
    { file: 'assets/sprites/sprite_house_01.png', color: '#87ceeb', label: 'HOUSE', textColor: '#111' },
    { file: 'assets/sprites/sprite_factory_01.png', color: '#ffa500', label: 'FACTORY', textColor: '#111' },
];

const size = 128;

for (const asset of assets) {
    const canvas = createCanvas(size, size);
    const ctx = canvas.getContext('2d');

    // Background
    ctx.fillStyle = asset.color;
    ctx.fillRect(0, 0, size, size);

    // Label
    ctx.font = 'bold 24px sans-serif';
    ctx.fillStyle = asset.textColor;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(asset.label, size / 2, size / 2);

    // Ensure directory exists
    fs.mkdirSync(path.dirname(asset.file), { recursive: true });
    // Write PNG
    const out = fs.createWriteStream(asset.file);
    const stream = canvas.createPNGStream();
    stream.pipe(out);
    out.on('finish', () => console.log('Created', asset.file));
} 