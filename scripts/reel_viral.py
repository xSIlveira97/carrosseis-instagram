"""Reels no padrão viral do Painel Viral (ESPECIFICACAO.md, Editor VSL):

- gancho na tela nos primeiros 3 s, grande, com a parte forte em amarelo
- ritmo: pausas cortadas a seco e mudança visual a cada 2,5–4 s (troca de enquadramento / zoom)
- zoom de impacto nas frases-chave
- legenda palavra a palavra com a palavra ATUAL em amarelo, em uma linha, com "pop" na entrada
- trilha com abaixamento automático na fala + efeitos (whoosh no zoom, pop nos cartões)
- barra de progresso no topo; nada de imagem parada em silêncio

Uso: /usr/bin/python3 reel_viral.py <chave> <pasta_saida> <pasta_transcricoes>
As definições ficam em reels_viral_def.py.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

import reel as base  # mesmas funções de corte no silêncio, cartões e quebra de título
from reels_viral_def import REELS

FF, FONTS, YEL_ASS = base.FF, base.FONTS, base.YEL_ASS
MUSICA = os.path.expanduser("~/Movies/_Edicao_Kenneth_TRABALHO/musica")
SFX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")
CAP_FONT = ImageFont.truetype(f"{FONTS}/BarlowCondensed-ExtraBold.ttf", 96)
CAP_MAX = 860


def run(cmd):
    subprocess.run(cmd, check=True)


def gerar_sfx():
    """Efeitos gerados pelo próprio sistema (sem licença de terceiros)."""
    os.makedirs(SFX, exist_ok=True)
    w = os.path.join(SFX, "whoosh.wav")
    if not os.path.exists(w):
        run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "anoisesrc=d=0.38:c=pink:r=48000:a=0.5",
             "-af", "highpass=f=500,lowpass=f=6000,afade=t=in:d=0.18:curve=exp,afade=t=out:st=0.2:d=0.18,volume=0.7", w])
    p = os.path.join(SFX, "pop.wav")
    if not os.path.exists(p):
        run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=900:d=0.09:r=48000",
             "-af", "afade=t=out:st=0.02:d=0.07,volume=0.5", p])
    return w, p


def largura(ws):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    return d.textlength(" ".join(w[2].upper() for w in ws), font=CAP_FONT)


def grupos(words):
    out, cur = [], []
    for w in words:
        if cur and (largura(cur + [w]) > CAP_MAX or len(cur) == 3):
            out.append(cur)
            cur = []
        cur.append(w)
        if w[2][-1:] in ",.?!" or "..." in w[2]:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def tomadas(ws, ra, rb):
    """Divide um trecho contínuo em tomadas de 2,5–4 s, trocando de enquadramento na fronteira entre palavras."""
    cortes, ini = [], ra
    dentro = [w for w in ws if ra - 0.01 <= w[0] < rb]
    for i, w in enumerate(dentro[:-1]):
        dur = w[1] - ini
        prox = dentro[i + 1]
        fim_frase = w[2][-1:] in ",.?!"
        if (dur >= 2.5 and fim_frase) or dur >= 4.0:
            t = (w[1] + prox[0]) / 2
            cortes.append((ini, t))
            ini = t
    cortes.append((ini, rb))
    return cortes


def main(key, saida, txdir):
    R = REELS[key]
    os.makedirs(saida, exist_ok=True)
    whoosh, pop = gerar_sfx()

    words = {}
    for n, _, _ in R["trechos"]:
        ws = []
        for w in json.load(open(f"{txdir}/job{n}.json")):
            if w[2].startswith("%") and ws:
                ws[-1] = [ws[-1][0], w[1], ws[-1][2] + w[2]]
            else:
                ws.append(w)
        words[n] = ws
    sigs = {n: base.audio(n) for n, _, _ in R["trechos"]}

    # trechos de áudio (pausas cortadas a seco) e tomadas de vídeo (troca de enquadramento)
    faixas, shots, final_words, maps, off = [], [], [], {}, 0.0
    for n, a, b in R["trechos"]:
        rngs, ws = base.keep_ranges(words[n], a, b, sigs[n], gap=0.32, pad=0.1)
        for ra, rb in rngs:
            faixas.append((n, ra, rb))
            for sa, sb in tomadas(ws, ra, rb):
                shots.append((n, sa, sb, off + sa - ra))
            for w in ws:
                if ra - 0.01 <= w[0] < rb:
                    final_words.append([w[0] - ra + off, min(w[1], rb) - ra + off, w[2]])
            maps.setdefault(n, []).append((ra, rb, off))
            off += rb - ra
    falado = off
    cauda = R.get("cauda", 0.0)  # segundos finais sem fala: imagem com aproximação lenta + trilha (para o cartão final)
    total = off + cauda
    print("duração:", round(total, 1), "s | tomadas:", len(shots))

    def m(n, t):
        for ra, rb, o in maps[n]:
            if t <= rb:
                return max(t, ra) - ra + o
        ra, rb, o = maps[n][-1]
        return rb - ra + o

    # zoom: alterna 1.00/1.12; frases-chave em 1.28 (com whoosh)
    fortes = [(m(n, t0), m(n, t1)) for n, t0, t1 in R.get("frases_chave", [])]
    zooms, whooshes, alt = [], [], 0
    for i, (n, sa, sb, t) in enumerate(shots):
        meio = t + (sb - sa) / 2
        if any(a <= meio <= b for a, b in fortes):
            z = 1.28
        else:
            z = (1.0, 1.12)[alt % 2]
            alt += 1
        if i > 0 and z == 1.28 and zooms[-1] != 1.28:
            whooshes.append(max(t - 0.15, 0))
        zooms.append(z)

    # legendas
    gancho_fim = 3.0
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "",
         "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: Cap,Barlow Condensed ExtraBold,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,1,0,1,6,3,2,40,40,0,1",
         "Style: Hook,Barlow Condensed Black,112,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,3,18,0,5,60,60,0,1",
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    if R.get("gancho"):
        branco, amarelo = R["gancho"]
        quebra = lambda t: t if "\\N" in t else base.quebra_titulo(t)  # \\N no texto = quebra manual
        hook = quebra(branco)
        hook += "\\N{\\c" + YEL_ASS + "}" + quebra(amarelo).replace("\\N", "\\N{\\c" + YEL_ASS + "}")
        L.append(f"Dialogue: 2,{base.ts(0)},{base.ts(gancho_fim)},Hook,,0,0,0,,"
                 f"{{\\pos(540,1060)\\fscx70\\fscy70\\t(0,140,\\fscx100\\fscy100)\\fad(0,180)}}{hook}")
    else:
        gancho_fim = 0.0
    sem = [(m(n, a), m(n, b)) for n, a, b in R.get("sem_legenda", [])]  # ex.: cartão de título do próprio VSL
    gs = grupos(final_words)
    for gi, g in enumerate(gs):
        g_fim = min(g[-1][1] + 0.05, gs[gi + 1][0][0] - 0.01) if gi + 1 < len(gs) else g[-1][1] + 0.3
        for wi, w in enumerate(g):
            a = w[0]
            b = g[wi + 1][0] if wi + 1 < len(g) else g_fim
            if b <= a or any(x0 <= a < x1 for x0, x1 in sem):
                continue
            txt = " ".join((f"{{\\c{YEL_ASS}}}{x[2].upper()}{{\\c&H00FFFFFF&}}" if j == wi else x[2].upper())
                           for j, x in enumerate(g))
            anim = "\\fscx85\\fscy85\\t(0,90,\\fscx100\\fscy100)" if wi == 0 else ""
            L.append(f"Dialogue: 1,{base.ts(a)},{base.ts(b)},Cap,,0,0,0,,{{\\an2\\pos(540,{R.get('legenda_y', 1400)}){anim}}}{txt}")
    ass = os.path.join(saida, "_legenda.ass")
    open(ass, "w", encoding="utf-8").write("\n".join(L) + "\n")

    # cartões (depois do gancho); o último é a chamada final
    fim_txt = R.get("fim")
    fim_ini = total - (R.get("fim_dur", 2.4) if fim_txt else 0.0)
    cards = []
    for a, b, t in R.get("cartoes", lambda m: [])(m):
        a, b = max(a, gancho_fim + 0.1), min(b, fim_ini - 0.05)
        if b - a > 0.6:
            cards.append((a, b, t))
    if fim_txt:
        cards.append((fim_ini, total, fim_txt if "{b}" in fim_txt else "{b}" + fim_txt + "{/b}"))

    # ---- montagem
    inputs, idx = [], {}
    for n, _, _ in R["trechos"]:
        if n not in idx:
            idx[n] = len(idx)
            inputs += ["-i", base.src(n)]
    fc = []
    vcat = ""
    for i, ((n, sa, sb, _), z) in enumerate(zip(shots, zooms)):
        k = idx[n]
        crop = "" if z == 1.0 else f"crop=w=iw/{z}:h=ih/{z}:x=(iw-ow)/2:y=(ih-oh)*0.30,"
        va, pad = sa, ""
        for sn, t0, t1 in R.get("evitar_video", []):  # ex.: tomada de outra pessoa no começo do corte
            if sn == n and t0 <= sa < t1 < sb:
                va, pad = t1, f"tpad=start_mode=clone:start_duration={t1 - sa:.3f},"
        fc.append(f"[{k}:v]trim=start={va:.3f}:end={sb:.3f},setpts=PTS-STARTPTS,{pad}{crop}scale=1080:1920,setsar=1,fps=30[v{i}]")
        vcat += f"[v{i}]"
    if cauda:
        f0 = f"{falado:.3f}"
        fc.append(f"{vcat}concat=n={len(shots)}:v=1:a=0,tpad=stop_mode=clone:stop_duration={cauda:.3f},"
                  f"scale=w='trunc(1080*(1+0.06*max(0,t-{f0})/{cauda:.3f})/2)*2':h=-2:eval=frame,"
                  f"crop=1080:1920:(iw-1080)/2:(ih-1920)*0.3,setsar=1[vc]")
    else:
        fc.append(f"{vcat}concat=n={len(shots)}:v=1:a=0[vc]")
    acat = ""
    for i, (n, ra, rb) in enumerate(faixas):
        k = idx[n]
        fc.append(f"[{k}:a]atrim=start={ra:.3f}:end={rb:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=11,"
                  f"aresample=48000,afade=t=in:d=0.015,afade=t=out:st={max(rb - ra - 0.02, 0):.3f}:d=0.02[a{i}]")
        acat += f"[a{i}]"
    fc.append(f"{acat}concat=n={len(faixas)}:v=0:a=1" + (f",apad=pad_dur={cauda:.3f}" if cauda else "") + ",asplit=2[voz][sc]")

    esc = ass.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    fc.append(f"[vc]ass=filename='{esc}':fontsdir='{FONTS}',"
              f"drawbox=x=0:y=0:w=iw*t/{total:.3f}:h=12:color=0xF5C400@0.95:t=fill[vs]")
    last, n_in = "vs", len(idx)
    for j, (a, b, t) in enumerate(cards):
        p = os.path.join(saida, f"_card{j}.png")
        base.card_png(t, p)
        dur = b - a
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", p]
        fc.append(f"[{n_in}:v]format=rgba,fade=t=in:st=0:d=0.15:alpha=1,fade=t=out:st={max(dur - 0.2, 0):.3f}:d=0.2:alpha=1,"
                  f"setpts=PTS-STARTPTS+{a:.3f}/TB[c{j}]")
        fc.append(f"[{last}][c{j}]overlay=x=(W-w)/2:y={R.get('card_top', base.CARD_TOP)}:eof_action=pass[o{j}]")
        last, n_in = f"o{j}", n_in + 1
    fc.append(f"[{last}]null[vo]")

    # trilha com abaixamento sob a voz
    inputs += ["-stream_loop", "-1", "-i", os.path.join(MUSICA, R["musica"])]
    mus = n_in
    n_in += 1
    fc.append(f"[{mus}:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,aresample=48000,volume={R.get('musica_vol', 0.5)},"
              f"afade=t=in:d=0.4,afade=t=out:st={max(total - 0.8, 0):.3f}:d=0.8[mus]")
    fc.append("[mus][sc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400:makeup=1[duck]")
    # efeitos: whoosh no gancho e nos zooms fortes, pop em cada cartão
    sfx = [(whoosh, 0.0)] + [(whoosh, t) for t in whooshes] + [(pop, a) for a, _, _ in cards]
    mix = "[voz][duck]"
    for j, (f, t) in enumerate(sfx):
        inputs += ["-i", f]
        ms = int(t * 1000)
        fc.append(f"[{n_in}:a]aresample=48000,adelay={ms}|{ms}[s{j}]")
        mix += f"[s{j}]"
        n_in += 1
    fc.append(f"{mix}amix=inputs={2 + len(sfx)}:normalize=0:duration=first,alimiter=limit=0.89[ao]")

    mp4 = os.path.join(saida, R["saida"] + ".mp4")
    if not os.environ.get("SO_CAPA"):
        run([FF, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[ao]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30",
             "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", mp4])
    capa(R, saida)
    print(key, f"{total:.1f}s", mp4)


def capa(R, saida):
    """Capa 9:16 e recorte 4:5 (mesmo modelo dos Reels anteriores)."""
    n, t = R["foto"]
    png = os.path.join(saida, "_quadro.png")
    run([FF, "-v", "error", "-y", "-ss", str(t), "-i", base.src(n), "-frames:v", "1", png])
    img = Image.open(png).convert("RGB").resize((1080, 1920))
    grad = Image.new("L", (1, 1920))
    for y in range(1920):
        grad.putpixel((0, y), int(max(0, min(1, (y - 700) / 700)) * 200))
    img = Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, grad.resize(img.size))
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(f"{FONTS}/BarlowCondensed-Black.ttf", 150)
    small = ImageFont.truetype(f"{FONTS}/Poppins-SemiBold.ttf", 34)

    def linhas(texto, largura=930):
        out, cur = [], ""
        for p in texto.split():
            tst = (cur + " " + p).strip()
            if d.textlength(tst, font=big) <= largura:
                cur = tst
            else:
                out.append(cur)
                cur = p
        out.append(cur)
        return out

    branco, amarelo = R["capa"]
    ls = [(l, (255, 255, 255)) for l in linhas(branco)] + [(l, base.YELLOW) for l in linhas(amarelo)]
    y = R.get("capa_y", 1180) - len(ls) * 150 // 2
    for l, cor in ls:
        w = d.textlength(l, font=big)
        d.text(((1080 - w) / 2, y), l, font=big, fill=cor, stroke_width=3, stroke_fill=(0, 0, 0))
        y += 150
    rod = "KENNETH RIBEIRO · GESTÃO DE ESCRITÓRIOS"
    d.text(((1080 - d.textlength(rod, font=small)) / 2, y + 40), rod, font=small, fill=(230, 230, 230))
    out = os.path.join(saida, R["saida"] + "_capa.jpg")
    img.save(out, quality=92)
    top = max(150, y + 40 + 60 - 1350)
    img.crop((0, top, 1080, top + 1350)).save(out.replace("_capa.jpg", "_capa_feed4x5.jpg"), quality=92)
    os.remove(png)


if __name__ == "__main__":
    main(*sys.argv[1:4])
