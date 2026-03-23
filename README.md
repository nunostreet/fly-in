# fly-in

Projeto em Python para parsing de mapas, routing, simulacao e visualizacao.

## Setup

Este projeto usa Python 3.12 e dependencias instaladas em `.venv`.

### Criar o ambiente virtual

Com Python 3.12 disponivel na maquina:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se `python` ou `python3` continuarem a apontar para o Python global, usa diretamente o interpretador do projeto:

```bash
./.venv/bin/python --version
./.venv/bin/python -m pip install -r requirements.txt
```

## Visualizacao

Para correr a visualizacao com o interpretador certo:

```bash
python3 visualization/render.py
```

Se o ambiente virtual estiver ativo corretamente, `python` e `python3` devem apontar ambos para `.venv/bin/...`.

Se isso nao acontecer, usa temporariamente:

```bash
./.venv/bin/python visualization/render.py
```

## Notas

- `.venv/` nao vai para o Git.
- Depois de fazer `git pull` noutra maquina, tens de recriar o ambiente virtual localmente.
- As dependencias do projeto estao em `requirements.txt`.
