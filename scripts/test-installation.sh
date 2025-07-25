#!/bin/bash
set -e

echo "Testing Autonomy installation..."

# Test pipx installation (recommended)
pipx install autonomy
autonomy --help
autonomy next --help
autonomy plan --help

# Test pip installation
pip install autonomy
python -c "import src.core.platform; print('✅ Core imports work')"

autonomy --version
echo "✅ Installation test passed"
