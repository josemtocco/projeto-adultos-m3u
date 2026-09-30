import json
import re
from urllib.parse import urlparse
import requests

TIMEOUT = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; M3U-Generator/1.0)"}

ADULT_TERMS = (
    "xxx", "adult", "adulto", "adultos", "18+", "porn", "pornographic",
    "sex", "sexy", "erotic", "erotico", "erótica", "playboy", "venus", "hot"
)


def baixar(url):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def parse_m3u(text):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF") and i + 1 < len(lines):
            info = lines[i]
            stream = lines[i + 1]
            if not stream.startswith("#"):
                nome = info.split(",", 1)[1].strip() if "," in info else "Canal Adulto"
                attrs = dict(re.findall(r'([A-Za-z0-9_-]+)="([^"]*)"', info))
                out.append((info, nome, attrs, stream))
                i += 2
                continue
        i += 1
    return out


def eh_adulto(nome, attrs):
    texto = " ".join([
        nome,
        attrs.get("group-title", ""),
        attrs.get("tvg-name", ""),
        attrs.get("tvg-id", "")
    ]).lower()
    return any(term in texto for term in ADULT_TERMS)


def stream_ativo(url):
    try:
        # Primeiro tenta HEAD; alguns servidores não suportam HEAD.
        try:
            r = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            if r.status_code < 400:
                r.close()
                return True
        except requests.RequestException:
            pass

        r = requests.get(
            url,
            headers={**HEADERS, "Range": "bytes=0-2048"},
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=True,
        )
        ok = r.status_code < 400
        r.close()
        return ok
    except requests.RequestException:
        return False


def limpar_nome(nome):
    nome = re.sub(r"^Logo canal\s*", "", nome, flags=re.I)
    nome = re.sub(r"^logo\s*[:\-]\s*", "", nome, flags=re.I)
    return re.sub(r"\s+", " ", nome).strip() or "Canal Adulto"


def montar_extinf(nome, attrs):
    nome = limpar_nome(nome)
    attrs = dict(attrs)
    attrs["tvg-name"] = attrs.get("tvg-name") or nome
    attrs["tvg-country"] = attrs.get("tvg-country") or ""
    attrs["tvg-language"] = attrs.get("tvg-language") or ""
    attrs["group-title"] = "Adultos"
    # Não inventa logos/EPG; preserva somente metadados existentes.
    ordem = ["tvg-id", "tvg-name", "tvg-logo", "tvg-country", "tvg-language", "group-title"]
    partes = []
    for k in ordem:
        if attrs.get(k):
            partes.append(f'{k}="{attrs[k]}"')
    return "#EXTINF:-1 " + " ".join(partes) + "," + nome


def main():
    with open("fontes.json", encoding="utf-8") as f:
        fontes = json.load(f)["fontes"]

    saida = ["#EXTM3U"]
    vistos = set()
    encontrados = 0
    adultos = 0
    ativos = 0
    erros = []

    for fonte in fontes:
        print(f"\n[FONTE] {fonte['nome']}")
        try:
            texto = baixar(fonte["url"])
            canais = parse_m3u(texto)
        except Exception as e:
            erros.append({"fonte": fonte["nome"], "erro": str(e)})
            print(f"[ERRO] {e}")
            continue

        for info, nome, attrs, stream in canais:
            encontrados += 1
            if not eh_adulto(nome, attrs):
                continue
            adultos += 1
            chave = stream.strip().lower()
            if not chave or chave in vistos:
                continue

            print(f"[TESTE] {limpar_nome(nome)}")
            if not stream_ativo(stream):
                print("  -> OFFLINE")
                continue

            vistos.add(chave)
            saida.append(montar_extinf(nome, attrs))
            saida.append(stream.strip())
            ativos += 1
            print("  -> ATIVO")

    with open("adultos.m3u", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(saida) + "\n")

    status = {
        "fontes_configuradas": len(fontes),
        "entradas_m3u_lidas": encontrados,
        "entradas_identificadas_como_adultas": adultos,
        "canais_ativos": ativos,
        "removidos_por_falha_no_teste": adultos - ativos,
        "erros_de_fontes": erros,
    }
    with open("status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

    print(f"\nConcluído: {ativos} canais ativos gravados em adultos.m3u")


if __name__ == "__main__":
    main()
