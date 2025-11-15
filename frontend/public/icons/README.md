# Conduit PWA Icons

This directory contains the app icons for the Conduit Progressive Web App.

## Source Icon

The `icon-source.svg` file is the source vector graphic that should be used to generate all PNG icons in the required sizes.

## Required Icon Sizes

The PWA requires icons in the following sizes (as configured in `vite.config.ts`):

- 72x72
- 96x96
- 128x128
- 144x144
- 152x152
- 192x192
- 384x384
- 512x512

## Generating Icons

### Option 1: Using ImageMagick (Recommended)

If you have ImageMagick installed, run the generation script:

```bash
cd frontend/public/icons
./generate-icons.sh
```

### Option 2: Manual Generation

You can use online tools or design software:

1. **Online Tools:**
   - [realfavicongenerator.net](https://realfavicongenerator.net)
   - [favicon.io](https://favicon.io)
   - Upload `icon-source.svg` and download the generated icons

2. **Design Software:**
   - Open `icon-source.svg` in Figma, Sketch, or Adobe Illustrator
   - Export to PNG at each required size
   - Name files as `icon-{size}x{size}.png` (e.g., `icon-192x192.png`)

### Option 3: Using sharp (Node.js)

Install sharp and run the Node.js script:

```bash
npm install -g sharp-cli
cd frontend/public/icons
./generate-icons.js
```

## Icon Design

The Conduit icon represents:
- **Green gradient**: The brand color (#5cb85c)
- **Pipe/conduit symbol**: Represents the flow of knowledge and ideas
- **Branching structure**: Shows how content flows from authors to multiple readers
- **"C" letter**: Brand initial for easy recognition

## Customization

To customize the icon:
1. Edit `icon-source.svg` in your preferred vector editor
2. Keep the 512x512 viewBox for best results
3. Maintain good contrast for small sizes (72x72)
4. Test the icon at different sizes before deploying

## Favicon

Don't forget to also generate `favicon.ico` for legacy browser support:

```bash
# Using ImageMagick
convert icon-source.svg -define icon:auto-resize=16,32,48 ../favicon.ico
```
