#!/usr/bin/env sh
# Crée l'environnement virtuel .venv et y installe la lib en mode éditable :
# les modifications dans src/ sont prises en compte sans réinstaller.
#
# Le Python vient de uv (rangé dans ~/.local/share/uv) et non de /usr/bin : le même
# .venv fonctionne ainsi dans le terminal et dans PyCharm en Flatpak, dont le bac à
# sable a son propre /usr/bin/python3.
set -eu
cd "$(dirname "$0")"

UV="$(command -v uv || echo "$HOME/.local/bin/uv")"
if [ ! -x "$UV" ]; then
    echo "uv introuvable : curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

[ -d .venv ] || "$UV" venv --python 3.14 --managed-python .venv
"$UV" pip install --python .venv/bin/python -e .

echo "Prêt. Lancer la démo : .venv/bin/python examples/demo.py"
