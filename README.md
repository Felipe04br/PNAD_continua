# 📥 Extrator e Analisador de Microdados PNAD Contínua

Pipeline Python para download, extração, pré-processamento e análise estatística dos microdados da **PNAD Contínua (IBGE)** diretamente do FTP oficial, com filtragem por UF e geração de relatório Excel segmentado.

---

## 🗂️ Arquivos

| Arquivo | Descrição |
|---|---|
| `App.py` | Download, extração e filtragem dos microdados via FTP do IBGE |
| `Media_Moda_Mediana.py` | Cálculo de média, moda e mediana segmentados por período |
| `Banco_de_dados.csv` | Base gerada pelo `App.py` — 274.541 registros (Bahia, 2023–2025) |

---

## ✨ Funcionalidades

### `App.py` — Extrator
- Conexão e download automático via **FTP do IBGE**
- Seleção interativa de **ano** (2023–2025 ou específico) e **trimestre** (1–4 ou todos)
- Filtragem dos dados por **UF** (padrão: Bahia — código 29)
- Leitura de arquivo de largura fixa (`.txt`) com layout oficial da PNAD Contínua
- Concatenação e ordenação cronológica de múltiplos períodos
- Exportação opcional para **CSV**
- Gerenciamento automático de disco: arquivos temporários são removidos após o processamento

### `Media_Moda_Mediana.py` — Analisador
- Calcula **média**, **mediana** e **moda** das variáveis selecionadas
- Gera três níveis de agregação:
  - **Trimestral** — estatísticas por ano e trimestre
  - **Consolidado Anual** — estatísticas por ano (todos os trimestres)
  - **Total do Banco** — estatísticas gerais de todo o período
- Exporta o resultado em `Relatorio_PNAD_Segmentado.xlsx`

---

## 🚀 Como executar

### 1. Instale as dependências

```bash
pip install pandas openpyxl
```

> `zipfile`, `ftplib` e `os` fazem parte da biblioteca padrão do Python.

### 2. Extraia os microdados

```bash
python App.py
```

Responda às perguntas interativas:

```
Qual ano deseja extrair? (Digite 0 para carregar o padrão 2023 a 2025, ou o ano específico):
Qual trimestre deseja extrair? (Digite 0 para carregar todos, ou 1, 2, 3 ou 4):
```

Ao final, confirme a exportação para `Banco_de_dados.csv`.

### 3. Gere o relatório estatístico

Edite o caminho do CSV no início do arquivo:

```python
caminho = r'caminho\para\Banco_de_dados.csv'
```

Em seguida, execute:

```bash
python Media_Moda_Mediana.py
```

O arquivo `Relatorio_PNAD_Segmentado.xlsx` será gerado no diretório atual.

---

## 📁 Saídas

| Arquivo | Descrição |
|---|---|
| `Banco_de_dados.csv` | Microdados filtrados por UF, prontos para análise |
| `Relatorio_PNAD_Segmentado.xlsx` | Relatório com média, moda e mediana por período |

> Os arquivos `.zip` e `.txt` intermediários são excluídos automaticamente do disco pelo `App.py`.

---

## 📊 Banco de dados atual

| Cobertura | Detalhe |
|---|---|
| UF | Bahia (código 29) |
| Período | 2023 T1 → 2025 T4 (12 trimestres) |
| Registros | 274.541 linhas · 77 variáveis |

---

## 🗂️ Variáveis extraídas

O layout lê **77 variáveis** do arquivo oficial, incluindo:

- **Identificação:** `Ano`, `Trimestre`, `UF`, `Capital`, `RM_RIDE`
- **Domicílio:** `V1008`, `V1014`, `V1022`, `V1023`
- **Pessoa:** `V2001`, `V2007`, `V2009`, `V2010`
- **Trabalho e rendimento:** `V4002`, `V4012`, `V4013`, `V4015` a `V4051` e derivadas

**Variáveis analisadas em `Media_Moda_Mediana.py`:** `V2007`, `V2009`, `V2010`, `V403412`, `V4039`

Consulte o [dicionário oficial da PNAD Contínua](https://www.ibge.gov.br/estatisticas/sociais/trabalho/9171-pesquisa-nacional-por-amostra-de-domicilios-continua-mensal.html) para a descrição completa de cada variável.

---

## ⚙️ Requisitos

- Python 3.8+
- Conexão com a internet (acesso ao FTP do IBGE) para o `App.py`
- Espaço em disco temporário para os arquivos `.zip` e `.txt` durante o processamento

---

## 🛠️ Tecnologias

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
