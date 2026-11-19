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
  metalis: { maosNeutras: false, pescoco: ['Head'], cabeca: .35, arq: 'material/producao/personagens/metalis/metalis_final.glb', alt: 1.10, fora: ['papelao_cena'],
    recorte: ['trapo_poncho', 'trapo_bermuda', 'cobertor'], cores: { pelo_sujo: '#3f4f8c', pele_suja: '#c2a186', luva_suja: '#cbc3b4', tenis_sujo: '#827c95', preto: '#272727', iris: '#006127', corda: '#9a7c54' } },
};
export async function ator(nome, o = {}) {
  const E = ELENCO[nome];
  const m = await M.carregar(E.arq, { texMax: o.texMax ?? 256, fora: E.fora, mat: o.mat });
  const raiz = new THREE.Group(); raiz.name = 'ator:' + nome; raiz.add(m.obj);
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
  // pescoço/cabeça: o retarget copiou a rotação da cabeça pro pescoço E pra cabeça (dobrada) → nos loops idle/sit/talk
  // a cabeça ficava rodando em círculo sem parar. Guarda a pose de descanso e amortece (o resto do corpo fica igual).
  const BIND = new Map(), BASE = []; m.obj.traverse(b => { if (b.isBone) { BIND.set(b, b.quaternion.clone()); BASE.push([b, b.quaternion.clone(), b.position.clone()]); } });   // pose neutra (bind) por osso
  const PESC = (E.pescoco ?? ['spine.004', 'spine.005']).map(n => m.osso(n)).filter(Boolean);
  const REPOUSO = PESC.map(b => b.quaternion.clone()), CAB = o.cabeca ?? E.cabeca ?? .2;
  const amortecer = () => PESC.forEach((b, i) => b.quaternion.slerpQuaternions(REPOUSO[i], b.quaternion.clone(), CAB));
  // MÃOS: o retarget gravou a rotação do osso da mão CONSTANTE e errada (dobrada ~90° pra dentro em todos os clipes);
  // andando, essa mão torta balançava com o braço e parecia girar. A cada pose o pulso volta pro neutro do rig
  // (mão na linha do antebraço) e os dedos ficam levemente relaxados. Interações (V.pegar, IK) sobrescrevem depois.
  const MAOS = (E.maosNeutras === false ? [] : ['hand.L', 'hand.R']).map(n => m.osso(n)).filter(Boolean);
  const DEDOS = []; for (const s of ['L', 'R']) for (const d of ['f_index', 'f_middle', 'f_ring', 'f_pinky']) for (const k of ['.01.', '.02.', '.03.']) { const b = m.osso(d + k + s); if (b) DEDOS.push(b); }
  const ANTE = { L: m.osso('forearm.L'), R: m.osso('forearm.R') }, TOR = (typeof location !== 'undefined' && new URLSearchParams(location.search).get('tor')?.split(',').map(Number)) || E.torcao || [82, -82];   // pronação: palmas viradas pro corpo (o retarget deixou as palmas pra frente)
  const neutralizar = () => { if (MAOS.length) { if (ANTE.L) ANTE.L.rotateY(TOR[0] * Math.PI / 180); if (ANTE.R) ANTE.R.rotateY(TOR[1] * Math.PI / 180); }
    for (const b of MAOS) b.quaternion.copy(BIND.get(b)); for (const b of DEDOS) { b.quaternion.copy(BIND.get(b)); b.rotateX(.22); } };
  // pose determinística: ação `nome` no tempo t (loop); mistura opcional com outra ação (b, peso)
  // AVALIADOR PRÓPRIO (sem o cache do AnimationMixer): o mixer do Three.js só reescreve um osso quando o valor muda; numa
  // pose parada (sentado no carro, 1º quadro de um gesto) ele não escrevia nada e tudo que o filme aplica por cima
  // (pronação, dedos, olhares, torção) SOMAVA no quadro anterior → cabeças/mãos/braços girando e tremendo.
  // Aqui cada quadro: todos os ossos voltam à base → cada trilha do clipe é avaliada no tempo t e ESCRITA → mistura.
  const AV = {};
  for (const c of m.clips) AV[c.name] = { dur: c.duration, trilhas: c.tracks.map(tr => { const pr = THREE.PropertyBinding.parseTrackName(tr.name), no = THREE.PropertyBinding.findNode(m.obj, pr.nodeName);
    return no && /^(quaternion|position|scale)$/.test(pr.propertyName) ? { no, prop: pr.propertyName, it: tr.createInterpolant() } : null; }).filter(Boolean) };
  const _q = new THREE.Quaternion(), _v = new THREE.Vector3();
  const aplicar = (av, t, peso) => { const tt = ((t % av.dur) + av.dur) % av.dur;
    for (const { no, prop, it } of av.trilhas) { const r = it.evaluate(tt);
      if (prop === 'quaternion') { _q.fromArray(r).normalize(); peso >= 1 ? no.quaternion.copy(_q) : no.quaternion.slerp(_q, peso); }
      else { _v.fromArray(r); peso >= 1 ? no[prop].copy(_v) : no[prop].lerp(_v, peso); } } };
  function pose(nomeA, t, b = null, pb = 0, tb = t) {
    for (const [o2, q, p2] of BASE) { o2.quaternion.copy(q); o2.position.copy(p2); }
    const A1 = AV[nomeA]; if (!A1) return;
    aplicar(A1, t, 1); if (b && AV[b] && pb > 0) aplicar(AV[b], tb, pb);
    amortecer(); neutralizar(); atual = nomeA;
  }
  // pose congelada no fim/instante (sem loop)
  function quadro(nomeA, t) { const A1 = acoes[nomeA]; if (!A1) return; pose(nomeA, Math.min(t, A1.getClip().duration - 1e-3)); }
  pose('idle', 0);
  m.obj.updateMatrixWorld(true);
  const bb = new THREE.Box3().setFromObject(m.obj, true);
  const h = bb.max.y - bb.min.y || 1, k = (o.alt ?? E.alt) / h; m.obj.scale.multiplyScalar(k); m.obj.position.y -= bb.min.y * k;
  return { bind: b => BIND.get(b), obj: raiz, alt: o.alt ?? E.alt, modelo: m, pose, quadro, acoes, osso: m.osso, malhas: m.malhas, dur: n => acoes[n]?.getClip().duration ?? 0 };
}
