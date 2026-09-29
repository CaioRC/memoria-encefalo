"""Gera os ícones do app (PWA) em icones/*.png a partir de um SVG.

Uso:  python ferramentas/gerar_icones.py
"""
from pathlib import Path

import fitz  # PyMuPDF renderiza SVG

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "icones"

# (MuPDF não renderiza gradientes de SVG, por isso as cores são sólidas.)
# Duas cartas (pista violeta, resposta rosa) com o cérebro, dentro da zona segura de ícones "maskable".
SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#2A1D55"/>
  <g transform="rotate(-12 256 256)">
    <rect x="138" y="132" width="172" height="222" rx="26" fill="#5B47A8"/>
    <rect x="150" y="144" width="148" height="198" rx="18" fill="none" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="4"/>
  </g>
  <g transform="rotate(9 256 256)">
    <rect x="204" y="160" width="172" height="222" rx="26" fill="#DC4A78"/>
    <rect x="216" y="172" width="148" height="198" rx="18" fill="none" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="4"/>
    <g transform="translate(290 271) scale(4.6) translate(-12 -11.5)" fill="none" stroke="#FFFFFF"
       stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 4.5C10.5 3 8 3.2 7.2 5 5 5 3.8 7 4.6 8.8 3 9.8 3 12.5 4.8 13.4 4 15.5 5.6 17.8 8 17.5c.8 1.8 3 2.1 4 1z"/>
      <path d="M12 4.5c1.5-1.5 4-1.3 4.8.5 2.2 0 3.4 2 2.6 3.8 1.6 1 1.6 3.7-.2 4.6.8 2.1-.8 4.4-3.2 4.1-.8 1.8-3 2.1-4 1z"/>
      <path d="M12 4.5v14M8 9.2c1 0 1.8.8 1.8 1.8M16 9.2c-1 0-1.8.8-1.8 1.8"/>
    </g>
  </g>
</svg>"""

TAMANHOS = {"icone-192.png": 192, "icone-512.png": 512, "apple-touch-icon.png": 180}


def main():
    PASTA.mkdir(exist_ok=True)
    pagina = fitz.open(stream=SVG.encode("utf-8"), filetype="svg")[0]
    for nome, lado in TAMANHOS.items():
        escala = lado / pagina.rect.width
        pagina.get_pixmap(matrix=fitz.Matrix(escala, escala), alpha=False).save(PASTA / nome)
        print(f"icones/{nome} ({lado}px)")


if __name__ == "__main__":
    main()
