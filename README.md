# Gerador M3U — Canais Adultos

Gerador automático de playlist M3U para uso em players compatíveis, incluindo SS IPTV.

## O que o projeto faz

- reúne várias fontes M3U públicas configuradas em `fontes.json`;
- identifica entradas da categoria adulta;
- remove duplicados pelo endereço do stream;
- testa cada stream antes de colocá-lo na playlist final;
- remove automaticamente streams que falharem no teste;
- preserva `tvg-name` e outros metadados quando fornecidos pela fonte;
- força `group-title="Adultos"` para organização no SS IPTV;
- atualiza automaticamente a cada 6 horas pelo GitHub Actions;
- gera `adultos.m3u` e `status.json` no diretório principal.

## Arquivos

- `fontes.json` — URLs das fontes de entrada.
- `gerar_m3u.py` — coletor, filtro e testador dos streams.
- `adultos.m3u` — playlist final gerada automaticamente.
- `status.json` — resumo da última execução.
- `requirements.txt` — dependência Python.
- `.github/workflows/atualizar.yml` — atualização automática.

## Instalação no GitHub

1. Crie um repositório no GitHub.
2. Envie todos os arquivos mantendo a pasta `.github/workflows/`.
3. Abra **Actions** e execute manualmente `Atualizar lista M3U Adultos` na primeira vez.
4. Depois disso, o GitHub Actions executará a atualização a cada 6 horas.

## URL para o SS IPTV

Se o GitHub Pages estiver habilitado para o repositório, a URL terá o formato:

`https://SEU-USUARIO.github.io/SEU-REPOSITORIO/adultos.m3u`

Também é possível usar a URL `raw.githubusercontent.com` do arquivo `adultos.m3u`.

## Fontes configuradas

As fontes foram escolhidas por serem playlists públicas encontradas na web. O projeto apenas lê e testa os endereços fornecidos por elas; não hospeda nem fornece o conteúdo de vídeo.

Use apenas streams cujo uso seja permitido pelos respectivos fornecedores/licenciantes.
