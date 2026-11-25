"""Gera videos/60-ep1-posto/index.html a partir do plano 43 APROVADO (que fica intacto): os primeiros 24,4 s são idênticos.
Rever 2 (diretor): menos tempo no frentista; o Adryan investiga de verdade (sai olhando o teto, agacha, pega a pedra, olha, encara o escuro).
uso: python3 tools/gerar_cena60.py"""
s = open('videos/43-posto/index.html').read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("""<!-- v4 PLANO 3 · 0:26–0:48 · POSTO: chega e para na bomba; frentista vem à janela ("Boa noite. Completa pra mim."), abastece calado
     ("Movimento fraco hoje, hein?" sem resposta; "Beleza... também não precisa conversar."); Nicolas imóvel com a maleta; Adryan paga, frentista vai embora. -->
<script>VIDEO={w:1920,h:1080,fps:30,dur:24}</script>""",
"""<!-- EPISÓDIO 1 (reformulado) · CENA 60 · POSTO — GERADA por tools/gerar_cena60.py a partir do plano 43 do v4 (aprovado, intacto):
     até 24,4 s é idêntica. Depois (rev. 2): o frentista vai pro alojamento (um plano só) e entra lá no fundo ENQUANTO a pedrinha vem do
     escuro e bate no teto do carro; a porta dele bate fora de quadro. O Adryan se assusta, abre a porta, sai olhando o teto, vai até a
     traseira, AGACHA e pega a pedra, levanta olhando pra ela e encara o escuro de onde ela veio (continua na cena 61).
     ?cam=x,y,z,ax,ay,az,fov força uma câmera (inspeção). -->
<script>VIDEO={w:1920,h:1080,fps:30,dur:39}</script>""")
rep("import * as V from '../../lib/v4.js';", "import * as V from '../../lib/v4.js';\nimport * as E from '../../lib/ep1.js';\nimport * as E4 from '../../lib/elenco4.js';")
rep("""  const { car } = D, Me = C.Me; Me.obj.visible = false;""",
"""  const { car } = D, Me = C.Me; Me.obj.visible = false;
  // ── EP1 ──
  const AL = await E.alojamento(C), q = new URLSearchParams(location.search), camQ = q.get('cam')?.split(',').map(Number);
  const AdF = await E4.ator('adryan'); S.scene.add(AdF.obj); AdF.obj.visible = false;          // Adryan DE PÉ, fora do carro
  const pedra = await E.prop('rock_09', { altura: .04 }); S.scene.add(pedra); pedra.visible = false;
  const PEDRA = [v3(8.6, 1.2, -5.4), v3(-.1, 1.47, -.05), v3(-1.52, .04, -1.82)];          // mão do Metalis no escuro → teto do carro → chão atrás da porta
  const FORA = [AL.fora[0], AL.fora[2]], DENTRO = [AL.dentro[0], AL.dentro[2]], MESA = [AL.mesa[0], AL.mesa[2]];
  const AD_PORTA = [.62, -1.5], AD_TRAS = [-1.0, -1.8], ROT_TRAS = Math.atan2(AD_TRAS[0] - AD_PORTA[0], AD_TRAS[1] - AD_PORTA[1]);
  const ESCURO = Math.atan2(PEDRA[0].x - AD_TRAS[0], PEDRA[0].z - AD_TRAS[1]);
  const T_AG = 32.8, T_SOBE = 34.5, RISE = 1.15;                                              // agacha (32,8–33,9) · pega (33,5–34,2) · levanta (34,5–35,65)""")
rep("""    else { anda = V.caminhar(Fr, JANELA, [4.5, -6.5], t, 24.4, 28.8, { de: 0 }); }""",
"""    // EP1 — ALOJAMENTO: janela → porta (24,4–27,4) · vira, mão na maçaneta, abre (27,4–28,0) · entra (28,0–28,9) · a porta bate (29,0)
    //       · lá dentro vai até a mesa e senta (fora de quadro)
    else if (t < 27.4) { anda = V.caminhar(Fr, JANELA, FORA, t, 24.4, 27.4, { de: 0 }); }
    else if (t < 28.0) { Fr.obj.position.set(FORA[0], 0, FORA[1]); Fr.obj.rotation.y = angLerp(Math.atan2(FORA[0] - JANELA[0], FORA[1] - JANELA[1]), Math.PI, P.suave(27.4, 27.7, t)); Fr.pose('idle', t); }
    else if (t < 29.3) { anda = V.caminhar(Fr, FORA, DENTRO, t, 28.0, 28.9, { de: Math.PI }); if (!anda) { Fr.obj.rotation.y = Math.PI; Fr.pose('idle', t); } }
    else if (t < 31.3) { anda = V.caminhar(Fr, DENTRO, MESA, t, 29.3, 31.3, { de: Math.PI }); }
    else { Fr.obj.position.set(MESA[0], 0, MESA[1]); Fr.obj.rotation.y = .1; const k = t - 31.3, d = Fr.dur('u_Sitting_Enter'); Fr.pose(k < d ? 'u_Sitting_Enter' : 'u_Sitting_Idle_Loop', k < d ? k : k - d); }""")
rep("""    Me.obj.visible = false;
    // câmeras""",
"""    Me.obj.visible = false;
    // ── EP1: porta do alojamento · pedrinha · Adryan sai e investiga ──
    AL.atualizar(t);
    AL.porta(P.suave(27.6, 28.1, t) * (1 - P.suave(28.85, 29.1, t) ** 2));                     // abre; FECHA com força (bate às 29,0)
    const maca = P.suave(27.45, 27.65, t) * (1 - P.suave(28.05, 28.3, t));
    if (maca > 0 && t < 28.4) { const r = Fr.obj.rotation.y; V.pegar(Fr, 'R', AL.macaneta(), frente(r).add(v3(0, -.3, 0)).normalize(), v3(0, 1, 0), direita(r).multiplyScalar(.8).add(v3(0, -.6, 0)), maca, .8); }
    // pedra: sai do escuro (27,9) → bate no teto (28,5) → quica e cai atrás da porta do motorista (29,05) → na mão do Adryan (34,0)
    pedra.visible = t > 27.9;
    const naMao = t >= 34.0;
    if (pedra.visible && !naMao) { const [a, b, c] = PEDRA; let p;
      if (t < 28.5) { const u = (t - 27.9) / .6; p = a.clone().lerp(b, u); p.y += Math.sin(Math.PI * u) * 1.5; }
      else if (t < 29.05) { const u = (t - 28.5) / .55; p = b.clone().lerp(c, u); p.y = P.lerp(b.y, c.y, u * u) + Math.sin(Math.PI * u) * .3; }
      else p = c;
      pedra.position.copy(p); if (t < 29.05) pedra.rotation.set(t * 9, t * 7, 0); }
    // Adryan no carro: susto com a pancada (28,5) — encolhe, olha pro teto, olha em volta; abre a porta (30,3–31,0)
    const susto = P.suave(28.52, 28.7, t) * (1 - P.suave(29.9, 30.3, t)), volta = Math.sin(Math.max(0, t - 29.1) * 2.4) * P.suave(29.1, 29.4, t) * (1 - P.suave(29.9, 30.2, t));
    if (t < 31.0) { V.girar(D.Ad, 'spine.005', [1, 0, 0], -.42 * susto); V.girar(D.Ad, 'spine.005', [0, 1, 0], .55 * volta); V.girar(D.Ad, 'spine.003', [1, 0, 0], .1 * P.suave(28.52, 28.62, t) * (1 - P.suave(28.7, 29.0, t))); }
    car.abrirPorta(P.suave(30.3, 31.0, t));
    const fora2 = t >= 30.95; D.Ad.obj.visible = !fora2; AdF.obj.visible = fora2;
    if (fora2) {
      let cab = 0;
      if (t < 32.8) {                                                                           // sai andando pra traseira, olhando o teto
        if (!V.caminhar(AdF, AD_PORTA, AD_TRAS, t, 30.95, 32.8, { de: ROT_TRAS - .5 })) AdF.pose('idle', t);
        cab = -.42 * P.suave(30.95, 31.3, t) * (1 - P.suave(32.1, 32.6, t)) + .35 * P.suave(32.3, 32.8, t);   // olha pra cima → acha a pedra no chão
      } else if (t < 36.7) {                                                                    // agacha, pega, levanta olhando pra pedra
        AdF.obj.position.set(AD_TRAS[0], 0, AD_TRAS[1]); AdF.obj.rotation.y = ROT_TRAS;
        const k = t < T_SOBE ? RISE * (1 - P.suave(T_AG, T_AG + 1.1, t)) : Math.min(RISE, t - T_SOBE);
        AdF.pose('m_crouch_rise_up', k, 'idle', P.suave(T_SOBE + RISE - .2, T_SOBE + RISE + .3, t), t);
        cab = .45 * (1 - P.suave(36.3, 36.7, t));
      } else {                                                                                  // vira pro escuro de onde veio a pedra
        AdF.obj.position.set(AD_TRAS[0], 0, AD_TRAS[1]); AdF.obj.rotation.y = angLerp(ROT_TRAS, ESCURO, P.suave(36.7, 37.5, t));
        AdF.pose('m_idle_looking_around', t - 36.7, 'idle', 1 - P.suave(36.8, 37.6, t), t);
      }
      AdF.obj.updateMatrixWorld(true);
      if (cab) V.girar(AdF, 'spine.005', [1, 0, 0], cab);
      const r = AdF.obj.rotation.y;
      // mão direita: desce até a pedra (33,4–34,0), fecha nela; depois traz pra frente do peito pra olhar (35,4–36,5)
      const alcanca = P.suave(33.35, 33.95, t) * (1 - P.suave(34.3, 34.8, t)), olha = P.suave(35.3, 35.9, t) * (1 - P.suave(36.4, 37.0, t));
      if (alcanca > 0) V.pegar(AdF, 'R', PEDRA[2].clone().add(v3(0, .03, 0)), v3(0, -1, 0).add(frente(r).multiplyScalar(.6)).normalize(), frente(r), direita(r).multiplyScalar(.6).add(v3(0, -.2, 0)), alcanca, .9);
      if (olha > 0) { const peito = AdF.obj.position.clone().add(v3(0, 1.18, 0)).addScaledVector(frente(r), .3).addScaledVector(direita(r), .04);
        V.pegar(AdF, 'R', peito, frente(r).add(v3(0, .3, 0)).normalize(), v3(0, 1, 0), direita(r).add(v3(0, -.8, 0)), olha, .9); }
      if (naMao) { AdF.obj.updateMatrixWorld(true); const h = AdF.osso('hand.R'), m = AdF.osso('f_middle.01.R');
        pedra.position.copy(h.getWorldPosition(v3())).lerp(m.getWorldPosition(v3()), .8); pedra.rotation.set(.4, r, 0); }
    }
    // câmeras""")
rep("""    if (t < 5) cam([14, 6, 13], [P.lerp(-10, 0, ch), .8, P.lerp(7, -1, ch)], 40);""",
"""    if (camQ) cam(camQ.slice(0, 3), camQ.slice(3, 6), camQ[6]);
    else if (t < 5) cam([14, 6, 13], [P.lerp(-10, 0, ch), .8, P.lerp(7, -1, ch)], 40);""")
rep("""    else cam([1.8, 1.6, -4.2], [.2, 1.0, -.8], 42);""",
"""    else if (t < 26.4) cam([4.6, 1.9, 2.6], [P.lerp(1.6, 2.0, P.suave(24.4, 26.4, t)), 1.05, -6.4], 44);        // o frentista vai pro alojamento
    else if (t < 28.75) cam([-1.35, 1.8, .95], [4.2, 1.25, -3.0], 50);                                        // do teto: ele entra lá no fundo; a pedra vem do escuro e bate
    else if (t < 30.3) cam([.1, 1.1, -1.4], [.3, 1.3, -.25], 44);                                          // Adryan se assusta (a porta do alojamento bate fora de quadro)
    else if (t < 31.0) cam([1.9, 1.4, -3.3], [.35, 1.0, -1.0], 46);                                           // a porta do carro abre
    else if (t < 32.8) { const a = AdF.obj.position; cam([P.lerp(1.6, .4, P.suave(31.0, 32.8, t)), 1.55, -4.0], [a.x, 1.35, a.z], 42); }   // sai olhando o teto, vai pra traseira
    else if (t < 35.3) cam([-2.75, .55, -1.15], [-1.25, .5, -1.9], 46);                                        // rente ao chão: agacha e pega a pedra
    else if (t < 36.8) cam([-2.55, 1.5, -2.7], [-1.0, 1.3, -1.8], 42);                                    // de frente: olha a pedra na mão
    else { const a = AdF.obj.position; cam([a.x - 1.1, 1.65, a.z + 1.1], [PEDRA[0].x * .45, 1.1, PEDRA[0].z * .5], 44); }   // por trás dele: o escuro de onde ela veio""")
open('videos/60-ep1-posto/index.html', 'w').write(s); print('ok')
