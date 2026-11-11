"""Monta os Reels do mês 2 no estilo do mês 1.

Uso: /usr/bin/python3 reel.py <M2S2|M2S4> <pasta_saida> <pasta_transcricoes>

- corta os trechos indicados, encurta pausas longas
- legenda palavra a palavra (Barlow Condensed, uma palavra em amarelo)
- título de abertura em caixa preta e cartões amarelos (Poppins)
- normaliza o áudio e gera capa 9:16 e recorte 4:5
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

T = os.path.expanduser("~/Movies/_Edicao_Kenneth_TRABALHO")
FF, FONTS = f"{T}/bin/ffmpeg", f"{T}/fonts"
JOB = os.path.expanduser("~/Downloads/job_1793366817055_{}.mp4")
YEL_ASS, INK_ASS = "&H0000C4F5", "&H001D1916"
YELLOW = (245, 196, 0)
CARD_TOP = 905  # cartões abaixo do queixo e acima da legenda (que começa em ~1290)

STOP = set("a o as os e é de do da dos das no na nos nas um uma uns umas que se por para pra com em ao à ele ela eu você "
           "seu sua isso esse essa ali aí mas mais não já nós vai foi tem ter só né então".split())

REELS = {
    "M2S2": dict(
        saida="M02S2_whatsapp_oficial",
        trechos=[("11", 1.7, 58.55)],
        abertura="O CELULAR DO ESCRITÓRIO VIROU GARGALO?",
        # (início, fim, texto) em segundos do vídeo final; \\N quebra linha; {b}...{/b} negrito
        cartoes=lambda m: [
            (m("11", 2.0), m("11", 10.3), "{b}BUSINESS{/b}\\Nnegócio pequeno"),
            (m("11", 10.4), m("11", 14.0), "{b}OFICIAL{/b}\\Nescala"),
            (m("11", 33.0), m("11", 58.55), "{b}3 SINAIS DE QUE É HORA DE TROCAR{/b}\\N"
             "várias pessoas no mesmo número\\Nconversa que se perde\\Nninguém sabe quem respondeu"),
        ],
        fim="Salve para decidir com a equipe",
        capa=("O CELULAR DO SEU ESCRITÓRIO VIROU", "GARGALO?"),
        foto=("11", 13.0),
    ),
    "M2S4": dict(
        saida="M02S4_whatsapp_caiu",
        trechos=[("17", 2.0, 16.7), ("16", 4.9, 29.8)],
        abertura="E SE O SEU WHATSAPP CAIR AMANHÃ?",
        cartoes=lambda m: [
            (m("17", 12.2), m("17", 16.7), "{b}TRAVOU POR DOIS MESES{/b}"),
            (m("16", 9.2), m("16", 14.2), "{b}Não dependa de{/b}\\N{b}um único canal{/b}"),
            (m("16", 14.3), m("16", 29.8), "{b}PLANO B EM 4 PASSOS{/b}\\N"
             "1. número reserva já ativo\\N2. outros canais divulgados\\N3. aviso pronto para o cliente\\N4. um responsável por acionar"),
        ],
        fim="Monte o seu plano B esta semana",
        capa=("E SE O SEU WHATSAPP", "CAIR AMANHÃ?"),
        foto=("16", 22.0),
    ),
}


def run(cmd):
    subprocess.run(cmd, check=True)


SR = 16000


def audio(n):
    """Áudio mono 16 kHz do corte, para achar os silêncios."""
    import numpy as np
    raw = subprocess.run([FF, "-v", "error", "-i", JOB.format(n), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="float32")


def silencio(sig, t0, t1):
    """Instante de menor energia (janela de 30 ms) entre t0 e t1."""
    import numpy as np
    t0, t1 = max(t0, 0.0), min(t1, len(sig) / SR - 0.02)
    best, best_t, t = None, t0, t0
    while t <= t1:
        i = int(t * SR)
        e = float(np.sqrt(np.mean(sig[i:i + int(0.03 * SR)] ** 2) + 1e-12))
        if best is None or e < best:
            best, best_t = e, t + 0.015
        t += 0.01
    return best_t


def keep_ranges(words, a, b, sig, gap=0.75, pad=0.22):
    """Trechos a manter dentro de [a,b], encurtando pausas maiores que `gap`.
    Todo ponto de corte é levado ao silêncio mais próximo, para não cortar palavra."""
    ws = [w for w in words if w[0] >= a - 0.05 and w[0] < b]
    rngs, start = [], a
    for prev, nxt in zip(ws, ws[1:]):
        if nxt[0] - prev[1] > gap:
            rngs.append((start, min(prev[1] + pad, b)))
            start = max(nxt[0] - pad, prev[1] + pad)
    rngs.append((start, b))
    out = []
    for ra, rb in rngs:
        # limites: nunca entrar na palavra anterior nem na seguinte
        ant = max([w[1] for w in words if w[1] <= ra + 0.02] or [0.0])
        prox = min([w[0] for w in words if w[0] >= rb - 0.02] or [len(sig) / SR])
        ra = silencio(sig, max(ra - 0.25, ant + 0.03), ra + 0.02)   # começo: procura antes da palavra
        rb = silencio(sig, rb - 0.02, min(rb + 0.3, prox - 0.1))    # fim: procura depois da palavra
        out.append((ra, rb))
    return out, ws


def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def card_png(texto, path):
    """Cartão amarelo de cantos arredondados. Linhas com {b}..{/b} em Poppins ExtraBold."""
    fb = ImageFont.truetype(f"{FONTS}/Poppins-ExtraBold.ttf", 50)
    fr = ImageFont.truetype(f"{FONTS}/Poppins-SemiBold.ttf", 42)
    linhas = []
    for ln in texto.split("\\N"):
        bold = "{b}" in ln
        linhas.append((ln.replace("{b}", "").replace("{/b}", ""), fb if bold else fr))
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    larg = max(tmp.textlength(t, font=f) for t, f in linhas)
    alt = [int(f.size * 1.3) for _, f in linhas]
    pw, ph = 44, 30
    img = Image.new("RGBA", (int(larg) + 2 * pw, sum(alt) + 2 * ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius=22, fill=YELLOW + (255,))
    y = ph
    for (t, f), h in zip(linhas, alt):
        d.text(((img.width - d.textlength(t, font=f)) / 2, y), t, font=f, fill=(22, 25, 29))
        y += h
    img.save(path)


CAP_FONT = ImageFont.truetype(f"{FONTS}/BarlowCondensed-ExtraBold.ttf", 82)
CAP_MAX = 820  # largura máxima da legenda em px (tela de 1080), sempre em uma linha


def largura(ws):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    return d.textlength(" ".join(w[2].upper() for w in ws), font=CAP_FONT)


HOOK_FONT = ImageFont.truetype(f"{FONTS}/BarlowCondensed-Black.ttf", 100)
HOOK_MAX = 820  # largura máxima de cada linha do título de abertura


def quebra_titulo(texto):
    """Quebra o título de abertura em linhas que cabem na tela (a legenda usa WrapStyle 2, sem quebra automática)."""
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    linhas, cur = [], ""
    for p in texto.split():
        tst = (cur + " " + p).strip()
        if cur and d.textlength(tst, font=HOOK_FONT) > HOOK_MAX:
            linhas.append(cur)
            cur = p
        else:
            cur = tst
    linhas.append(cur)
    return "\\N".join(linhas)


def grupos(words):
    """Agrupa 1 a 3 palavras por legenda, sempre em uma linha só, quebrando na pontuação."""
    out, cur = [], []
    for w in words:
        if cur and largura(cur + [w]) > CAP_MAX:
            out.append(cur)
            cur = []
        cur.append(w)
        if len(cur) == 3 or w[2][-1:] in ",.?!" or "..." in w[2]:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def destaque(g):
    cand = [i for i, w in enumerate(g) if w[2].strip(",.?!…").lower() not in STOP and len(w[2]) > 3]
    if len(g) < 2 or not cand:
        return None
    return max(cand, key=lambda i: len(g[i][2]))


def main(key, saida, txdir):
    R = REELS[key]
    os.makedirs(saida, exist_ok=True)
    words = {}
    for n, _, _ in R["trechos"]:
        ws = []
        for w in json.load(open(f"{txdir}/job{n}.json")):
            if w[2].startswith("%") and ws:  # "100 %" -> "100%"
                ws[-1] = [ws[-1][0], w[1], ws[-1][2] + w[2]]
            else:
                ws.append(w)
        words[n] = ws

    # trechos finais e mapa de tempo origem -> vídeo final
    segs, final_words, offset = [], [], 0.0
    maps = {}
    sigs = {n: audio(n) for n, _, _ in R["trechos"]}
    for n, a, b in R["trechos"]:
        rngs, ws = keep_ranges(words[n], a, b, sigs[n])
        for (ra, rb) in rngs:
            segs.append((n, ra, rb, offset))
            for w in ws:
                if ra - 0.01 <= w[0] < rb:
                    final_words.append([w[0] - ra + offset, min(w[1], rb) - ra + offset, w[2]])
            offset += rb - ra
        maps[n] = [(s[1], s[2], s[3]) for s in segs if s[0] == n]
    total = offset
    print('cortes:', [(n, round(a, 2), round(b, 2)) for n, a, b, _ in segs])

    def m(n, t):
        for ra, rb, off in maps[n]:
            if t <= rb:
                return max(t, ra) - ra + off
        ra, rb, off = maps[n][-1]
        return rb - ra + off

    # legenda .ass
    abertura_fim = 2.6
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "",
         "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: Cap,Barlow Condensed ExtraBold,82,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,5,2,2,60,60,560,1",
         f"Style: Hook,Barlow Condensed Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,3,16,0,5,90,90,0,1",
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    L.append(f"Dialogue: 2,{ts(0)},{ts(abertura_fim)},Hook,,0,0,0,,{{\\pos(540,1180)\\fad(0,200)}}{quebra_titulo(R['abertura'])}")
    gs = grupos(final_words)
    for gi, g in enumerate(gs):
        a, b = g[0][0], g[-1][1] + 0.05
        if gi + 1 < len(gs):  # nunca sobrepor com a legenda seguinte
            b = min(b, gs[gi + 1][0][0] - 0.01)
        if b <= abertura_fim:
            continue
        a = max(a, abertura_fim)
        h = destaque(g)
        txt = " ".join((f"{{\\c{YEL_ASS}}}{w[2].upper()}{{\\c&H00FFFFFF&}}" if i == h else w[2].upper()) for i, w in enumerate(g))
        L.append(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\an2\\pos(540,1360)}}{txt}")
    fim_ini = total - 2.4
    cards = []
    for a, b, t in R["cartoes"](m):
        a = max(a, abertura_fim + 0.1)
        b = min(b, fim_ini - 0.05)
        if b - a > 0.5:
            cards.append((a, b, t))
    cards.append((fim_ini, total, "{b}" + R["fim"] + "{/b}"))
    ass = os.path.join(saida, "_legenda.ass")
    open(ass, "w", encoding="utf-8").write("\n".join(L) + "\n")

    # montagem
    inputs, idx = [], {}
    for n, _, _ in R["trechos"]:
        if n not in idx:
            idx[n] = len(idx)
            inputs += ["-i", JOB.format(n)]
    fc, cat = [], ""
    for i, (n, a, b, _) in enumerate(segs):
        k = idx[n]
        fc.append(f"[{k}:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[{k}:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,"
                  f"afade=t=out:st={max(b - a - 0.03, 0):.3f}:d=0.03[a{i}]")
        cat += f"[v{i}][a{i}]"
    fc.append(f"{cat}concat=n={len(segs)}:v=1:a=1[vc][ac]")
    esc = ass.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    fc.append(f"[vc]ass=filename='{esc}':fontsdir='{FONTS}'[vs]")
    last = "vs"
    n_in = len(idx)
    for j, (a, b, t) in enumerate(cards):
        p = os.path.join(saida, f"_card{j}.png")
        card_png(t, p)
        k = n_in
        n_in += 1
        dur = b - a
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", p]
        fc.append(f"[{k}:v]format=rgba,fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st={max(dur - 0.2, 0):.3f}:d=0.2:alpha=1,"
                  f"setpts=PTS-STARTPTS+{a:.3f}/TB[c{j}]")
        fc.append(f"[{last}][c{j}]overlay=x=(W-w)/2:y={CARD_TOP}:eof_action=pass[o{j}]")
        last = f"o{j}"
    fc.append(f"[{last}]null[vo]")
    fc.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[ao]")
    mp4 = os.path.join(saida, R["saida"] + ".mp4")
    run([FF, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[ao]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", mp4])

    # capa 9:16 e 4:5
    n, t = R["foto"]
    png = os.path.join(saida, "_quadro.png")
    run([FF, "-v", "error", "-y", "-ss", str(t), "-i", JOB.format(n), "-frames:v", "1", png])
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
    ls = [(l, (255, 255, 255)) for l in linhas(branco)] + [(l, YELLOW) for l in linhas(amarelo)]
    y = 1180 - len(ls) * 150 // 2
    for l, cor in ls:
        w = d.textlength(l, font=big)
        d.text(((1080 - w) / 2, y), l, font=big, fill=cor, stroke_width=3, stroke_fill=(0, 0, 0))
        y += 150
    rod = "KENNETH RIBEIRO · GESTÃO DE ESCRITÓRIOS"
    d.text(((1080 - d.textlength(rod, font=small)) / 2, y + 40), rod, font=small, fill=(230, 230, 230))
    capa = os.path.join(saida, R["saida"] + "_capa.jpg")
    img.save(capa, quality=92)
    top = max(150, y + 40 + 60 - 1350)  # cabeça, título e assinatura no recorte 4:5
    img.crop((0, top, 1080, top + 1350)).save(capa.replace("_capa.jpg", "_capa_feed4x5.jpg"), quality=92)
    os.remove(png)
    print(key, f"{total:.1f}s", mp4)


if __name__ == "__main__":
    main(*sys.argv[1:4])
