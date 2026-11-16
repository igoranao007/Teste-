import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Series, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import legendas from "./legendas.json";

// Edição final (Remotion): junta os 10 planos renderizados pela skill PS1, põe a trilha, o título, a ficha e as legendas.
export const PLANOS: [string, number][] = [
  ["01-estrada", 8], ["02-dentro-do-carro", 12], ["03-a-placa", 8], ["04-corte-por-cor", 10], ["05-a-casa", 8],
  ["06-elevador", 8], ["07-igor-anao", 17], ["08-o-computador", 14.5], ["09-projeto-mogg", 6], ["10-final", 6],
];
export const DURACAO = PLANOS.reduce((a, [, d]) => a + d, 0);
const VERDE = "#39ff6a", CLARO = "#b9ffc9";
const fontes = `
@font-face { font-family: 'Geist'; src: url(${staticFile("fonts/geist.woff2")}) format('woff2'); font-weight: 100 900; }
@font-face { font-family: 'JetBrains Mono'; src: url(${staticFile("fonts/jetbrains.woff2")}) format('woff2'); font-weight: 100 800; }`;
const TITULO: React.CSSProperties = { fontFamily: "'Geist', sans-serif", fontWeight: 900, letterSpacing: ".04em" };
const TERMINAL: React.CSSProperties = { fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 };

// 0:03–0:06 — título letra por letra; 0:06–0:08 — ficha de registro digitada, com os ???? piscando
const Titulo: React.FC = () => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  if (t < 3 || t >= 6) return null;
  return (
    <AbsoluteFill>
      <div style={{ ...TITULO, position: "absolute", left: 0, right: 0, top: 230, textAlign: "center", fontSize: 170, color: VERDE, textShadow: "6px 6px 0 #03220f" }}>
        {"THE GREEN PATH".slice(0, Math.max(0, Math.floor((t - 3) / 0.12)))}
      </div>
      {t >= 4.9 && <div style={{ ...TERMINAL, position: "absolute", left: 0, right: 0, top: 435, textAlign: "center", fontSize: 44, color: CLARO, textShadow: "3px 3px 0 #03220f" }}>feito por Igor Anão</div>}
    </AbsoluteFill>
  );
};
const FICHA = "REGISTRO\n────────────────\nNOME: PHANTOM\nIDADE: 19 ANOS\nCONDIÇÃO: MUDO\nFUNÇÃO: ";
const Ficha: React.FC = () => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  if (t < 6 || t >= 8) return null;
  const n = Math.floor((t - 6.05) * 62), pisca = Math.floor(t * 5) % 2;
  return (
    <AbsoluteFill>
      <div style={{ ...TERMINAL, position: "absolute", right: 110, top: 250, width: 640, padding: "34px 40px", background: "rgba(2,12,6,.82)", border: `3px solid ${VERDE}`, fontSize: 40, lineHeight: 1.55, color: VERDE, whiteSpace: "pre" }}>
        {FICHA.slice(0, Math.max(0, n))}
        {n >= FICHA.length ? <span style={{ opacity: pisca ? 1 : 0.12 }}>????</span> : "▮"}
      </div>
    </AbsoluteFill>
  );
};
// legendas das falas do Igor (geradas por tools/som.py)
const Legendas: React.FC = () => {
  const ms = (useCurrentFrame() / useVideoConfig().fps) * 1000;
  const l = (legendas as { text: string; startMs: number; endMs: number }[]).find((x) => ms >= x.startMs && ms < x.endMs);
  if (!l) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 70 }}>
      <div style={{ ...TERMINAL, fontSize: 46, color: "#eafff0", background: "rgba(2,12,6,.78)", padding: "12px 28px", borderLeft: `6px solid ${VERDE}`, maxWidth: 1500, textAlign: "center" }}>{l.text}</div>
    </AbsoluteFill>
  );
};

export const Filme: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <style>{fontes}</style>
      <Series>
        {PLANOS.map(([nome, d]) => (
          <Series.Sequence key={nome} durationInFrames={Math.round(d * fps)}>
            <OffthreadVideo src={staticFile(`planos/${nome}.mp4`)} muted />
          </Series.Sequence>
        ))}
      </Series>
      <Sequence><Titulo /><Ficha /><Legendas /></Sequence>
      <Audio src={staticFile("trilha.wav")} />
    </AbsoluteFill>
  );
};
