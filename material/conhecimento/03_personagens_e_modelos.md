# 3. Personagens e modelos — as 3 formas (e o que aprendi em cada uma)

## A) Modelo em CÓDIGO (procedural) — Igor e o primeiro Dom
**Onde:** `lib/tgp.js` → `igor()`, `dom()`, `cabecaDom()`, `rostoPlanoDom()`.
**Como funciona:**
1. **Corpo:** `corpo(cores)` carrega um corpo simples com esqueleto (`material/modelos/personagem-simples.glb`) e pinta cada vértice
   pela cor do osso dominante (roupa/mão/perna/pé) + usa a textura original como "relevo" (dobras) em cinza.
2. **Cabeça a partir de FOTO:** uma esfera low-poly deformada (nariz, queixo, mandíbula) em que a **frente recebe a foto projetada de
   frente** (UV = posição x,y na foto, em pixels medidos: centro do rosto, olhos, boca, queixo) e a parte de trás recebe cor de cabelo/pelo.
   A foto é recortada, reduzida (≈ 90 px) e quantizada pra 15 bits (cor de PS1). Piscada e boca são **desenhadas por cima num canvas** a cada quadro.
3. **Acessórios** (chapéu cônico, véu, gola, capa) são geometria simples (`CylinderGeometry` com abertura `thetaStart/thetaLength`) com
   textura de canvas (ex.: 火 desenhado em traços; 小人の隠れ家 com fonte IPAGothic).
**Armadilhas que aprendi:**
- Medir os pontos da foto com uma **grade desenhada por cima** (crop + linhas a cada 20 px) antes de mapear.
- Abertura de cilindro: o "vão" fica onde `thetaStart+thetaLength` termina; com `rotation.y = -π/2` o vão vai pra frente (+z). Com `+π/2` vai pra trás (erro que cometi: o véu cobriu o rosto).
- Foto projetada numa ESFERA parece **"bolha"** (o diretor odiou). Pra rosto de PS1, o certo é **plano** (como a freira de terror PS1 que ele mandou).

## B) Modelo PRONTO (pacote) — Adryan, Gusta, Nicolas, Frentista, Dom final
**Base:** *Simple PSX Character* (JashiPSX, pago). Pipeline (tudo em Blender headless; arquivos 3D FORA do git):
```bash
J=material/producao/modelos-pagos/simple_character_psx
# 1. triângulos do modelo (uv + posição + normal + objeto + material) pra pintar fora do Blender
blender -b --disable-autoexec $J/simple-character-psx.blend --python dump_todos.py -- tris.json
# 2. textura: roupa por região 3D (altura Z, |X|, normal) + rosto da foto alinhada (olhos em y=378,5, meio em x=478)
ROUPA=dom CAB=40,34,30 CONTRASTE=1.3 python3 tools/pintar_jashi_vasco.py tris.json $J/texture/character_256.png foto_alinhada.png texturas/X_512.png
# 3. monta (tira os óculos; CALCA=1 calça reta; CABELO_CURTO; ROSTO_PLANO=-0.10 achata o nariz)
CALCA=1 blender -b --disable-autoexec $J/simple-character-psx.blend --python tools/blender/montar_jashi.py -- texturas/X_512.png $J/X.blend
# 4. (Dom) troca a cara pela foto NA PRÓPRIA MALHA
RZ1=1.965 RKX=0.8 RFYMIN=334 blender -b $J/X.blend --python tools/blender/rosto_foto.py -- material/dom/rosto_alinhado.png $J/X.blend
# 5. passa as 10 animações (idle walk run talk wave sit cower attack hit death) do PSX Character Creator pro esqueleto (retarget em espaço de mundo)
blender -b $J/X.blend --python tools/blender/animar_jashi.py -- $J/X_anim.blend
blender -b $J/X_anim.blend --python tools/blender/exportar_glb.py -- $J/X_anim.glb
```
Depois registre em `lib/elenco4.js` → `ELENCO.X = { arq, alt (altura em m), passada (medida) }` e use `E4.ator('x')`.
**Esqueleto JashiPSX:** `spine … spine.005` (spine.005 = cabeça), `upper_arm.L/R`, `forearm`, `hand`, dedos `f_index/middle/ring/pinky.01–.03`, `thumb`, `thigh/shin/foot`.
**Metalis** (outro rig, Mixamo-like): `Hips, Spine, Head, LeftArm, LeftForeArm, LeftHand…` — **sem dedos**; a mão esquerda segura uma **garrafa** e a direita uma **lata** (pesos de pele no osso da mão!). Trouxa e vara presas na `Spine`.
**Armadilhas:**
- **Rosto alinhado:** a foto precisa ficar na geometria que o pintor espera (olhos nivelados; transformação de similaridade com os dois olhos como âncora).
- Olhos estreitos somem na textura de 256 px → reforce contraste/tamanho do olho na foto (sem saturar: vira vermelho).
- **Escala no carro:** os atores dentro do carro usam escala **0,74** (o modelo do carro é "alto"). Fora do carro, perto dele, escale o carro **1,25** pra proporção bater (senão o Adryan fica mais alto que o teto).
- **Alcance:** o Metalis com 1,10 m tinha ombro a 67 cm e braço de 21 cm (alcance 88 cm) — não alcançava a janela (99 cm). Subi pra 1,38 m e **medi de novo a passada**.

## C) "FRANKENSTEIN" — corpo do pacote + rosto de foto (o Dom final)
O diretor quis: **corpo, roupa, animações e cabeça (cabelo, orelhas, nuca) do modelo pronto; só a CARA da foto.** Tentativas, em ordem:
| Tentativa | Resultado | Lição |
|---|---|---|
| cabeça inteira do 1º modelo no lugar da cabeça do pacote | ok, mas não era o pedido | leia o pedido 2×: "de orelha pra trás é o 2º modelo" |
| máscara (só a frente da esfera) por cima | "serrilhado" nos olhos | o corte estava na altura dos olhos (y 62 vs olhos em 61): suba o corte até a testa |
| meia cabeça da frente | borda saltando na lateral; nariz do pacote furando | estreitar (0,94) e avançar 3 cm |
| placa oval plana por cima | gostou do plano, mas "não deixar espaço" | placa sempre deixa vão/borda |
| **✅ recortar as faces da cara da cabeça do pacote no Blender (`rosto_foto.py`) e dar a ela a foto por UV planar** | encaixe perfeito, sem vão, acompanha a animação | **a melhor solução: trocar a textura NA PRÓPRIA MALHA**, com material próprio; piscada/boca via canvas em runtime (`acessoriosDom`) |
Detalhes do ✅: selecionar faces com centro em `1,69 < z < 1,965`, `|x| < 0,084`, normal pra frente (`n.y < −0,25`); `bpy.ops.mesh.separate`;
UV = mesma conta do pintor (`mx = x/0,4·512+256; my = (1,86−z)/0,4·512+256`, PY interpolado), `KX 0,8` (amostra mais estreita = sem a sombra do véu),
`RFYMIN 334` (a testa não pega a aba do chapéu da foto). Antes, `montar_jashi` com `ROSTO_PLANO=-0.10` (sem nariz) e a textura com `ROSTO_LISO=1`.
**Acessórios do Dom** (`T.acessoriosDom(A)`): chapéu + véu presos ao osso da cabeça (`osso.attach(grupo)` mantém a posição de mundo);
capa (chamas amarelas, 小人の隠れ家 nas costas) presa ao `spine.003`; gola ao `spine.004`. Use `?semveu=1` na folha pra inspecionar a cabeça.

## Folha de aprovação de personagem
`videos/98-dom/index.html` (`?v=frente|tres|lado|costas|rosto`, `&clip=walk|wave`, `&cam=`). Sempre mande pro diretor: 5 vistas + close + andando + acenando.
