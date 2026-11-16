// Carrega modelos GLB/GLTF/FBX e troca todo material por P.mat (o visual PS1 continua valendo:
// vértice tremido, textura afim, luz por vértice, névoa). Funciona com esqueleto (SkinnedMesh).
//   const m = await M.carregar('material/modelos/tv.glb', { esc: 1, mat: { semLuz: false }, fora: ['Icosphere'] });
//   cena.add(m.obj);  m.osso('hand.L').rotation.x = …;  m.malhas  m.clips
// Caminhos a partir da raiz do projeto. Rode dentro de window.SETUP = async () => {…}.
import * as P from './ps1.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';
const { THREE } = P;
export const RAIZ = new URL('../', import.meta.url).href;
const cache = new Map();

export const imagem = caminho => new Promise((ok, erro) => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => erro(new Error('imagem: ' + caminho)); i.src = RAIZ + caminho; });

// textura do modelo → pixel duro, sem mipmap, sem gerenciamento de cor; `max` reduz pra no máximo N px (cara de PS1)
export function texPS1(t, max = 128) {
  if (!t) return null;
  const img = t.image;
  if (img && max && Math.max(img.width, img.height) > max) {
    const k = max / Math.max(img.width, img.height), c = document.createElement('canvas');
    c.width = Math.max(1, Math.round(img.width * k)); c.height = Math.max(1, Math.round(img.height * k));
    c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
    const n = new THREE.CanvasTexture(c); n.flipY = t.flipY; n.wrapS = t.wrapS; n.wrapT = t.wrapT; t = n;
  }
  t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.NoColorSpace; t.needsUpdate = true;
  return t;
}

// material do three → P.mat (ou A.matA se passar o.fabrica)
export function converter(m, o = {}) {
  const fab = o.fabrica ?? P.mat;
  const novo = fab({
    cor: m.color ? '#' + m.color.getHexString() : '#ffffff',
    mapa: texPS1(m.map, o.texMax ?? 128),
    opac: m.transparent && m.opacity < 1 ? m.opacity : 1,
    lados: m.side, corVertice: !!m.vertexColors, ...(o.mat || {}),
  });
  novo.name = m.name; return novo;
}

export async function carregar(caminho, o = {}) {
  if (!cache.has(caminho)) {
    const fbx = /\.fbx$/i.test(caminho);
    cache.set(caminho, new Promise((ok, erro) => (fbx ? new FBXLoader() : new GLTFLoader()).load(RAIZ + caminho, r => ok(fbx ? { scene: r, animations: r.animations } : r), undefined, erro)));
  }
  const g = await cache.get(caminho);
  const obj = SkeletonUtils.clone(g.scene), malhas = [], ossos = {};
  const fora = [];
  obj.traverse(n => {
    if (n.isBone) ossos[n.name] = n;
    if (n.isLight || n.isCamera || (o.fora || []).some(f => n.name === f || n.name.startsWith(f))) fora.push(n);
    if (!n.isMesh) return;
    n.material = Array.isArray(n.material) ? n.material.map(m => converter(m, o)) : converter(n.material, o);
    if (n.isSkinnedMesh) n.frustumCulled = false;
    if (!n.geometry.attributes.normal) n.geometry.computeVertexNormals();
    malhas.push(n);
  });
  fora.forEach(n => n.removeFromParent());
  if (o.esc) obj.scale.multiplyScalar(o.esc);
  if (o.pos) obj.position.set(...o.pos);
  if (o.rot) obj.rotation.set(...o.rot);
  const lim = x => x.replace(/[._ ]/g, '').replace(/^DEF-/, '');
  const achar = nome => { let r = null; obj.traverse(n => { if (!r && lim(n.name) === lim(nome)) r = n; }); return r; };   // aceita 'hand.L', 'handL' e o prefixo DEF- do Rigify
  return { obj, malhas: malhas.filter(m => m.parent), clips: g.animations || [], ossos, osso: achar, achar };
}

// gira o osso (no espaço do mundo) pra que a direção osso→filho aponte pra `dir`
const _a = new THREE.Vector3(), _b = new THREE.Vector3(), _q = new THREE.Quaternion(), _pq = new THREE.Quaternion();
export function apontar(osso, filho, dir) {
  osso.updateWorldMatrix(true, true);
  osso.getWorldPosition(_a); filho.getWorldPosition(_b);
  const atual = _b.sub(_a).normalize(), alvo = new THREE.Vector3(...dir).normalize();
  _q.setFromUnitVectors(atual, alvo);
  osso.parent.getWorldQuaternion(_pq);
  const mundo = new THREE.Quaternion(); osso.getWorldQuaternion(mundo);
  osso.quaternion.copy(_pq.invert().multiply(_q.multiply(mundo)));
  osso.updateWorldMatrix(false, true);
}
