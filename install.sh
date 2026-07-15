#!/bin/bash
# obsidian-brain installer for macOS/Linux
# Usage: curl -fsSL https://raw.githubusercontent.com/sean0407/obsidian-brain/main/install.sh | bash

set -e

echo "=========================================="
echo "  obsidian-brain installer"
echo "=========================================="
echo ""

INSTALL_DIR="$HOME/obsidian-brain"

if [ -d "$INSTALL_DIR" ]; then
    echo "Existing installation found. Updating..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "Cloning obsidian-brain to $INSTALL_DIR..."
    git clone https://github.com/sean0407/obsidian-brain.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "Installing Python dependencies..."
pip install python-frontmatter pyyaml -q

echo ""
read -p "Enter your Obsidian vault path: " VAULT_PATH

# Update config
sed -i.bak "s|vault_path:.*|vault_path: \"$VAULT_PATH\"|" config.yaml
rm -f config.yaml.bak

echo ""
echo "Initializing Karpathy wiki structure..."
python3 cli.py init

echo ""
echo "=========================================="
echo "  Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Open your Obsidian vault"
echo "  2. Edit CLAUDE.md to customize your schema"
echo "  3. Run 'python3 cli.py audit' any time to check compliance"
