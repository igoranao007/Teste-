import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Series, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import dados from "./legendas4.json";

// THE GREEN PATH v4 — edição final: 16 planos renderizados (skill PS1), trilha, fichas, título e legendas.
type Leg = { text: string; quem: string; startMs: number; endMs: number; semVoz: boolean };
export const PLANOS4 = dados.planos as [string, number][];
export const DURACAO4 = PLANOS4.reduce((a, [, d]) => a + d, 0);
const INI: Record<string, number> = {}; { let a = 0; for (const [n, d] of PLANOS4) { INI[n.slice(0, 2)] = a; a += d; } }
const VERDE = "#39ff6a", CLARO = "#b9ffc9";
const fontes = `
@font-face { font-family: 'Geist'; src: url(${staticFile("fonts/geist.woff2")}) format('woff2'); font-weight: 100 900; }
@font-face { font-family: 'JetBrains Mono'; src: url(${staticFile("fonts/jetbrains.woff2")}) format('woff2'); font-weight: 100 800; }`;
const TITULO: React.CSSProperties = { fontFamily: "'Geist', sans-serif", fontWeight: 900, letterSpacing: ".04em" };
const TERMINAL: React.CSSProperties = { fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 };
const useT = () => useCurrentFrame() / useVideoConfig().fps;

// ficha digitada (plano 1: Adryan · plano 2: Nicolas)
const Ficha: React.FC<{ ini: number; fim: number; texto: string; lado?: "dir" | "esq" }> = ({ ini, fim, texto, lado = "dir" }) => {
  const t = useT();
  if (t < ini || t >= fim) return null;
  const n = Math.floor((t - ini - .1) * 40), sai = Math.max(0, Math.min(1, (fim - t) / .3));
  return (
    <AbsoluteFill style={{ opacity: sai }}>
      <div style={{ ...TERMINAL, position: "absolute", [lado === "dir" ? "right" : "left"]: 90, top: 150, width: 600, padding: "30px 38px", background: "rgba(2,12,6,.84)", border: `3px solid ${VERDE}`, fontSize: 36, lineHeight: 1.55, color: VERDE, whiteSpace: "pre" }}>
        {texto.slice(0, Math.max(0, n))}{n < texto.length ? "▮" : <span style={{ opacity: Math.floor(t * 3) % 2 ? 1 : .2 }}>▮</span>}
      </div>
    </AbsoluteFill>
  );
};
// THE GREEN PATH: letras grandes, verdes, pixeladas (plano 5)
const Titulo: React.FC = () => {
  const t = useT(), t0 = INI["45"] + 2.6, t1 = INI["45"] + 6.4;
  if (t < t0 || t >= t1 + .4) return null;
  const k = Math.min(1, (t - t0) / .25), sai = Math.max(0, Math.min(1, (t1 + .4 - t) / .4)), px = 6;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: sai }}>
      <svg width="1920" height="400" style={{ imageRendering: "pixelated" }}>
        <defs><filter id="px"><feFlood x="0" y="0" width={px} height={px} /><feComposite width={px} height={px} /><feTile result="a" /><feComposite in="SourceGraphic" in2="a" operator="in" /><feMorphology operator="dilate" radius={px / 2} /></filter></defs>
        <text x="960" y="250" textAnchor="middle" filter="url(#px)" style={{ ...TITULO, fontSize: 190 * (0.9 + 0.1 * k), fill: VERDE }} >THE GREEN PATH</text>
      </svg>
      <div style={{ ...TERMINAL, position: "absolute", top: 700, fontSize: 40, color: CLARO, opacity: k }}>feito por Igor Anão</div>
    </AbsoluteFill>
  );
};
// legendas: nome de quem fala + texto (as falas ainda sem voz aparecem em itálico)
const Legendas: React.FC = () => {
  const ms = useT() * 1000;
  const l = (dados.legendas as Leg[]).find((x) => ms >= x.startMs && ms < x.endMs);
  if (!l) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 70 }}>
      <div style={{ ...TERMINAL, fontSize: 42, color: "#eafff0", background: "rgba(2,12,6,.8)", padding: "12px 28px", borderLeft: `6px solid ${VERDE}`, maxWidth: 1560, textAlign: "center", fontStyle: l.semVoz ? "italic" : "normal" }}>
        <span style={{ color: VERDE }}>{l.quem.toUpperCase()}: </span>{l.text}
      </div>
    </AbsoluteFill>
  );
};

export const Filme4: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <style>{fontes}</style>
      <Series>
        {PLANOS4.map(([nome, d]) => (
          <Series.Sequence key={nome} durationInFrames={Math.round(d * fps)}>
            <OffthreadVideo src={staticFile(`planos/${nome}.mp4`)} muted />
          </Series.Sequence>
        ))}
      </Series>
      <Sequence>
        <Ficha ini={INI["41"] + 10.3} fim={INI["41"] + 16.8} texto={"FICHA\n──────────────\nNOME: ADRYAN\nIDADE: 17 ANOS\nETNIA: PARDO\nFUNÇÃO: AGENTE TDA\nSTATUS: EM MISSÃO"} />
        <Ficha ini={INI["42"] + 1.0} fim={INI["42"] + 8.6} texto={"FICHA\n──────────────\nNOME: NICOLAS\nIDADE: 14 ANOS\nFUNÇÃO: NÃO INFORMADA\nSTATUS: EM MISSÃO"} />
        <Titulo /><Legendas />
      </Sequence>
      <Audio src={staticFile("trilha4.wav")} />
    </AbsoluteFill>
  );
};
