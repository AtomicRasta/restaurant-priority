#!/bin/bash
# Setup automation Chrome profile for restaurant checking

PROFILE_DIR="$HOME/.openclaw/chrome-automation"

echo "Setting up automation Chrome profile..."
echo ""
echo "This will:"
echo "1. Create a dedicated Chrome profile at: $PROFILE_DIR"
echo "2. Open Chrome so you can log into Resy, OpenTable, and Tock"
echo "3. Save those sessions for automated checking"
echo ""
echo "Press Enter to continue..."
read

mkdir -p "$PROFILE_DIR"

echo ""
echo "Opening Chrome with automation profile..."
echo "Please log into:"
echo "  • Resy.com"
echo "  • OpenTable.com"  
echo "  • Tock.com (if needed)"
echo ""
echo "Once logged in, close Chrome and press Enter here..."

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  --no-default-browser-check \
  https://resy.com https://www.opentable.com &

wait

echo ""
echo "✅ Setup complete!"
echo ""
echo "This profile is now ready for automated checking."
echo "Run: python3 restaurants/auto_check.py"
