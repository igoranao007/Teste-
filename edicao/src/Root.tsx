import React from "react";
import { Composition } from "remotion";
import { Filme, DURACAO } from "./Filme";
import { Filme4, DURACAO4 } from "./Filme4";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Filme" component={Filme} durationInFrames={Math.round(DURACAO * 30)} fps={30} width={1920} height={1080} />
    <Composition id="Filme4" component={Filme4} durationInFrames={Math.round(DURACAO4 * 30)} fps={30} width={1920} height={1080} />
  </>
);
