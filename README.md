# Shift Scheduler Optimizer 🚚🕒

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org)
[![Optimization](https://img.shields.io/badge/Optimization-MILP-green)](#-função-objetivo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📌 Visão Geral do Projeto

Este projeto foi desenvolvido como uma solução autoral de **Pesquisa Operacional (PO)** aplicada à gestão de logística e operações industriais 24/7. O **Shift Scheduler Optimizer** utiliza modelos de **Programação Linear Inteira Mista (MILP)** para automatizar e otimizar o dimensionamento de força de trabalho (*workforce sizing*) e a escala de turnos em centros de distribuição ou linhas de produção.

O objetivo principal é garantir **100% de cobertura operacional** — com foco especial em turnos críticos (como o turno noturno) —, enquanto minimiza o custo da folha operacional e respeita as restrições da CLT (Consolidação das Leis do Trabalho) e regras de fadiga humana.

---

## 🎯 Cenário e Escopo do MVP

O modelo simula um **Centro de Distribuição (CD)** que opera em regime contínuo (**24h por dia, 7 dias por semana**).

### 1. Definição dos Turnos
* **Turno A (Noturno):** 00:00 - 08:00
* **Turno B (Matutino):** 08:00 - 16:00
* **Turno C (Vespertino):** 16:00 - 00:00

### 2. Restrições do Modelo
* **Cobertura Mínima (Logística):** Cada turno exige um número mínimo de operadores, baseado na previsão de demanda de movimentação de carga diária.
* **Descanso Interjornada (CLT):** Deve haver no mínimo 11 horas entre o fim de um turno e o início do próximo (CLT, art. 66). Por isso, são proibidas as transições **C → A**, **C → B** e **B → A** em dias consecutivos.
* **Jornada Máxima Semanal:** Limite de 44 horas de trabalho regulares por colaborador na semana.
* **Ergonomia e Escala:** Máximo de 1 turno por dia por colaborador e garantia de pelo menos 1 folga semanal regular.

### 3. 🎯 Função Objetivo

$$ \min \sum_{i \in I} \sum_{d \in D} \sum_{t \in T} c_{i,t} \cdot x_{i,d,t} $$

Onde:

* $I$: conjunto de colaboradores; $D$: conjunto de dias da semana; $T$: conjunto de turnos (A, B, C);
* $x_{i,d,t} \in \{0,1\}$: igual a 1 se o colaborador $i$ é alocado ao turno $t$ no dia $d$;
* $c_{i,t}$: custo de alocar o colaborador $i$ ao turno $t$ (salário-hora × duração do turno, somado ao adicional noturno quando aplicável).

O modelo minimiza o custo total da folha operacional, penalizando financeiramente alocações em turnos mais caros (como o noturno) e evitando excesso de pessoal, buscando o ponto ótimo de eficiência (*lean staffing*).

### 4. Simplificações do MVP

Para manter o modelo enxuto, esta versão **não** trata:

* variável explícita de horas extras (a jornada é limitada a 44h regulares);
* hora noturna reduzida (52min30s) e intervalo intrajornada de 1h;
* habilidades específicas por posto de trabalho.

Esses itens estão no roteiro de evolução do projeto.

---

## 🏗️ Arquitetura do Repositório

```text
shift-scheduler-optimizer/
│
├── data/
│   ├── demand_shifts.csv        # Demanda de pessoal necessária por turno e dia
│   └── workers_profile.csv      # Lista de funcionários, custos e restrições
│
├── src/
│   ├── model.py                 # Formulação matemática e execução do solver (PuLP)
│   ├── validator.py             # Script de compliance (validação de regras trabalhistas)
│   └── utils.py                 # Funções auxiliares (transformação de dados e relatórios)
│
├── notebooks/
│   └── walkthrough.ipynb        # Jupyter Notebook com a jornada do problema e EDA
│
├── output/
│   └── optimal_schedule.csv     # Escala de trabalho final otimizada gerada pelo modelo
│
├── requirements.txt             # Dependências do projeto
├── README.md                    # Documentação principal
└── LICENSE                      # Licença de uso (MIT)
```

---

## 🛠️ Ferramentas e Tecnologias

* **Linguagem Principal:** Python 3.10+
* **Modelagem Matemática & Otimização:** `PuLP` com o solver CBC (open source) para resolução do problema combinatório.
* **Manipulação de Dados:** `pandas` e `numpy` para estruturar as matrizes de decisão.
* **Visualização de Resultados:** `matplotlib`, `seaborn` e `plotly` para a construção de **Gráficos de Gantt** da escala otimizada.

---

## 📊 Impacto e Resultados Operacionais

A substituição do planejamento de escalas manual (planilhas tradicionais) por este otimizador matemático traz os seguintes resultados:

| Métrica Analisada | Planejamento Manual | Otimizador MILP | Impacto obtido |
| :--- | :---: | :---: | :---: |
| **Tempo de Geração da Escala** | ~4 horas / semana | < 10 segundos | **-99.9% de tempo de liderança** |
| **Custo Total da Folha Operacional** | Ajustes reativos | Minimizado via modelo | **Redução de custos estimada** |
| **Violações de Restrições (CLT)** | Frequentes (erro humano) | 0 violações | **Risco de passivo trabalhista reduzido** |
| **Cobertura Mínima por Turno** | Sobrecarga de equipes | 100% atendida | **Maior ergonomia e retenção** |

---

## 🚀 Como Executar o Projeto

1. Clone o repositório:
```bash
git clone https://github.com/hugoarcanjodev/shift-scheduler-optimizer.git
cd shift-scheduler-optimizer
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o otimizador:
```bash
python src/model.py
```

4. Visualize os resultados em `output/optimal_schedule.csv` ou explore os gráficos abrindo `notebooks/walkthrough.ipynb`.

---

## 🧔 Autor

Desenvolvido por **Hugo Arcanjo**
* 🎓 Estudante de Engenharia de Produção
* 💼 Atuante na área de Logística / Supply Chain
* 🔗 Conecte-se comigo no [LinkedIn](https://www.linkedin.com/in/hugo-arcanjo/)