# Cássia — a Sala Lilás virtualizada

**AKCIT Camp Multicêntrico 2026 · Centro-Oeste · Goiânia · 24/10/2026**

A Sala Lilás é o melhor acolhimento que existe no Brasil: uma sala dentro da delegacia,
com médica legista, enfermeira e assistente social, onde a mulher é atendida sem repetir
a história. Em Goiás são três unidades — e quem mora longe não chega.

A Cássia transforma essa Sala Lilás em software: o mesmo acolhimento, as mesmas fontes
oficiais e a mesma revisão humana, presentes em qualquer ambiente onde a mulher estiver.

**O número que abre o pitch:** em Goiás existem 3 Salas Lilás em 246 municípios.
**243 não têm.** 26 municípios têm delegacia da mulher (DEAM), 18 delegacias têm plantão
24 horas, e 219 municípios não têm nenhuma dessas três camadas.

---

## Entregáveis obrigatórios (seção 8.1 do edital)

| # | Entregável | Onde está |
|---|---|---|
| 1 | Protótipo funcional do agente (demo ao vivo ou gravado) | `cassia-prototipo/index.html` — HTML único, abre offline, sem build |
| 2 | BMC do negócio ou impacto social atualizado | `cassia-bmc/index.html` |
| 3 | Pitch de 3 minutos | `cassia-pitch/cassia-pitch-3min.pptx` (e `.pdf`) + `cassia-pitch/pitch-texto.md` |
| 4 | Documentação do fluxo do agente (inputs, lógica, outputs) | `cassia-arquitetura/index.html` |

Extras: suíte de testes do protótipo (`build/test_prototype.js`, 80 asserções), base de rede
dos 246 municípios de Goiás, log de chamadas de agente por sessão e o texto integral do
pitch com as respostas às objeções da banca.

---

## Como rodar a demo (60 segundos)

1. Abra `cassia-prototipo/index.html` no navegador (funciona offline, sem servidor).
2. **Mapa da rede** (M): a grade de 246 municípios, com as três camadas (Sala Lilás, DEAM,
   delegacia 24h), a lista de quem tem Sala Lilás (3) e de quem não tem (243), e a resposta
   para o município escolhido.
3. **Rota segura** (R): troque o município. **Campos Belos** mostra a DEAM a 303 km e as
   cidades do trajeto **sem rede de apoio**.
4. **Relato** (A1 → A2): o agente extrai 9 campos, com status *relatado / incerto / negado /
   não perguntado*.
5. **Cofre** (C): o que a Cássia guarda quando a mulher ainda não tem coragem de ir.
6. **Painel da equipe** (P): é onde a equipe lê o resumo, a procedência de cada frase e as
   pendências. É a tela que responde à objeção "e se o relato for falso?".
7. **Modo discreto** (D): fachada, sensor de manuseio e o **botão de saída rápida**.

## Roteiro do pitch (3 min)

| Tempo | Bloco | Slide |
|---|---|---|
| 0:00 | A cena: 2h da manhã, interior de Goiás, delegacia a 303 km, 243 sem Sala Lilás | 2 |
| 0:20 | **O que é uma Sala Lilás** — para quem nunca ouviu | 3 |
| 0:40 | **"É só ligar 180?"** — a objeção que vem primeiro | 4 |
| 0:55 | A solução: a Sala Lilás como software | 5 |
| 1:10 | **O cofre**: guardar sem apressar | 6 |
| 1:25 | O fluxo do agente: roteador + 8 especialistas | 7 |
| 1:45 | **"E se o relato for falso?"** — a objeção da banca, respondida antes | 8 |
| 2:00 | Demo (60 s) | 10 |
| 2:30 | Negócio: quem paga, ativo próprio, indicadores | 11 |
| 2:45 | O pedido | 12 |

Texto falado: **480 palavras** (3:00 a 160 ppm). Ver `cassia-pitch/pitch-texto.md` (também
está nas notas do orador de cada slide do PPTX).

## Arquitetura em uma frase

> Um roteador e oito especialistas; o banco vetorial guarda **norma pública**, o banco
> relacional com PostGIS guarda a **rede** (unidades, horários, rotas) e o relato da mulher
> fica **cifrado, isolado e fora do vetor**, no **cofre**, sob chave da própria usuária.
> A IA organiza; a profissional decide.

## Repositório (proposta)

```
cassia/
├─ README.md
├─ cassia-prototipo/index.html      # protótipo navegável (entregável 1)
├─ cassia-bmc/index.html            # BMC de impacto social (entregável 2)
├─ cassia-pitch/cassia-pitch-3min.pptx   # pitch (entregável 3)
├─ cassia-pitch/pitch-texto.md      # texto do pitch + respostas às objeções
├─ cassia-arquitetura/index.html   # fluxo do agente (entregável 4)
├─ data/municipios_go.csv           # rede dos 246 municípios (levantamento da equipe)
└─ tests/test_prototype.js          # suíte de testes do protótipo
```

## Limites assumidos (e por quê)

- **Dados da rede:** o que existe foi levantado pela equipe; endereço, telefone e horário
  aparecem como **sintéticos** no protótipo, marcados como tal, até a confirmação oficial.
  O mapa de cobertura é **não geográfico**: cada quadradinho é um município, porque as
  coordenadas não estavam disponíveis a tempo.
- **Relato falso:** a Cássia não descobre mentira. Ela garante **procedência** (trecho literal
  + número da mensagem), não inventa lacuna, não aciona polícia e não classifica risco.
- **Botão de saída rápida, não botão de pânico:** "pânico" sugere alerta automático à polícia,
  e a Cássia nunca aciona polícia. O botão pausa a sessão e mascara a tela.
- **Cofre:** protege o conteúdo em repouso e o controle de acesso, não um dispositivo
  infectado nem uma situação de coerção. O que a Cássia promete é um lugar cifrado, sob
  chave da própria usuária, e a possibilidade de apagar tudo.
- **Fora do escopo do protótipo:** WhatsApp em produção, voz, menores como usuários, dados
  reais e qualquer notificação automática à polícia.

## Fontes

Polícia Científica de Goiás (Salas Lilás e endereços) · Polícia Civil-GO (delegacias, plantão
24 horas e horários de atendimento) · goias.gov.br/social (rede de atendimento e proteção à
mulher) · Ministério das Mulheres (Ligue 180 e canais de atendimento, inclusive WhatsApp) ·
Prefeitura de Goiânia (CEVAM e Casa Abrigo Sempre Viva) · TJ-GO (rede de atendimento) ·
IBGE (Censo 2022) · Lei 11.340/2006 · Lei 13.431/2017 · Lei 14.149/2021 (FONAR) ·
Portaria SSP/GO nº 2/2025 (Programa Sala Lilás).
