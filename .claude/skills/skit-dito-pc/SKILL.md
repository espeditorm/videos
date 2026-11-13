---
name: skit-dito-pc
description: Cria episódios do formato de skit do Dito com o mascote Dito PC (computadorzinho retrô convencido que rouba a cena), do tema ao vídeo 1080x1920 pronto pro Reels. Use quando o Dito pedir um vídeo novo do formato, roteiro de skit com o PC, novas cenas/B-rolls desses personagens, vozes, ou ajustes em um episódio. Tudo vive em skit/ deste repositório.
---

# Skit Dito + Dito PC

Formato: o Dito (humano, low-poly 3D) conversa com o **Dito PC**, um computadorzinho retrô
creme com tela verde-água, que é **a piada**: convencido, inventa coisas, rouba a cena.
Cenário fixo: estufa-biblioteca noturna com cúpula de vidro. Vídeo vertical 1080x1920, 30 fps,
40–50 s, feito 100% em código a partir de imagens paradas (baseado no método "How I make my AI skits").

Tudo está em `skit/`. Leia `skit/episodio.json` (episódio 01, "Interrogatório") como modelo.

## Fluxo de um episódio novo

1. **Tema.** Ofereça 3–5 opções, cada uma com as 3 primeiras falas e "o que o Dito entrega".
   Temas do Dito: IA, tecnologia, design/UX, ética, clima. A entrega é sempre algo útil de verdade.
2. **Roteiro.** Proponha 2–3 *estruturas* diferentes (ex.: "flagra ao vivo", "interrogatório", "aula invertida")
   antes de escrever. Depois de escolhida, mande **só a lista de falas numeradas** (`01 PC: ...`): o Dito
   gosta de editar fala por fala. Aplique as edições dele exatamente; só ajuste pontuação pra voz.
3. **`skit/episodios/NN.json`** (copie a estrutura de `skit/episodio.json`). Por linha:
   - `quem`: `dito` | `pc` · `plano`: ver tabela abaixo · `legenda`: texto na tela
   - `fala`: texto falado quando difere da legenda (números por extenso, `Óscar`, etc.)
   - `pausa_antes`: segundos (padrão 0,18 mesma pessoa / 0,28 troca; 1,3 para "segundos depois")
   - `pc_expr`: `terno` (olhos grandes brilhantes), `404` (tela de erro), `aberto`; padrão `convencido`.
     Vale do começo da fala até a próxima.
   - `cards`: até 3 cards no céu do plano S6 (`linha`, `num`, `titulo`, `sub`). Use pra entrega.
4. **Vozes** → mande prévia de áudio ao Dito antes de renderizar (ele ouve e pede ajustes).
5. **Render** → confira quadros (rosto do PC visível, boca, cards, legendas) → mande o vídeo.
6. Commit + push na branch de trabalho. Vozes reais do Dito nunca vão pro git.

Comando único: `EPISODIO=episodios/02.json bash skit/fazer_video.sh`
(primeira vez na máquina: `bash skit/setup.sh`). Etapas soltas: `gerar_vozes.py [n ...]`,
`montar_audio.py`, `preparar.py [S..]`, `render.py frame <seg> <arquivo.jpg>` (testar 1 quadro), `render_tudo.sh`.
Em CPU: vozes ~1 min/fala, render ~5 min.

## Regras de roteiro (aprendidas)
- 40–50 s; uma fala a cada 2–2,5 s; falas de 1–8 palavras; cada fala é um corte.
- 1ª fala é gancho do PC (mentira/afirmação absurda). Fim retoma o começo ou escala a piada.
- A IA/PC é a piada: mostre a alucinação **acontecendo** em vez de explicar ("Erro 404", resposta que muda).
- Um momento sincero do PC (olhos `terno`) seguido de quebra seca ("Gostou?" / "Não.").
- Escreva com vírgulas, não pontos picotados. CTA é opcional (o Dito às vezes não quer).
- **Confira fatos citados** (lei, datas, números). Ex.: direito a advogado = art. 5º, **LXIII** (LXVIII é habeas corpus).

## Planos (imagens em `skit/stills/`, config em `skit/cena.json`)
| Plano | Imagem | Uso |
|---|---|---|
| S7 | estufa de longe | abertura (desce até a mesa) e fim — automático |
| S1 | plano aberto, os dois | 1ª fala, momentos grandes |
| S2 / S2b | Dito falando (b = mais fechado) | falas do Dito |
| S3 / S3b / S3c | PC falando, bracinho levantado (c = push-in forte) | falas do PC, punchline |
| S4 / S4b | Dito braços cruzados | reações secas |
| S5 / S5b | PC close baixo | momento sincero |
| S6 | de costas, céu estrelado | falas com cards |

B-rolls prontos em `skit/brolls/` (índice em `skit/brolls.md`). Para usar uma imagem nova como plano:
adicione em `cena.json` com `chars` (recorte), `dito_face` (`mouth` [x,y,largura,inclinação],
`eyes` [[x,y,rx,ry],...]) e/ou `pc_face` (`screen` [x0,y0,x1,y1], `eyes` [[x0,y0,x1,y1] x2]),
em pixels da imagem 944x1680. Ache as coordenadas recortando o rosto com grade (PIL) e confira
com sobreposição antes de renderizar. Rode `preparar.py <plano>`.

## Personagens e imagens
- Sheets: `skit/sheets/dito.jpg` (**só bigode, sem barba** — nunca use imagens com barba por fazer;
  as antigas estão em `sheets/antigos/`), `computador.jpg`, `computador_natal.jpg` (gorro de Natal).
- O PC é gerado com a **tela vazia e escura**; olhos/boca/"404" são desenhados em código (pixel verde).
- Prompts de imagem: comece com
  `Vertical 9:16 film still, same night greenhouse library, same low-poly faceted 3D animation style, same lighting and colours as the first reference image.`
  e termine com `Empty space in the top third. No text, no logos, no watermark.`
  Referências: plano aberto S1 + sheet do personagem. Para trocar só um detalhe, edite a imagem existente
  ("Keep EVERYTHING exactly the same ... Only this change: ...") pra manter o enquadramento.
- Canva gera ~6 imagens por vez e depois pede pausa (`quota_cooldown`); espere e repita.
  Não dá pra baixar do Canva por aqui: o Dito baixa e sobe no GitHub (Add file → Upload files, branch de trabalho).

## Voz e som
- Vozes fixas (sintéticas, no repo): `skit/vozes/dito_D.wav` (Dito, "voz D") e `pc_B.wav` (PC, "voz B"),
  clonadas pelo OmniVoice (motor do VoiceStudio). As duas passam pela mesma cadeia "estúdio" — o Dito
  rejeitou voz com som de "caixa"/sala diferente da do PC.
- `gerar_vozes.py` confere cada fala com Whisper e descarta tentativas erradas ou atropeladas; `SEMENTE=50` tira outras.
  Erros comuns: "IA" vira "Aí a"; palavras isoladas no início ("Um,") somem → reescreva ("Número um,").
- Referência de clonagem nunca pode ter pedaço de palavra que não está no texto (o modelo engole o início das falas).
- Música: original, gerada por `musica.py` (sem crédito necessário). Não use a do Kevin MacLeod (o Dito não gostou).
- Mix final -14 LUFS, "plim" nos cards.

## Combinados com o Dito
- Português do Brasil, direto. Mostre prévias (áudio, quadros) antes de renderizar de novo.
- Diga quanto tempo falta quando algo demora. Confira o vídeo (quadros) antes de entregar.
