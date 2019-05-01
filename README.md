# Python SafeSite

Esta aplicação foi desenvolvida com o propósito de
treinar suas habilidades em penetration testing.

É um site simples que pode ser explorado de diversas
formas diferentes. Foi desenvolvido em Python com Flask
e SQLite.

## Rodando dentro do Docker

Para rodar dentro do Docker, tenha o Docker instalado, o
GNU Make e o Git.

```bash
git clone https://github.com/wesleyit/python_safesite.git
cd python_safesite
make build  # para criar a imagem
make start  # vai iniciar o container
```

Com o container rodando, basta acessar em `http://localhost:8000`.

## Rodando direto na máquina

Para os corajosos, é possível rodar sem container.
Para isso, é necessário ter o Python3 instalado,
o Venv, o PIP, o Git e o GNU Make. O app foi testado
apenas no Linux, não sabemos se funciona diretamente
no Mac OS ou Windows, ok?

```bash
git clone https://github.com/wesleyit/python_safesite.git
cd python_safesite
make venv  # para criar o virtual env
source env/bin/activate  # chaveando para o venv
make pip  # baixar as dependências do Python3
make run  # iniciar em modo direto
```

## Disclaimer

> Esta aplicação tem falhas de segurança e pode comprometer o servidor onde for instalada. Cuidado.
