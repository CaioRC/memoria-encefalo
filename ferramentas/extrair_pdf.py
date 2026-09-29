"""Extrai as estruturas do encéfalo de Fonte.pdf para dados/estruturas.json + img/*.jpg.

O PDF segue um padrão de 4 páginas por estrutura (em ordem variável):
  - página do NOME (texto curto, sem marcadores)
  - página da FUNÇÃO (texto com marcadores desenhados como pequenos quadrados)
  - página da IMAGEM (uma figura; às vezes com rótulos ou um "?" colorido)
  - página da FUNÇÃO repetida (ignorada)

Uso:  python ferramentas/extrair_pdf.py
"""
import io
import json
import re
import unicodedata
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageChops

RAIZ = Path(__file__).resolve().parent.parent
PDF = RAIZ / "Fonte.pdf"
SAIDA_JSON = RAIZ / "dados" / "estruturas.json"
PASTA_IMG = RAIZ / "img"

# Nomes do PDF (maiúsculas, sem acento) -> nome de exibição.
NOMES = {
    "LOBO FRONTAL": "Lobo Frontal",
    "LOBO PARIETAL": "Lobo Parietal",
    "LOBO DA INSULA": "Lobo da Ínsula",
    "LOBO TEMPORAL": "Lobo Temporal",
    "LOBO OCCIPITAL": "Lobo Occipital",
    "HIPOTALAMO": "Hipotálamo",
    "MESENCEFALO": "Mesencéfalo",
    "PONTE": "Ponte",
    "BULBO": "Bulbo",
    "TALAMO": "Tálamo",
    "GIRO PRE-CENTRAL": "Giro Pré-central",
    "GIRO POS-CENTRAL": "Giro Pós-central",
}


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def marcadores(pagina):
    """Quadradinhos preenchidos usados como bullets (não o fundo da página)."""
    return [d["rect"] for d in pagina.get_drawings() if d["rect"].width < 15 and d["rect"].height < 15]


def linhas(pagina):
    out = []
    for bloco in pagina.get_text("dict")["blocks"]:
        for linha in bloco.get("lines", []):
            texto = "".join(s["text"] for s in linha["spans"])
            if texto.strip():
                tamanho = max(s["size"] for s in linha["spans"])
                out.append({"bbox": fitz.Rect(linha["bbox"]), "texto": texto, "tamanho": tamanho})
    return sorted(out, key=lambda l: (round(l["bbox"].y0), l["bbox"].x0))


def extrair_funcoes(pagina):
    """Reconstrói os bullets: linha com marcador (ou com tamanho de fonte diferente) inicia item;
    as demais continuam o item anterior. Linhas-título terminadas em ':' (ex.: 'Reflexos como:')
    agrupam os itens curtos logo abaixo. Páginas sem marcadores têm o parágrafo dividido em frases."""
    dots = marcadores(pagina)
    ls = linhas(pagina)
    passos = [b["bbox"].y0 - a["bbox"].y0 for a, b in zip(ls, ls[1:])]
    passo = sorted(passos)[len(passos) // 2] if passos else 30

    itens = []  # cada item: {"texto": str, "titulo": bool, "y": float}
    for l in ls:
        tem_dot = any(l["bbox"].y0 - 2 <= d.y0 + d.height / 2 <= l["bbox"].y1 + 2 for d in dots)
        texto = limpar(l["texto"])
        mudou_fonte = bool(itens) and abs(l["tamanho"] - itens[-1]["tamanho"]) > 2
        if tem_dot or not itens or mudou_fonte:
            itens.append({"texto": texto, "titulo": not tem_dot and texto.endswith(":"), "y": l["bbox"].y1, "linhas": 1,
                          "tamanho": l["tamanho"]})
        elif texto.endswith(":"):
            itens.append({"texto": texto, "titulo": True, "y": l["bbox"].y1, "linhas": 1, "tamanho": l["tamanho"]})
        else:
            itens[-1]["texto"] += " " + texto
            itens[-1]["y"] = l["bbox"].y1
            itens[-1]["linhas"] += 1

    funcoes, i = [], 0
    while i < len(itens):
        it = itens[i]
        if it["titulo"]:
            filhos, j, y = [], i + 1, it["y"]
            while (j < len(itens) and not itens[j]["titulo"] and itens[j]["linhas"] == 1
                   and itens[j]["y"] - y < passo * 1.6):
                filhos.append(itens[j]["texto"])
                y = itens[j]["y"]
                j += 1
            funcoes.append(it["texto"] + " " + ", ".join(f[0].lower() + f[1:] for f in filhos) if filhos else it["texto"])
            i = j
        else:
            funcoes.append(it["texto"])
            i += 1
    funcoes = [limpar(f) for f in funcoes]
    if not dots:
        funcoes = [frase for f in funcoes for frase in re.split(r"(?<=\.)\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", f)]
    return funcoes


def recortar_pagina(pagina, destino, lado_max=720):
    """Renderiza a página e corta as margens brancas (mantém rótulos e o '?' colorido)."""
    pix = pagina.get_pixmap(dpi=144)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    fundo = Image.new("RGB", img.size, (255, 255, 255))
    dif = ImageChops.difference(img, fundo).convert("L").point(lambda v: 255 if v > 14 else 0)
    caixa = dif.getbbox()
    if caixa:
        m = 14
        caixa = (max(caixa[0] - m, 0), max(caixa[1] - m, 0), min(caixa[2] + m, img.width), min(caixa[3] + m, img.height))
        img = img.crop(caixa)
    img.thumbnail((lado_max, lado_max), Image.LANCZOS)
    img.save(destino, "JPEG", quality=84, optimize=True, progressive=True)
    return img.size


def main():
    doc = fitz.open(PDF)
    PASTA_IMG.mkdir(exist_ok=True)
    SAIDA_JSON.parent.mkdir(exist_ok=True)

    estruturas = []
    for inicio in range(0, len(doc), 4):
        grupo = list(range(inicio, min(inicio + 4, len(doc))))
        p_img = next(n for n in grupo if doc[n].get_images())
        p_nome = next(n for n in grupo if n != p_img and len(linhas(doc[n])) == 1)
        p_fun = next(n for n in grupo if n not in (p_img, p_nome))

        nome_pdf = limpar(doc[p_nome].get_text())
        nome = NOMES.get(nome_pdf, nome_pdf.title())
        ident = slug(nome)
        largura, altura = recortar_pagina(doc[p_img], PASTA_IMG / f"{ident}.jpg")

        estruturas.append({
            "id": ident,
            "nome": nome,
            "imagem": f"img/{ident}.jpg",
            "imagemTamanho": [largura, altura],
            "funcoes": extrair_funcoes(doc[p_fun]),
            "paginasPdf": {"nome": p_nome + 1, "funcao": p_fun + 1, "imagem": p_img + 1},
        })

    dados = {
        "titulo": "Estruturas do Encéfalo",
        "fonte": PDF.name,
        "estruturas": estruturas,
    }
    SAIDA_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(estruturas)} estruturas -> {SAIDA_JSON.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
