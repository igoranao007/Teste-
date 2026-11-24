# Personagens PRESERVADOS — aguardando decisão posterior sobre a utilização

> Decisão do diretor (24/11): **nenhum** destes personagens ou arquivos é apagado, substituído, modificado ou sobrescrito.
> A produção técnica fica separada da decisão jurídica sobre a publicação (paródia / art. 47 da Lei 9.610/98, análise individual
> por cena). Versões de visual próprio, se feitas, vão em arquivos NOVOS ao lado destes e não substituem os originais.
> A estrutura narrativa da minissérie (MINISSERIE_NOTAS.md) continua a mesma.

## PHANTOM (referência: Deadpool) — versões clássica (vermelha) e amarela (aliado do Dom)
- Documentação: `material/producao/personagens/phantom/LEIA.md` · folha: `folha_phantom.jpg`
- Modelos: `phantom_classica.blend`, `phantom_classica_anim.blend` (+ `.glb`), `phantom_amarela.blend`, `phantom_amarela_anim.blend` (+ `.glb`),
  `malorian.glb` (arma solta) — fora do git (licença dos arquivos de origem não informada)
- Gerador: `tools/blender/phantom.py` · no motor: `E4.ator('phantom')` / `E4.ator('phantom_amarelo')` (lib/elenco4.js)
- Papel na série: mercenário chamado pelo Dom; fim do episódio 1 (casa cheia de quadrinhos da Star Comics, parede explode).

## METALIS (referência: Sonic) — o mendigo de Casmiron
- Documentação: `material/producao/personagens/metalis/LEIA.md`
- Modelos: `metalis_final.blend/.glb` (no elenco), `metalis_v2`, `metalis_v3`, `sonic_base.blend`; `modelos-pagos/simple_character_psx/metalis.blend/.glb`
- No motor: `E4.ator('metalis')` · papel: posto de gasolina (pede moedinha, joga a pedra no carro, acena), olhos na mata.

## ZANGÃO (referência: Cartman) — versões original e militar
- Documentação: `material/producao/personagens/zangao/LEIA.md` · folhas: `folha_zangao_original.jpg`, `folha_zangao_militar.jpg`
- Modelos: `zangao_militar.blend`, `exports/zangao_original.glb`, `exports/zangao_militar.glb`; gerador `tools/blender/zangao.py`
- Pendente: águia do distintivo → escudo do Universitário (referência ao clube). Papel: base de Kessinburgh (renegados anti-caos), comendo enlatado, sem falas.

## OLIVEIRA (referência: cabeça do Godzilla) — v3
- Documentação: `material/producao/personagens/oliveira/LEIA.md` · folhas: `folha_oliveira_v2.jpg`, `folha_oliveira_v3.jpg`
- Modelos: `modelos-pagos/simple_character_psx/oliveira.blend`, `oliveira_anim.blend/.glb`; `material/producao/personagens/oliveira/oliveira.blend`, `exports/oliveira.glb` (v1)
- Geradores: `tools/blender/oliveira_jashi.py`, `tools/blender/girar_ossos.py` · no motor: `E4.ator('oliveira')`
- Papel: base do Dom com o Luan (falas do episódio 1), voz livre grave.
