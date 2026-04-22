# 📥 Extrator de Microdados PNAD Contínua

Script Python para download, extração e pré-processamento automático dos microdados da **PNAD Contínua (IBGE)** diretamente do FTP oficial, com filtragem por UF e exportação para CSV.

---

## ✨ Funcionalidades

- Conexão e download automático via **FTP do IBGE**
- Seleção interativa de **ano** (2023–2025 ou específico) e **trimestre** (1–4 ou todos)
- Filtragem dos dados por **UF** (padrão: Bahia — código 29)
- Leitura de arquivo de largura fixa (`.txt`) com layout oficial da PNAD Contínua
- Concatenação e ordenação cronológica de múltiplos períodos
- Exportação opcional para **CSV**
- Gerenciamento automático de disco: arquivos temporários são removidos após o processamento

---

## 🚀 Como executar

### 1. Instale as dependências

```bash
pip install pandas
```

> `zipfile`, `ftplib` e `os` já fazem parte da biblioteca padrão do Python.

### 2. Execute o script

```bash
python App.py
```

### 3. Responda às perguntas interativas

```
Qual ano deseja extrair? (Digite 0 para carregar o padrão 2023 a 2025, ou o ano específico):
Qual trimestre deseja extrair? (Digite 0 para carregar todos, ou 1, 2, 3 ou 4):
```

Ao final, o script pergunta se deseja exportar o resultado como `Banco_de_dados.csv`.

---

## 📁 Saída

| Arquivo | Descrição |
|---|---|
| `Banco_de_dados.csv` | DataFrame final exportado (opcional) |

> Os arquivos `.zip` e `.txt` intermediários são excluídos automaticamente do disco.

---

## 🗂️ Variáveis extraídas

O script lê **70+ variáveis** do layout oficial da PNAD Contínua, incluindo:

- Identificação: `Ano`, `Trimestre`, `UF`, `Capital`, `RM_RIDE`
- Domicílio: `V1008`, `V1014`, `V1022`, `V1023`
- Pessoa: `V2001`, `V2007`, `V2009`, `V2010`
- Trabalho e rendimento: `V4002`, `V4012`, `V4013`, `V4015` a `V4051` e derivadas

Consulte o [dicionário oficial da PNAD Contínua](https://www.ibge.gov.br/estatisticas/sociais/trabalho/9171-pesquisa-nacional-por-amostra-de-domicilios-continua-mensal.html) para a descrição completa de cada variável.

---

## ⚙️ Requisitos

- Python 3.8+
- Conexão com a internet (acesso ao FTP do IBGE)
- Espaço em disco temporário para os arquivos `.zip` e `.txt` durante o processamento

---

## 🛠️ Tecnologias

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
