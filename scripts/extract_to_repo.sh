#!/bin/bash
set -e

# Extract autonomy-mcp to standalone repository
# Usage: ./scripts/extract_to_repo.sh [target_directory]

TARGET_DIR=${1:-"../autonomy"}
AUTONOMY_MCP_DIR="autonomy-mcp"

echo "🚀 Extracting Autonomy MCP to standalone repository..."

# Check if autonomy-mcp directory exists
if [ ! -d "$AUTONOMY_MCP_DIR" ]; then
    echo "❌ Error: $AUTONOMY_MCP_DIR directory not found"
    exit 1
fi

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy all files from autonomy-mcp to target directory
echo "📁 Copying files to $TARGET_DIR..."
cp -r "$AUTONOMY_MCP_DIR"/* "$TARGET_DIR/"

# Copy root files that should be in the standalone repo
echo "📄 Copying project files..."
cp "$AUTONOMY_MCP_DIR/README.md" "$TARGET_DIR/"
cp "$AUTONOMY_MCP_DIR/LICENSE" "$TARGET_DIR/"
cp "$AUTONOMY_MCP_DIR/CHANGELOG.md" "$TARGET_DIR/"
cp "$AUTONOMY_MCP_DIR/pyproject.toml" "$TARGET_DIR/"

echo "✅ Extraction complete!"
echo ""
echo "📋 Next steps:"
echo "1. cd $TARGET_DIR"
echo "2. git init (if new repository)"
echo "3. git remote add origin https://github.com/mehulbhardwaj/autonomy.git"
echo "4. git add ."
echo "5. git commit -m 'Initial commit: Autonomy MCP v0.1.0'"
echo "6. git push -u origin main"
echo ""
echo "🔧 Development setup:"
echo "1. pip install -e ."
echo "2. pip install -e .[dev]"  
echo "3. pytest"
echo ""
echo "📦 Publishing to PyPI:"
echo "1. pip install build twine"
echo "2. python -m build"
echo "3. twine upload dist/*"
