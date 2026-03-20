#!/bin/bash

# Icon generation script for Conduit PWA
# Requires ImageMagick or GraphicsMagick

set -e

SIZES=(72 96 128 144 152 192 384 512)
SOURCE="icon-source.svg"

echo "Generating PWA icons from $SOURCE..."

# Check if convert command exists
if ! command -v convert &> /dev/null; then
    echo "Error: ImageMagick 'convert' command not found"
    echo "Please install ImageMagick: https://imagemagick.org/script/download.php"
    echo ""
    echo "Alternative: Use the Node.js script (generate-icons.js) or online tools"
    exit 1
fi

# Generate each icon size
for size in "${SIZES[@]}"; do
    output="icon-${size}x${size}.png"
    echo "  Generating $output..."
    convert "$SOURCE" -resize "${size}x${size}" -quality 100 "$output"
done

echo ""
echo "✓ All icons generated successfully!"
echo ""
echo "Generated icons:"
ls -lh icon-*.png

# Generate favicon
echo ""
echo "Generating favicon.ico..."
convert "$SOURCE" -define icon:auto-resize=16,32,48 ../favicon.ico
echo "✓ Favicon generated: ../favicon.ico"
