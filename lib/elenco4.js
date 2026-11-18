// Elenco da versão 4 (GLB feitos no Blender, com as 10 animações: idle walk run talk wave sit cower attack hit death).
//   const A = await E4.ator('adryan'); cena.add(A.obj); A.pose('walk', t); A.osso('hand.R')
import * as P from './ps1.js';
import * as M from './modelo.js';
const { THREE } = P;
const J = 'material/producao/modelos-pagos/simple_character_psx/';
export const ELENCO = {
  adryan: { arq: J + 'vegetti_vasco_final_anim.glb', alt: 1.76 },
  gusta: { arq: J + 'gusta_anim.glb', alt: 1.80 },
  nicolas: { arq: J + 'nicolas_anim.glb', alt: 1.62 },
  frentista: { arq: J + 'frentista_anim.glb', alt: 1.74 },
  metalis: { arq: 'material/producao/personagens/metalis/metalis_final.glb', alt: 1.10, fora: ['papelao_cena'],
    recorte: ['trapo_poncho', 'trapo_bermuda', 'cobertor'], cores: { pelo_sujo: '#3f4f8c', pele_suja: '#c2a186', luva_suja: '#cbc3b4', tenis_sujo: '#827c95', preto: '#272727', iris: '#006127', corda: '#9a7c54' } },
};
export async function ator(nome, o = {}) {
  const E = ELENCO[nome];
  const m = await M.carregar(E.arq, { texMax: o.texMax ?? 256, fora: E.fora, mat: o.mat });
  const raiz = new THREE.Group(); raiz.add(m.obj);
  // trapos: o exportador grava a transparência errada; refaz o recorte pela cor (preto da folha = buraco)
  if (E.recorte) for (const ml of m.malhas) for (const mt of (Array.isArray(ml.material) ? ml.material : [ml.material])) {
    const nm = mt.name.replace(/\.\d+$/, ''), tx = mt.uniforms?.uMapa?.value;
    if (!E.recorte.includes(nm) || !tx?.image) continue;
    const im = tx.image, c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
    const x = c.getContext('2d'); x.drawImage(im, 0, 0); const d = x.getImageData(0, 0, c.width, c.height), q = d.data;
    for (let i = 0; i < q.length; i += 4) q[i + 3] = (q[i] * .3 + q[i + 1] * .59 + q[i + 2] * .11) > 8 ? 255 : 0;
    x.putImageData(d, 0, 0); const n = new THREE.CanvasTexture(c); n.flipY = tx.flipY; n.wrapS = tx.wrapS; n.wrapT = tx.wrapT;
    n.magFilter = n.minFilter = THREE.NearestFilter; n.generateMipmaps = false; n.colorSpace = THREE.NoColorSpace; mt.uniforms.uMapa.value = n;
  }
  if (E.cores) for (const ml of m.malhas) for (const mt of (Array.isArray(ml.material) ? ml.material : [ml.material])) { const c = E.cores[mt.name.replace(/\.\d+$/, '')]; if (c && mt.uniforms?.uCor) mt.uniforms.uCor.value.set(c); }
  // altura real → escala
  const mixer = new THREE.AnimationMixer(m.obj), acoes = {};
  for (const c of m.clips) acoes[c.name] = mixer.clipAction(c);
  let atual = null;
  // pose determinística: ação `nome` no tempo t (loop); mistura opcional com outra ação (b, peso)
  function pose(nomeA, t, b = null, pb = 0, tb = t) {
    for (const a of Object.values(acoes)) { a.enabled = false; a.setEffectiveWeight(0); }
    const A1 = acoes[nomeA]; if (!A1) return;
    A1.enabled = true; A1.play(); A1.setEffectiveWeight(1 - pb); A1.time = ((t % A1.getClip().duration) + A1.getClip().duration) % A1.getClip().duration;
    if (b && acoes[b]) { const B = acoes[b]; B.enabled = true; B.play(); B.setEffectiveWeight(pb); B.time = Math.min(tb, B.getClip().duration - 1e-3); }
    mixer.update(0); atual = nomeA;
  }
  // pose congelada no fim/instante (sem loop)
  function quadro(nomeA, t) { const A1 = acoes[nomeA]; if (!A1) return; pose(nomeA, Math.min(t, A1.getClip().duration - 1e-3)); }
  pose('idle', 0);
  m.obj.updateMatrixWorld(true);
  const bb = new THREE.Box3().setFromObject(m.obj, true);
  const h = bb.max.y - bb.min.y || 1, k = (o.alt ?? E.alt) / h; m.obj.scale.multiplyScalar(k); m.obj.position.y -= bb.min.y * k;
  return { obj: raiz, modelo: m, pose, quadro, acoes, osso: m.osso, malhas: m.malhas, dur: n => acoes[n]?.getClip().duration ?? 0 };
}
