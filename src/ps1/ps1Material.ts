import * as THREE from "three";

/**
 * Visual PS1:
 *  - vertex snapping (jitter dos vértices numa grade de baixa resolução)
 *  - "affine texture warping" (UV sem correção de perspectiva)
 *  - cor quantizada em 15 bits (5 por canal) com dithering Bayer 4x4
 */
export const PS1 = {
  snapResolution: new THREE.Vector2(160, 120), // quanto menor, mais "treme"
  colorDepth: 32.0, // 32 níveis por canal = 15-bit
};

export function ps1ify<T extends THREE.Material>(material: T): T {
  material.onBeforeCompile = (shader) => {
    shader.uniforms.uSnap = { value: PS1.snapResolution };
    shader.uniforms.uDepth = { value: PS1.colorDepth };

    shader.vertexShader = shader.vertexShader
      .replace(
        "#include <common>",
        `#include <common>
        uniform vec2 uSnap;
        varying float vAffineW;`
      )
      .replace(
        "#include <project_vertex>",
        `#include <project_vertex>
        vec4 snapped = gl_Position;
        snapped.xyz /= snapped.w;
        snapped.xy = floor(snapped.xy * uSnap) / uSnap;
        snapped.xyz *= snapped.w;
        gl_Position = snapped;
        vAffineW = gl_Position.w;`
      );

    // affine: multiplica UV por w no vértice e divide no fragmento
    if (shader.vertexShader.includes("#include <uv_vertex>")) {
      shader.vertexShader = shader.vertexShader.replace(
        "#include <fog_vertex>",
        `#include <fog_vertex>
        #ifdef USE_MAP
          vMapUv *= vAffineW;
        #endif`
      );
      shader.fragmentShader = shader.fragmentShader
        .replace(
          "#include <common>",
          `#include <common>
          varying float vAffineW;`
        )
        .replace(
          "#include <map_fragment>",
          `#ifdef USE_MAP
            vec4 sampledDiffuseColor = texture2D( map, vMapUv / vAffineW );
            diffuseColor *= sampledDiffuseColor;
          #endif`
        );
    } else {
      shader.fragmentShader = shader.fragmentShader.replace(
        "#include <common>",
        `#include <common>
        varying float vAffineW;`
      );
    }

    shader.fragmentShader = shader.fragmentShader
      .replace(
        "#include <common>",
        `#include <common>
        uniform float uDepth;
        float bayer4(vec2 p) {
          int x = int(mod(p.x, 4.0));
          int y = int(mod(p.y, 4.0));
          int i = x + y * 4;
          float m[16] = float[16](0.,8.,2.,10.,12.,4.,14.,6.,3.,11.,1.,9.,15.,7.,13.,5.);
          return m[i] / 16.0 - 0.5;
        }`
      )
      .replace(
        "#include <dithering_fragment>",
        `#include <dithering_fragment>
        vec3 c = gl_FragColor.rgb + bayer4(gl_FragCoord.xy) / uDepth;
        gl_FragColor.rgb = floor(c * uDepth) / uDepth;`
      );
  };
  return material;
}

/** Textura sem filtro (pixel duro), como no PS1. */
export function ps1Texture(tex: THREE.Texture): THREE.Texture {
  tex.magFilter = THREE.NearestFilter;
  tex.minFilter = THREE.NearestFilter;
  tex.generateMipmaps = false;
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.needsUpdate = true;
  return tex;
}

/** Textura procedural em canvas (pra testar sem baixar nada). */
export function checkerTexture(a: string, b: string, size = 32, cells = 8) {
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const g = c.getContext("2d")!;
  const s = size / cells;
  for (let y = 0; y < cells; y++)
    for (let x = 0; x < cells; x++) {
      g.fillStyle = (x + y) % 2 ? a : b;
      g.fillRect(x * s, y * s, s, s);
    }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return ps1Texture(t);
}

/** Aplica o visual PS1 em todos os materiais de um modelo carregado (GLB/GLTF). */
export function ps1ifyObject(root: THREE.Object3D) {
  root.traverse((o) => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    mats.forEach((m) => {
      const anyM = m as THREE.MeshStandardMaterial;
      if (anyM.map) ps1Texture(anyM.map);
      ps1ify(m);
      m.needsUpdate = true;
    });
  });
}
