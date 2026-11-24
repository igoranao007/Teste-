# GUIA DO ALUNO — como fazer tudo o que fizemos (do zero ao avançado)

> Aula completa, na ordem certa pra aprender. Cada parte tem: **o que é**, **pra que serve**, **o mínimo pra começar**,
> **as receitas que usamos** e **erros comuns**. Os exemplos são do próprio projeto THE GREEN PATH.
> Dica de professor: leia uma parte, rode o exemplo, mude UM número e rode de novo. É assim que se aprende 3D.

---

## AULA 0 — O mapa das ferramentas (quem faz o quê)
| Ferramenta | Pra que serve no projeto |
|---|---|
| **Terminal (bash)** | rodar tudo: Blender sem janela, Node, Python, ffmpeg, git |
| **Blender** (5.x) | modelar, pintar UV, esqueleto, pesos, animação, retarget, bake, exportar GLB, render de folhas |
| **Python + bpy** | controlar o Blender por script (repetível, sem clicar) |
| **Python + PIL/numpy** | pintar texturas, montar folhas de imagem, mexer em pixels |
| **three.js** (JavaScript) | o "motor" do filme: monta a cena, câmera, luz, personagens, efeitos PS1 |
| **Playwright + Chromium** | abre a página da cena sem janela e tira foto de cada quadro |
| **ffmpeg** | junta quadros em vídeo, corta, mistura áudio, converte formatos |
| **Remotion** | edição final (cortes, legendas, trilha) em cima dos planos renderizados |
| **Chatterbox (TTS)** | gera vozes (clonadas de referência ou voz pública) localmente |
| **git** | salvar versões e mandar pro GitHub |

Ordem de produção de uma cena: **modelo (Blender) → animação (Blender) → GLB → cena (three.js) → render (Playwright) → som (Python/ffmpeg) → edição (Remotion)**.

---

## AULA 1 — Terminal em 10 minutos
```bash
pwd                      # onde estou
ls -la pasta/            # listar
cd pasta                 # entrar
cp a b ; mv a b ; mkdir -p x/y
cat arquivo.txt | head -20
grep -rn "palavra" lib/  # procurar texto
du -sh pasta/            # tamanho
comando > log.txt 2>&1 & # rodar em segundo plano guardando o log
```
- Variáveis de ambiente antes do comando mudam o comportamento dos nossos scripts: `ROUPA=luan RES=1024 python3 tools/pintar_jashi_vasco.py ...`
- `| grep -E "Error|Traceback"` filtra só os erros de um comando barulhento (o Blender imprime muito).

---

## AULA 2 — Blender: o essencial (com e sem janela)
### 2.1 Conceitos que você PRECISA entender
- **Objeto** (tem posição/rotação/escala) contém **dados** (a malha: vértices, arestas, faces).
- **Modo Objeto × Modo Edição**: no Edição você mexe em vértices.
- **Malha low-poly PS1**: poucos triângulos (personagem ~2–7 mil), textura pequena (64–512 px), sem suavizar textura (**Closest**).
- **UV**: o "molde" que diz qual pixel da textura vai em cada face. Sem UV boa, textura borra/estica.
- **Material + Textura**: no PS1 usamos 1 textura colorida por material, interpolação **Closest** (pixel duro).
- **Armature (esqueleto)**: ossos. **Pesos (vertex groups)**: quanto cada osso puxa cada vértice. **Modificador Armature** liga malha ↔ esqueleto.
- **Pose de descanso (rest)** × **pose**: animação = rotação dos ossos em relação ao descanso, quadro a quadro (**Action** com **keyframes**).
- **Escala aplicada**: se o objeto tem escala ≠ 1, contas de distância dão errado (foi um bug nosso). `Ctrl+A → Escala` ou levar em conta a matriz.

### 2.2 Atalhos (com janela)
`G` mover · `R` girar · `S` escala · `Tab` modo edição · `1/2/3` vértice/aresta/face · `Ctrl+R` corte em laço · `E` extrudar ·
`U` desdobrar UV · `Ctrl+P` parentear (ex.: "Com pesos automáticos") · `Numpad 1/3/7` frente/lado/topo · `Ctrl+Tab` modo pose · `I` inserir keyframe.

### 2.3 Rodar sem janela (é assim que fizemos tudo)
```bash
blender -b arquivo.blend --python script.py -- arg1 arg2      # -b = sem janela; depois do "--" vêm os SEUS argumentos
blender -b --python-expr "import bpy; print(len(bpy.data.objects))"
```
Dentro do script: `args = sys.argv[sys.argv.index('--') + 1:]`.

### 2.4 bpy — o mínimo que resolve 90%
```python
import bpy, bmesh
from mathutils import Vector, Matrix
o = bpy.data.objects['body']                    # pegar objeto
mw = o.matrix_world                             # local → mundo
for v in o.data.vertices: p = mw @ v.co         # posição de cada vértice no mundo
bpy.ops.import_scene.gltf(filepath='x.glb')     # importar GLB  (fbx: import_scene.fbx · bvh: import_anim.bvh)
bpy.ops.export_scene.gltf(filepath='x.glb', export_format='GLB', export_animations=True)
bpy.ops.wm.save_as_mainfile(filepath='novo.blend')   # salvar como (NUNCA por cima do original)
```
**bmesh** (editar malha por código): `bm = bmesh.new(); bm.from_mesh(o.data)` → mexe → `bm.to_mesh(o.data); bm.free()`.
- Soldar vértices: `bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0004)`
- Apagar faces: `bmesh.ops.delete(bm, geom=faces, context='FACES')`
- Cortar por plano: `bmesh.ops.bisect_plane(...)` · Extrudar região: `bmesh.ops.extrude_face_region(...)` · Chanfro: `bmesh.ops.bevel(...)`

### 2.5 Receitas que usamos (copie e adapte)
**Reduzir polígonos (deixar PS1):**
```python
md = o.modifiers.new('d', 'DECIMATE'); md.ratio = 7000 / len(o.data.polygons); md.use_collapse_triangulate = True
bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='d')
```
> Antes de reduzir, **solde os vértices** — modelos que vêm com vértices soltos nas costuras se estilhaçam.

**UV automática:** selecionar SÓ o objeto → `bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.004); bpy.ops.object.mode_set(mode='OBJECT')`
> Erro clássico: com outros objetos selecionados, as ilhas de todos são empacotadas juntas e a textura fica minúscula.

**Bake (passar detalhe/cor de um modelo pesado pra um leve):** Cycles; material do modelo ALTO com um nó Image Texture ativo apontando
pra imagem nova; selecionar alto + baixo (baixo ativo);
`bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_selected_to_active=True, cage_extrusion=0.02, max_ray_distance=0.05)`;
depois `type='AO'` pra sombra nas dobras. Multiplica as duas e reduz pra 15 bits (ver Aula 4).

**Esqueleto + pesos automáticos:** selecionar malha e depois o esqueleto (ativo) → `bpy.ops.object.parent_set(type='ARMATURE_AUTO')`.
Conferir: nenhum vértice sem grupo. Limpar pesos errados (ex.: mão puxando a coxa) por região.

**Pose A → pose T:** girar os ossos do braço em modo pose, aplicar o modificador Armature na malha, `bpy.ops.pose.armature_apply()` no esqueleto e recolocar o modificador.

**Render de inspeção (folhas):** Workbench + `shading.color_type='TEXTURE'` (rápido, mostra a textura crua); Cycles pra versão bonita.
Câmera apontando: `cam.rotation_euler = (alvo - cam.location).to_track_quat('-Z', 'Y').to_euler()`.

### 2.6 Animação no Blender por código
- Ação nova: `act = bpy.data.actions.new('nome'); arm.animation_data_create(); arm.animation_data.action = act`
- Keyframe: `pb = arm.pose.bones['upper_arm.L']; pb.rotation_mode='QUATERNION'; pb.rotation_quaternion = q; pb.keyframe_insert('rotation_quaternion', frame=f)`
- Blender 5: as curvas ficam em `action.layers → strips → channelbags → fcurves` (não em `action.fcurves`).
- **Retarget** (passar animação de outro esqueleto): pra cada quadro, rotação do osso de origem relativa ao descanso dele → aplicar no osso de destino
  sobre o descanso do destino (espaço de mundo). Script pronto: `tools/blender/animar_bvh.py` (mapa de nomes `MAP`/`MAP_UAL`).
- **Encostar no chão**: medir a menor altura do pé no clipe e mover o quadril (`tools/blender/aterrar.py`).
- **Verificar**: `tools/blender/qa_animacoes.py` (pé afundando/flutuando, estalo > 60° por quadro, NaN) + folha visual (`folha_animacoes.py`).

### 2.7 Erros de Blender que já caímos
- Sobrescrever o `.blend` original → sempre salvar com nome novo (`_v2`).
- Referência a objeto que "sumiu" depois de importar outro arquivo (`ReferenceError`) → buscar de novo por nome.
- Nome de ação novo igual ao da importada → a importada é apagada sem querer.
- Medir com objeto escalado sem considerar a escala.

---

## AULA 3 — Estilo PS1 (as regras do visual)
1. Render em **1/4 da resolução** e ampliar sem suavizar (pixel grande).
2. **Vértices tremendo** (posição arredondada na grade da tela) e **textura afim** (entorta um pouco nas faces grandes).
3. **Cor de 15 bits** (32 níveis por canal) + pontilhado leve; texturas **64–512 px**, filtro **Closest**.
4. **Luz por vértice**, neblina pra esconder o fundo, poucas luzes.
5. Cores do projeto: verde `#39ff6a` dominante, amarelo nas luzes/energia, noite.
No nosso motor isso já vem pronto em `lib/ps1.js` (palco com `divisor:4`, `tremor`, `pont`).

---

## AULA 4 — Texturas com Python (PIL + numpy)
```python
from PIL import Image, ImageDraw
im = Image.new('RGB', (64, 64), (40, 40, 44)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, 63, 63), outline=(62, 62, 68)); d.line((8, 32, 56, 32), fill=(255, 210, 30))
im = im.point(lambda v: (v // 8) * 8)        # 15 bits (32 níveis)
im.save('placa.png')
```
- **Pintar sobre o UV de um modelo**: exporte os triângulos (`tools/blender/dump_tris.py`), rasterize cada triângulo no espaço UV
  (`tools/rasterizar_texels.py`) e decida a cor de cada pixel pela posição 3D dele (é o que `tools/pintar_jashi_vasco.py` faz: camisa,
  calça, gola em V, escudo, números…). Mantém as dobras pintadas do original multiplicando pela luminância (`dobra()`).
- **Projetar uma FOTO no modelo** (ex.: camisa real): mapear (x, z) do corpo → (px, py) da foto, com ângulo em volta do tronco.
- **Logos e emblemas**: desenhar com `ImageDraw` em alta e reduzir com `Image.LANCZOS`, depois 15 bits (`tools/dom_emblema.py`).
- **Folhas de apresentação**: colar renders lado a lado com títulos (`ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 24)` — fonte com acento e japonês).

---

## AULA 5 — O motor three.js do projeto (fazer uma cena)
Cada cena é uma pasta `videos/NN-nome/index.html`. Esqueleto mínimo:
```html
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<script>VIDEO={w:1920,h:1080,fps:30,dur:6}</script>
<script src="../../lib/boot.js"></script></head><body><div id="stage"></div>
<script type="module">
import * as P from '../../lib/ps1.js';
import * as E4 from '../../lib/elenco4.js';
const { THREE } = P;
window.SETUP = async () => {
  const S = P.palco({ fov: 35, cam: [0, 1.5, 4], alvo: [0, 1, 0], fundo: '#0d1410',
    luz: { keyDir: [-.4, .7, .8], keyCor: '#f2efe6', fillCor: '#3a5a44', amb: '#2a3a30' } });
  S.scene.add(P.caixa(10, .02, 10, P.mat({ cor: '#2a2a2c' }), { pos: [0, -.01, 0] }));   // chão
  const A = await E4.ator('adryan'); S.scene.add(A.obj);                                // personagem com animações
  S.update = t => {                                                                     // TUDO é função do tempo t (segundos)
    A.obj.position.z = -2 + t * .5;                                                     // anda pra frente…
    A.pose('u_Walk_Loop', t);                                                           // …com a animação de andar
    S.camera.position.set(2, 1.6, 3); S.camera.lookAt(A.obj.position.x, 1, A.obj.position.z);
  };
};
</script></body></html>
```
- Peças: `P.caixa(w,h,d,mat,{pos,rot})`, `P.cilindro(rTopo,rBase,h,mat,{seg})`, `P.esfera(r,mat)`, `P.mat({ cor, mapa, semLuz, aditivo, opac, lados })`.
- Texturas desenhadas no código: `P.textura(w, h, (ctx, w, h, rnd) => { ... })`.
- Modelos: `await M.carregar('caminho.glb', { esc, texMax })` (lib/modelo.js) — troca materiais pelo material PS1.
- Personagem: `A.pose(nomeDaAnimação, t)`, `A.osso('hand.R')` (pra prender objeto na mão: `osso.attach(objeto)`).
- **Andar sem deslizar o pé**: deslocamento = `t / duração_do_walk * passada` (`ELENCO[nome].passada`).
- Ver um quadro: `node tools/foto.mjs NN-nome 2.5 "v=frente" saida.jpg` · Render do vídeo: `node render.mjs NN --conc=2` → `out/NN-nome.mp4`.
- Parâmetros na URL (`?v=perto&clip=...`) facilitam testar várias câmeras sem mexer no código.

---

## AULA 6 — Efeitos (como fizemos cada um)
| Efeito | Como |
|---|---|
| **Luz própria / energia** | material com `semLuz:true` (no Blender: nome do material contendo `brilho`) |
| **Brilho forte (bloom falso)** | cópia da peça acesa um pouco maior, material `aditivo:true, opac:.4` (no Blender: nome com `aura`) |
| **Neblina** | `P.palco({ nevoa: ... })` / `P.nevoa(...)` |
| **Sirene / alarme** | luz que alterna cor/intensidade com `Math.sin(t*k)`; plano vermelho aditivo piscando; som de alarme |
| **Telas verdes / digitação** | `lib/terminal.js` (`terminal`, `carregando`), `lib/filme.js` (`telaCodigo`, `digitado`, `chiadoVerde`) |
| **Fita VHS / REC / câmera de segurança** | `lib/arh.js` (`hud`, `evidencia`) |
| **Perda de sinal / glitch** | `chiadoVerde` (linhas de tracking, rasgos, flash) |
| **Explosão (parede)** | flash branco 2 quadros + esfera aditiva laranja que cresce e some + pedaços (caixas) com velocidade e gravidade calculadas por `t` + fumaça (planos cinza que sobem e somem) + tremor de câmera + som de explosão |
| **Objeto girando sem emenda** | número inteiro de voltas por clipe (`tools/blender/girar_ossos.py`) |
| **Pano (capa)** | malha em grade recalculada todo quadro (`pano()` em lib/tgp.js) |
| **Mão segurando algo no chão** | IK de 2 ossos (ombro→cotovelo→punho) até o objeto (`segurar()` em `acessoriosDom`) |
| **Rosto em foto que pisca/fala** | desenhar a foto num canvas e pintar pálpebra/boca por cima a cada quadro |
| **Render "bonito" com brilho** | Cycles + emissão + `tools/brilho_png.py` (soma um desfoque das partes amarelas) |

---

## AULA 7 — Som, vozes e ffmpeg
**Vozes (Chatterbox, local, sem mandar áudio pra fora):**
```bash
python3 -m venv /tmp/tts && /tmp/tts/bin/pip install chatterbox-tts
/tmp/tts/bin/python tools/clonar_voz.py audio/voz/original.mp3 "Fecha essa porta imediatamente!" audio/voz/igor 3
```
- `exaggeration` 0,4 = calmo; 0,7–0,9 = emoção/grito. `cfg_weight` mais baixo = fala mais solta. Gere **3+ tomadas** e escolha.
- Voz sem referência = voz pública do modelo (pra personagens sem áudio, como Oliveira/Luan): engrossar com `tools/vilao.sh`/pitch.
- **Atuação**: escreva a fala como se fala ("Fecha… essa porta. IMEDIATAMENTE!"), pontuação marca pausa e força.

**ffmpeg (copie e cole):**
```bash
ffmpeg -i in.mp4 -ss 3 -t 5 -c copy corte.mp4                         # cortar 5 s a partir de 3 s
ffmpeg -i video.mp4 -i trilha.wav -c:v copy -c:a aac -shortest saida.mp4   # pôr áudio no vídeo
ffmpeg -i voz.wav -af "highpass=f=80,acompressor,loudnorm=I=-16" voz_ok.wav # limpar e nivelar voz
ffmpeg -i in.mp4 -vf scale=1280:-2 -crf 23 out_720p.mp4                 # reduzir pra 720p
ffmpeg -f concat -safe 0 -i lista.txt -c copy junto.mp4                 # juntar vídeos (lista: file 'a.mp4')
ffmpeg -i in.mp4 -vf "fps=2,scale=320:-1,tile=4x2" -frames:v 1 folha.png # folha de quadros pra conferir
```
**Trilha do filme:** `tools/som4.py` monta os eventos (cues) + vozes → `audio/synth.py` sintetiza a mixagem.

---

## AULA 8 — Edição final (Remotion)
- Projeto em `edicao/`. Os planos renderizados vão pra `edicao/public/planos/`, a trilha pra `edicao/public/`.
- Legendas/ordem em `edicao/src/legendas4.json`. Render: ver `tools/filme4.sh` (`npx remotion render ... Filme4 out/...mp4`).
- `npx remotion studio edicao/src/index.ts` abre o editor visual no navegador (quando tiver tela).

---

## AULA 9 — Baixar coisas grátis (itch.io, OpenGameArt) e conferir licença
**itch.io (script pronto):**
```bash
python3 tools/itch.py material/modelos/itch/minha_pasta https://autor.itch.io/pacote https://outro.itch.io/pacote2
```
Ele imprime o preço, a licença que achou na página e baixa os arquivos (só se o download for grátis). Depois:
`unzip -qo arquivo.zip -d pasta/` e converta pra GLB se precisar (`tools/para_glb.py` no Blender).

**Como achar pacotes:** busque "PSX", "PS1", "low poly" + o que precisa (weapons, food, bunker, office, sfx, music) no itch.io;
OpenGameArt (`opengameart.org/content/<nome>`) tem muito som **CC0**:
```bash
curl -sL -o pacote.zip https://opengameart.org/sites/default/files/100-CC0-SFX_0.zip
```
**Licenças — leia SEMPRE:**
- **CC0** = domínio público, usa à vontade. **CC BY** = usa, mas **dá crédito**. **CC BY-SA** = crédito + mesma licença no derivado.
- "Free for commercial use" = ok pra usar; "don't redistribute" = não pode subir os arquivos crus no GitHub público (deixe no `.gitignore`).
- Sem licença na página = **não use em publicação** sem perguntar ao autor.
- Registre tudo numa tabela (o projeto usa `material/producao/minisserie/ASSETS.md`) e ponha os créditos no fim do episódio.

---

## AULA 10 — git (salvar e enviar)
```bash
git status                     # o que mudou
git add arquivo1 pasta/        # escolher o que vai
git commit -m "mensagem clara do que mudou"
git push -u origin claude/mp4-animation-threejs-remotion-xyh5wp
git log --oneline | head       # histórico
```
- Arquivos pesados/licenciados ficam fora (`.gitignore`). Nunca `git stash`/`rm` sem conferir.

---

## AULA 11 — Método de trabalho (o que separa o amador do profissional)
1. **Anote o pedido inteiro** antes de produzir (o diretor manda em partes).
2. **Meça, não chute**: posição de objeto = medir no modelo (vista ortográfica com grade, centro por cor/material).
3. **Uma mudança por vez** e confira com imagem (frente, 3/4, lado, costas, close).
4. **Inspecione em resolução cheia**; o motor em 1/4 esconde defeitos.
5. **Verificação automática + olho humano** (QA de animação e folha visual).
6. **Nunca destrua o que existe**: versão nova em arquivo novo.
7. **Mostre e peça aprovação** antes de seguir pra próxima etapa.

---

## EXERCÍCIOS (faça na ordem)
1. Abra `videos/91-luan/index.html?p=adryan&clip=u_Walk_Loop&v=tres` com `tools/foto.mjs` e troque a animação por `m_walk_cautious`.
2. Crie `videos/60-teste/` com o esqueleto da Aula 5: Adryan andando 3 m e parando com `m_stop_from_run`.
3. Ponha uma caixa amarela com `semLuz` e uma cópia maior `aditivo` em volta: veja o brilho.
4. Faça uma luz de sirene piscando (vermelho) e um som de alarme do pacote sci-fi por cima (ffmpeg).
5. No Blender, importe uma lata do pacote de enlatados, reduza, ponha textura Closest e exporte GLB; carregue na cena com `M.carregar`.
6. Gere 3 tomadas de "Malditos, eles me acharam!" com exaggeration 0,8 e escolha a melhor.
