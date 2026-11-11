"""Desenha os carrosséis (1080x1350, JPEG) a partir de carrosseis_m2.py.

Uso: <python com Pillow> plano/render_carrossel.py <pasta_saida>
Gera <saida>/<nome>/01.jpg … e <saida>/<nome>/legenda.txt
"""
import io
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from carrosseis_m2 import CARROSSEIS  # noqa: E402

FONTS = os.path.expanduser("~/Movies/_Edicao_Kenneth_TRABALHO/fonts")
FF = os.path.expanduser("~/Movies/_Edicao_Kenneth_TRABALHO/bin/ffmpeg")
W, H = 1080, 1350
M = 84  # margem lateral
INK, PAPER, MUTED, LINE = (22, 25, 29), (242, 243, 245), (92, 99, 108), (214, 217, 222)
YELLOW, WHITE, DARK = (245, 196, 0), (255, 255, 255), (20, 22, 26)
HANDLE = "@eusoukennethribeiro"


def font(nome, tam):
    return ImageFont.truetype(os.path.join(FONTS, nome), int(tam))


def quebra(draw, texto, f, largura):
    linhas = []
    for par in texto.split("\n"):
        atual = ""
        for palavra in par.split():
            teste = (atual + " " + palavra).strip()
            if draw.textlength(teste, font=f) <= largura:
                atual = teste
            else:
                if atual:
                    linhas.append(atual)
                atual = palavra
        linhas.append(atual)
    return linhas


def bloco(draw, x, y, texto, f, cor, largura, entre=1.32, desenhar=True):
    alt = int(f.size * entre)
    for ln in quebra(draw, texto, f, largura):
        if desenhar:
            draw.text((x, y), ln, font=f, fill=cor)
        y += alt
    return y


def quadro(video, seg):
    raw = subprocess.run([FF, "-v", "error", "-ss", str(seg), "-i", video, "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    esc = W / img.width
    img = img.resize((W, int(img.height * esc)))
    return img


def rodape(draw, n, total, escuro=False):
    f = font("Poppins-SemiBold.ttf", 26)
    cor = (200, 203, 208) if escuro else MUTED
    draw.line([(M, H - 92), (W - M, H - 92)], fill=(60, 64, 70) if escuro else LINE, width=2)
    draw.text((M, H - 74), HANDLE, font=f, fill=cor)
    t = f"{n}/{total}"
    draw.text((W - M - draw.textlength(t, font=f), H - 74), t, font=f, fill=cor)


def capa(c, total):
    foto = quadro(*c["foto"])
    topo = 0 if foto.height - H < 200 else 120
    img = foto.crop((0, topo, W, topo + H))
    # escurece a metade de baixo para o título
    grad = Image.new("L", (1, H))
    for yy in range(H):
        grad.putpixel((0, yy), int(max(0, min(235, (yy - H * 0.32) / (H * 0.45) * 235))))
    preto = Image.new("RGB", (W, H), DARK)
    img = Image.composite(preto, img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    tag = "SALVE PARA USAR DEPOIS"
    ft = font("Poppins-ExtraBold.ttf", 26)
    tw = d.textlength(tag, font=ft)
    d.rectangle([W - M - tw - 36, 64, W - M, 64 + 56], fill=YELLOW)
    d.text((W - M - tw - 18, 76), tag, font=ft, fill=INK)
    titulo, sub = c["capa"]
    for tam in (128, 116, 104, 94):
        ftit = font("BarlowCondensed-Black.ttf", tam)
        linhas = quebra(d, titulo, ftit, W - 2 * M)
        if len(linhas) <= 4:
            break
    fsub = font("Poppins-SemiBold.ttf", 36)
    alt_sub = len(quebra(d, sub, fsub, W - 2 * M)) * int(36 * 1.35)
    y = H - 130 - alt_sub - 30 - len(linhas) * int(ftit.size * 0.98)
    for i, ln in enumerate(linhas):
        d.text((M, y), ln, font=ftit, fill=YELLOW if i == len(linhas) - 1 else WHITE)
        y += int(ftit.size * 0.98)
    bloco(d, M, y + 26, sub, fsub, (225, 227, 230), W - 2 * M, 1.35)
    rodape(d, 1, total, escuro=True)
    return img


def conteudo(lam, n, total, escala, y0=92):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    larg = W - 2 * M
    y = y0
    if lam.get("kicker"):
        fk = font("Poppins-ExtraBold.ttf", 32 * escala)
        k = lam["kicker"].upper()
        kw = d.textlength(k, font=fk)
        d.rectangle([M, y, M + kw + 32, y + fk.size + 22], fill=YELLOW)
        d.text((M + 16, y + 9), k, font=fk, fill=INK)
        y += fk.size + 22 + 34
    if lam.get("titulo"):
        ft = font("BarlowCondensed-Black.ttf", 108 * escala)
        for ln in quebra(d, lam["titulo"], ft, larg):
            d.text((M, y), ln, font=ft, fill=INK)
            y += int(ft.size * 0.98)
        y += int(34 * escala)
    fb = font("Poppins-SemiBold.ttf", 44 * escala)
    fbb = font("Poppins-ExtraBold.ttf", 46 * escala)
    for par in lam.get("texto", []):
        y = bloco(d, M, y, par, fb, (44, 49, 56), larg) + int(18 * escala)
    for rot, exp in lam.get("itens", []):
        d.rectangle([M, y + 8, M + 10, y + 8 + int(fbb.size * 1.1)], fill=YELLOW)
        y = bloco(d, M + 34, y, rot, fbb, INK, larg - 34, 1.25)
        y = bloco(d, M + 34, y, exp, fb, MUTED, larg - 34, 1.3) + int(22 * escala)
    if lam.get("tabela"):
        linhas = lam["tabela"]
        cols = len(linhas[0])
        cw = [larg * 0.46] + [larg * 0.54 / (cols - 1)] * (cols - 1)
        rh = int(fb.size * 1.9)
        for i, row in enumerate(linhas):
            cab, ult = i == 0, i == len(linhas) - 1
            if cab:
                d.rectangle([M, y, W - M, y + rh], fill=INK)
            elif ult:
                d.rectangle([M, y, W - M, y + rh], fill=(228, 230, 234))
            x = M
            for j, cel in enumerate(row):
                f = fbb if cab or ult else fb
                cor = WHITE if cab else INK
                tx = x + 22 if j == 0 else x + cw[j] - d.textlength(cel, font=f) - 22
                d.text((tx, y + (rh - f.size) / 2 - 4), cel, font=f, fill=cor)
                x += cw[j]
            y += rh
            if not cab:
                d.line([(M, y), (W - M, y)], fill=LINE, width=2)
        y += int(26 * escala)
    if lam.get("caixa"):
        fc = font("Poppins-ExtraBold.ttf", 50 * escala)
        alt = bloco(d, 0, 0, lam["caixa"], fc, INK, larg - 72, 1.3, desenhar=False)
        d.rectangle([M, y, W - M, y + alt + 64], fill=YELLOW)
        bloco(d, M + 36, y + 30, lam["caixa"], fc, INK, larg - 72, 1.3)
        y += alt + 64 + int(26 * escala)
    for par in lam.get("depois", []):  # texto que vem depois da caixa (ex.: exemplo depois da fórmula)
        y = bloco(d, M, y, par, fb, (44, 49, 56), larg) + int(18 * escala)
    if lam.get("nota"):
        fn = font("Poppins-SemiBold.ttf", 30 * escala)
        y = bloco(d, M, y + 4, lam["nota"], fn, MUTED, larg, 1.35)
    rodape(d, n, total)
    return img, y


def final(c, total):
    img = Image.new("RGB", (W, H), DARK)
    foto = quadro(*c["foto"]).crop((0, 170, W, 930))
    img.paste(foto, (0, 0))
    grad = Image.new("L", (1, 760))
    for yy in range(760):
        grad.putpixel((0, yy), int(max(0, min(255, (yy - 520) / 240 * 255))))
    img.paste(Image.new("RGB", (W, 760), DARK), (0, 0), grad.resize((W, 760)))
    d = ImageDraw.Draw(img)
    ft = font("BarlowCondensed-Black.ttf", 104)
    y = 720
    for ln in quebra(d, c["fim"].upper(), ft, W - 2 * M):
        d.text((M, y), ln, font=ft, fill=YELLOW)
        y += int(104 * 0.98)
    fs = font("Poppins-SemiBold.ttf", 34)
    bloco(d, M, y + 30, f"Toda semana, uma parte da gestão do escritório explicada na prática. Siga {HANDLE}.",
          fs, (225, 227, 230), W - 2 * M, 1.4)
    rodape(d, total, total, escuro=True)
    return img


def main(saida):
    for nome, c in CARROSSEIS.items():
        pasta = os.path.join(saida, nome)
        os.makedirs(pasta, exist_ok=True)
        total = len(c["laminas"]) + 2
        capa(c, total).save(os.path.join(pasta, "01.jpg"), quality=92)
        for i, lam in enumerate(c["laminas"], 2):
            for escala in (1.0, 0.93, 0.86, 0.8, 0.74, 0.68):
                img, fim_y = conteudo(lam, i, total, escala)
                if fim_y < H - 130:
                    break
            else:
                print("AVISO: texto apertado em", nome, i)
            sobra = H - 130 - fim_y
            if sobra > 120:  # distribui o conteúdo na altura em vez de deixar tudo no topo
                img, _ = conteudo(lam, i, total, escala, 92 + int(sobra * 0.35))
            img.save(os.path.join(pasta, f"{i:02d}.jpg"), quality=92)
        final(c, total).save(os.path.join(pasta, f"{total:02d}.jpg"), quality=92)
        open(os.path.join(pasta, "legenda.txt"), "w").write(c["legenda"] + "\n")
        print("ok", nome, total, "lâminas")


if __name__ == "__main__":
    main(sys.argv[1])
