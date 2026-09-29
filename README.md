# Memória do Encéfalo

Jogo da memória de neuroanatomia para estudar 12 estruturas do encéfalo: imagem, nome e funções.

**Jogar:** https://caiorc.github.io/memoria-encefalo/

## Como jogar

Vire uma carta de **pista** e depois ache a **resposta** que forma o par. Acertos seguidos multiplicam os pontos. Quando o par não combina, as cartas ficam abertas um tempo para leitura (toque para seguir antes). Toque numa carta acertada para ver a ficha completa da estrutura.

| Modo | Pista | Resposta |
|---|---|---|
| Estrutura → Nome | imagem | nome |
| Nome → Estrutura | nome | imagem |
| Estrutura → Função | imagem | funções |
| Nome → Função | nome | funções |

| Dificuldade | Pares | Espiada inicial | Texto |
|---|---|---|---|
| Fácil | 4 | 4 s | completo |
| Médio | 6 | 2,5 s | completo |
| Difícil | 8 | nenhuma | letras ocultas nos nomes; funções completas |

## Instalar no celular

Abra o link no celular. No Android, toque em **Instalar app**. No iPhone, toque em **Compartilhar** e depois em **Adicionar à Tela de Início**. Depois de instalado, o jogo funciona sem internet.

## Arquivos

- `index.html`: o jogo (HTML, CSS e JavaScript num arquivo só).
- `dados/estruturas.json`: as estruturas, com nome, imagem, funções e páginas de origem no PDF.
- `img/`: imagens recortadas dos slides.
- `manifest.json`, `sw.js` e `icones/`: app instalável e modo offline.
- `ferramentas/extrair_pdf.py`: gera o JSON e as imagens a partir do PDF de origem (`Fonte.pdf`, que não está no repositório).
- `ferramentas/gerar_icones.py`: gera os ícones do app.

As ferramentas usam Python com `pip install pymupdf pillow`.

## Rodar no computador

Na pasta do projeto, rode `jogar.bat` (Windows) ou `python -m http.server 8000` e abra http://localhost:8000/. Abrir o `index.html` direto do disco não funciona, porque o navegador bloqueia a leitura do JSON.
