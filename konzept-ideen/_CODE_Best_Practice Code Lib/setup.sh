#!/usr/bin/env bash
set -e

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt || true

# Try to install small spaCy models (ignore failure if offline)
python - <<'PY'
try:
    import spacy, sys, subprocess
    for m in ["de_core_news_sm", "en_core_web_sm"]:
        try:
            spacy.load(m)
        except Exception:
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", m])
            except Exception:
                pass
except Exception:
    pass
PY

echo "✔ Environment ready. Activate with: source .venv/bin/activate"
