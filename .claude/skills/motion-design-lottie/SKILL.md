---
name: motion-design-lottie
description: Princípios de motion design da LottieFiles (Disney adaptado, emoção para movimento, coreografia, tempo e curvas) traduzidos para vídeos explicativos narrados, com funções prontas em lib_motion.js (antecipação, squash & stretch, continuação, ação sobreposta, ação secundária, arcos, escalonamento 1/3, destaque do herói). Use junto com a /video-explicativo ao planejar e animar as cenas, ou quando o usuário pedir mais vida, peso ou expressão nos movimentos.
---

# Motion design (LottieFiles) para vídeos explicativos

Base: [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill), licença MIT (texto em `referencia_lottiefiles/LICENSE`).
O usuário credita na legenda do post, então não é preciso pôr crédito na imagem ou no vídeo.
O material original, que é voltado para interface, está em `referencia_lottiefiles/`. Esta página traduz o material para vídeo narrado, em que **toda ação acontece numa palavra**.

## Antes de animar uma cena: os três pilares

| Pilar | Pergunta | Decide |
|---|---|---|
| Intenção emocional | O que quem assiste deve sentir nesta frase? | curva, tempo, amplitude (tabela `EMO`) |
| Narrativa visual | Qual é a micro-história? preparação → ação → resolução | ordem dos elementos |
| Ofício | Como fica crível? | física, ação secundária, arcos |

**Três camadas em toda cena** (cena "chapada" = camada faltando):
1. **Principal:** o que o olho segue, disparado na palavra.
2. **Secundária:** o que reage (sombra, poeira, etiqueta, ícone que treme), 30 a 50% da amplitude, de 0,05 a 0,1 s depois.
3. **Ambiente:** o que nunca para (respiração da câmera, brilho, flutuação, cintilação).

## Checklist por batida (uma por frase da narração)

1. **Emoção** da frase: alegria, calma, urgência, tristeza, surpresa, tensão ou alívio.
2. **Personalidade** do vídeo: uma só, `MOTION.playful` por padrão nos nossos vídeos.
3. **Propriedade principal:** posição para entrar e sair, escala para dar ênfase, cor ou opacidade para mudar estado, tremida para alerta.
4. **Tempo** (tabela abaixo).
5. **Curva:** entrada desacelera (ease-out), saída acelera (ease-in), movimento na tela usa ease-in-out e loop usa seno. **Nunca linear** em movimento espacial; linear só em contador, relógio e rotação.
6. **Herói:** quem age nesta palavra. O resto escurece para 40 a 60% (`stageDim`).
7. **Camadas** secundária e ambiente.
8. **Regra de 1/3:** no máximo cerca de 1/3 dos elementos se mexendo ao mesmo tempo, e nenhum deslocamento maior que 1/3 da tela sem corte de câmera.

## Tempos traduzidos para vídeo narrado

| Situação | Interface (original) | Vídeo narrado |
|---|---|---|
| Pop de pílula, ícone ou carimbo | 150–300 ms | o pico cai **na palavra**: a antecipação começa 0,10–0,12 s antes e o pop assenta em 0,35–0,5 s |
| Personagem reage (squash) | 30–130 ms | agachar 0,1 s antes, impacto na palavra, recuperação em 0,3 s |
| Elemento sai | entradas 30–50% mais longas que saídas | sai em cerca de 0,4 s com ease-in (`EXIT`); entra em cerca de 0,55 s (`ENTER`) |
| Mudança de cena (íris) | 400–600 ms | 0,5 s |
| Revelação dramática | 600–1200 ms | 0,8–1,2 s, de preferência numa pausa da fala |
| Escalonamento | 50–150 ms entre itens | `stagger(i, n, span)`, com span de 0,4 a 0,8 s para a fila inteira |
| Parte que arrasta (antena, braço, cabelo, etiqueta) | 50–150 ms de atraso | `follow(dt, .08–.15)` com mola mais mole |

## Emoção para movimento (resumo; detalhes em `referencia_lottiefiles/director/emotion-mapping.md`)

| Emoção | Caráter | Trajetória | Mola em `EMO` |
|---|---|---|---|
| Alegria | quica, passa do ponto | arco para cima | z .42, w 14 |
| Calma | contínuo, sem overshoot | curvas suaves | z .80, w 6 |
| Urgência ou alerta | seco, rápido | reta, tremida horizontal | z .55, w 22 |
| Tristeza ou peso | lento | cai para baixo | z .85, w 5 |
| Surpresa ou impacto | estoura | radial para fora | z .38, w 20 |
| Tensão | curto, duro | ângulos | z .50, w 18 |
| Alívio | mola mole que assenta | desce e para | z .35, w 8 |

Cores: verde só **chega** (transição para verde), vermelho **pisca e assenta** (não sustenta), e o neutro usa opacidade.

## Os 12 princípios no nosso motor (funções em `lib_motion.js`)

- **Squash & stretch:** `popIn(dt)` e `squash(dt)`. Preserve o volume: se a largura sobe, a altura desce.
- **Antecipação:** `anticipate(dt)` e a parte `pre` de `squash`. O recuo vem antes da palavra, para o pico cair nela.
- **Destaque do herói (staging):** `stageDim(s, t0, t1)` no globalAlpha dos coadjuvantes. Uma ação principal por batida.
- **Continuação e ação sobreposta:** `follow(dt, lag)` e `overlap(s, paradas)` para partes que chegam e balançam depois do corpo.
- **Entrada lenta e saída rápida:** `enterK` e `exitK`.
- **Arcos:** `arc(p0, p1, u, bend)`. Nada viaja em linha reta, com curvatura de 10 a 20% da distância.
- **Ação secundária:** `secondary(dt)`, por exemplo poeira no carimbo, faísca no raio ou anel quando o ✓ chega.
- **Exagero:** a personalidade Playful passa 15 a 25% do ponto.
- **Desenho sólido e apelo:** formas arredondadas e volume constante. Sem contornos, como manda a /video-explicativo.

## Como ligar no motor

1. Copie `lib_motion.js` para `src/` do projeto e inclua depois de `lib_utils.js` (`//@include lib_motion.js`).
2. Em `pill()`: entrada com `popIn` começando 0,08 s antes da deixa, saída com `exitK`.
3. Nos personagens: troque os `kick` de pose por `squash(s - deixa)` (que traz antecipação) e adicione `overlap` em antena, braços e cabeça.
4. Em cada batida: escolha o herói, aplique `stageDim` nos outros e adicione uma ação secundária.
5. Movimentos de A para B usam `arc`, e filas e grades usam `stagger`.

Referências completas (inglês): `referencia_lottiefiles/director/` (filosofia, Disney, emoção, coreografia, narrativa), `patterns/` (entrada e saída, feedback, ambiente, escalonamento) e `reference/` (tabelas de tempo e curvas, checklist de qualidade, solução de problemas).
