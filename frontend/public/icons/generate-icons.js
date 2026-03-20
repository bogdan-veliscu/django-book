#!/usr/bin/env node

/**
 * Icon generation script for Conduit PWA
 * Requires: npm install -g sharp-cli
 * or: npm install sharp (in project)
 */

const fs = require('fs');
const path = require('path');

const SIZES = [72, 96, 128, 144, 152, 192, 384, 512];
const SOURCE = 'icon-source.svg';

async function generateIcons() {
  try {
    // Try to require sharp
    const sharp = require('sharp');

    console.log(`Generating PWA icons from ${SOURCE}...`);

    if (!fs.existsSync(SOURCE)) {
      console.error(`Error: ${SOURCE} not found`);
      process.exit(1);
    }

    // Generate each icon size
    for (const size of SIZES) {
      const output = `icon-${size}x${size}.png`;
      console.log(`  Generating ${output}...`);

      await sharp(SOURCE)
        .resize(size, size)
        .png({ quality: 100 })
        .toFile(output);
    }

    console.log('\n✓ All icons generated successfully!\n');

    // List generated files
    const files = fs.readdirSync('.')
      .filter(f => f.startsWith('icon-') && f.endsWith('.png'))
      .map(f => {
        const stats = fs.statSync(f);
        return `  ${f} (${(stats.size / 1024).toFixed(2)} KB)`;
      });

    console.log('Generated icons:');
    console.log(files.join('\n'));

  } catch (error) {
    if (error.code === 'MODULE_NOT_FOUND') {
      console.error('\nError: sharp module not found');
      console.error('\nPlease install sharp:');
      console.error('  npm install sharp');
      console.error('  or: npm install -g sharp-cli\n');
      console.error('Alternative: Use the Bash script (generate-icons.sh) or online tools');
    } else {
      console.error('\nError generating icons:', error.message);
    }
    process.exit(1);
  }
}

generateIcons();
