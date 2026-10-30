#!/usr/bin/env sh
# Crée l'environnement virtuel .venv et y installe la lib en mode éditable (+ pytest) :
# les modifications dans src/ sont prises en compte sans réinstaller.
#
# Avec uv, le Python vient de uv (rangé dans ~/.local/share/uv) et non de /usr/bin : le même
# .venv fonctionne ainsi dans le terminal et dans PyCharm en Flatpak, dont le bac à
# sable a son propre /usr/bin/python3. Sans uv, on retombe sur python3 -m venv.
set -eu
cd "$(dirname "$0")"

# Un .venv dont le Python a disparu (ex: uv désinstallé) est recréé
if [ -d .venv ] && ! .venv/bin/python -c "" 2>/dev/null; then
    echo ".venv cassé : recréation"
    rm -rf .venv
fi

UV="$(command -v uv || echo "$HOME/.local/bin/uv")"
if [ -x "$UV" ]; then
    [ -d .venv ] || "$UV" venv --python 3.14 --managed-python .venv
    "$UV" pip install --python .venv/bin/python -e ".[dev]"
else
    echo "uv introuvable, utilisation de python3 -m venv (installer uv : curl -LsSf https://astral.sh/uv/install.sh | sh)"
    [ -d .venv ] || python3 -m venv .venv
    .venv/bin/python -m pip install -q -e ".[dev]"
fi

echo "Prêt. Tests : .venv/bin/python -m pytest | Démo : .venv/bin/python examples/demo.py"
