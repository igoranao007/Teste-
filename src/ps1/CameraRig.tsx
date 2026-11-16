import { useThree } from "@react-three/fiber";
import { useEffect } from "react";
import { interpolate, useCurrentFrame, Easing } from "remotion";

type Key = { frame: number; pos: [number, number, number]; look: [number, number, number] };

/** Câmera por keyframes (frame -> posição/alvo). */
export const CameraRig: React.FC<{ keys: Key[]; fov?: number }> = ({ keys, fov = 60 }) => {
  const frame = useCurrentFrame();
  const { camera } = useThree();
  const frames = keys.map((k) => k.frame);
  const lerp = (axis: "pos" | "look", i: number) =>
    interpolate(frame, frames, keys.map((k) => k[axis][i]), {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.quad),
    });
  useEffect(() => {
    camera.position.set(lerp("pos", 0), lerp("pos", 1), lerp("pos", 2));
    camera.lookAt(lerp("look", 0), lerp("look", 1), lerp("look", 2));
    (camera as any).fov = fov;
    camera.updateProjectionMatrix();
  });
  return null;
};
