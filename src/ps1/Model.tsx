import React, { useEffect, useMemo, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { continueRender, delayRender, staticFile } from "remotion";
import { ps1ifyObject } from "./ps1Material";

/**
 * Carrega um modelo .glb/.gltf de public/models/ e aplica o visual PS1.
 * Ex: <Model file="models/tv.glb" position={[0,0,0]} scale={1} />
 */
export const Model: React.FC<{
  file: string;
  position?: [number, number, number];
  rotation?: [number, number, number];
  scale?: number;
}> = ({ file, ...props }) => {
  const [scene, setScene] = useState<THREE.Group | null>(null);
  const handle = useMemo(() => delayRender(`modelo ${file}`), [file]);

  useEffect(() => {
    new GLTFLoader().load(
      staticFile(file),
      (gltf) => {
        ps1ifyObject(gltf.scene);
        setScene(gltf.scene);
        continueRender(handle);
      },
      undefined,
      (err) => {
        console.error(err);
        continueRender(handle);
      }
    );
  }, [file, handle]);

  if (!scene) return null;
  return <primitive object={scene} {...props} />;
};
