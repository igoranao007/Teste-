import { ThreeCanvas } from "@remotion/three";
import React from "react";
import { useVideoConfig } from "remotion";

/**
 * Renderiza a cena em baixa resolução (320x240 por padrão, igual PS1)
 * e amplia sem suavização pra ficar com o pixel "gordo".
 */
export const PS1Canvas: React.FC<{
  children: React.ReactNode;
  internalWidth?: number;
  background?: string;
}> = ({ children, internalWidth = 320, background = "#000" }) => {
  const { width, height } = useVideoConfig();
  const scale = width / internalWidth;
  const internalHeight = Math.round(height / scale);
  return (
    <div style={{ width, height, overflow: "hidden", background }}>
      <div
        style={{
          width: internalWidth,
          height: internalHeight,
          transform: `scale(${scale})`,
          transformOrigin: "top left",
          imageRendering: "pixelated",
        }}
      >
        <ThreeCanvas
          width={internalWidth}
          height={internalHeight}
          dpr={1}
          gl={{ antialias: false, preserveDrawingBuffer: true }}
          style={{ imageRendering: "pixelated" }}
        >
          {children}
        </ThreeCanvas>
      </div>
    </div>
  );
};
