# Autonomy Installation Guide

Autonomy requires Python 3.8 or newer. The recommended method is using `pipx`.

```bash
# Install with pipx
pipx install autonomy

# Or install with pip
pip install autonomy
```

To work from source clone the repository and install in editable mode:

```bash
git clone https://github.com/mehulbhardwaj/autonomy.git
cd autonomy
pip install -e .[dev]
```

Run `autonomy --version` to verify the installation.
