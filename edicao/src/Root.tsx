import React from "react";
import { Composition } from "remotion";
import { Filme, DURACAO } from "./Filme";

export const RemotionRoot: React.FC = () => (
  <Composition id="Filme" component={Filme} durationInFrames={Math.round(DURACAO * 30)} fps={30} width={1920} height={1080} />
);
