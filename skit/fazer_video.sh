#!/bin/bash
# Do roteiro ao vídeo: EPISODIO=episodios/02.json bash skit/fazer_video.sh
# Etapas: vozes -> linha do tempo/legendas -> camadas das imagens (se faltar) -> render -> mixagem
set -e
cd "$(dirname "$0")"
export EPISODIO=${EPISODIO:-episodio.json}
PY=${PY:-.venv/bin/python}
mkdir -p audio out prep
echo "== episódio: $EPISODIO"
$PY gerar_vozes.py            # gera todas as falas (ou: $PY gerar_vozes.py 3 7 pra refazer só algumas)
$PY montar_audio.py           # pausas, efeito do PC, estúdio, tempos das palavras -> timeline.json
# camadas das imagens: só prepara os planos que ainda não têm prep/
FALTA=$($PY -c "import json,os;c=json.load(open('cena.json'))['shots'];print(' '.join(s for s in c if not os.path.exists(f'prep/{s}_full.png')))")
[ -n "$FALTA" ] && $PY preparar.py $FALTA
PY=$PY N=${N:-4} ./render_tudo.sh
