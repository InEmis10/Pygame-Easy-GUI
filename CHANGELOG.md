# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), versions : [SemVer](https://semver.org/lang/fr/).

## [1.0.0] - 2026-10-30

Première version stable.

### Ajouté
- `TimeService.Delay(Seconds, Callback, *Args)` et `TimeService.Every(Seconds, Callback, *Args)`, qui renvoient un `Timer` (`Cancel()`, `Active`).
  Avancent avec `ScreenGui.Update` / `Application` ; la boucle d'`Application` se réveille à l'échéance du prochain timer.
- Marqueur `py.typed` : les annotations de type sont visibles par les IDE et mypy dans les projets qui utilisent la lib.
- Métadonnées du package (URLs, mots-clés, classifiers) et ce changelog.

### Modifié
- Fichiers renommés en PascalCase : `datatypes/Color3.py`, `Udim.py`, `Vector2.py`, `Sequence.py`, `IntValue.py`,
  `core/mixins/AttributeMixin.py`, `utils/ArgumentVerifier.py`. L'API publique (`from pygame_easy_gui import ...`) ne change pas.
- La version n'est plus écrite qu'à un endroit : `__version__` dans `src/pygame_easy_gui/__init__.py`.
- `init.sh` utilise `python3 -m venv` quand uv est absent, recrée un `.venv` cassé et installe pytest.
- Les tests trouvent la lib via `pythonpath` de pytest (plus de `sys.path` modifié dans `conftest.py`).

### Retiré
- `InputObject`, `UserInputType`, `UserInputStates` (préparation d'un UserInputService, non utilisés) : prévus pour une version suivante.
- `utils/Timer.py` (ébauche vide, remplacée par `TimeService`).

### Corrigé
- `examples/game_loop_demo.py` : `NameError` sur `Index` dans la liste des niveaux.

## [0.1.0]

Version de développement.
