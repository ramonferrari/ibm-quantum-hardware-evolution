# Análise da Evolução do Hardware Quântico IBM (2020-2024)

Este repositório contém o motor de extração de dados utilizado no artigo **"A Lei de Moore Quântica"**. O código realiza uma análise longitudinal da qualidade dos processadores supercondutores da IBM, utilizando dados históricos de calibração (*snapshots*) para quantificar o progresso da engenharia quântica.

## ⚛️ O Que Este Código Faz (Visão Científica)

Diferente de benchmarks que medem apenas a velocidade de software, este script acessa a **camada física** dos processadores para extrair três métricas críticas que definem a "Utilidade Quântica":

1.  **$T_1$ (Tempo de Relaxamento):** O "combustível" do qubit. Mede quanto tempo o qubit consegue segurar sua energia antes de decair para 0. É o limite fundamental da duração de um algoritmo.
2.  **$T_2$ (Tempo de Defasagem):** A "memória" do qubit. Mede quanto tempo a fase quântica permanece intacta. No processador *Heron*, observamos $T_2 > T_1$ devido à nova arquitetura de acopladores ajustáveis (*Tunable Couplers*), um marco importante analisado aqui.
3.  **Readout Error (Erro de Leitura):** A probabilidade de erro ao medir o resultado final.

### As Eras Analisadas
O código agrupa os dados em quatro gerações tecnológicas distintas para provar a tese de que a qualidade (coerência) inicialmente caiu com o aumento da escala, mas se recuperou com a maturidade de fabricação:

* **Era Falcon (27 Qubits):** A referência de estabilidade (2020).
* **Era Eagle R1 (127 Qubits):** A fase de expansão rápida, onde o "piso" de qualidade caiu (2021-2022).
* **Era Eagle R3 (127 Qubits):** A maturação do processo de fabricação e recuperação dos tempos de coerência (2023).
* **Era Heron (133 Qubits):** O estado da arte, focado em qualidade e conectividade modular (2024).

## 🛠️ Metodologia Técnica

O script utiliza a biblioteca `qiskit-ibm-runtime` para carregar **Fake Backends**. Estes objetos não são simulações aleatórias, mas sim "fotografias congeladas" (snapshots) contendo os dados reais de calibração dos chips em datas específicas.

* **Amostragem Populacional:** Analisamos frotas completas (ex: *Sherbrooke, Brisbane, Kyoto, Osaka*) em vez de chips únicos, garantindo robustez estatística.
* **Output:** Gera um arquivo `quantum_hardware_data.csv` com dados brutos de cada qubit individual, permitindo a criação de gráficos de densidade (Violin Plots) e análise de *Yield* (rendimento de fabricação).

## 🚀 Como Reproduzir

1. Instale as dependências (recomendado usar `uv` ou `pip`):
   ```bash
   uv add numpy qiskit-ibm-runtime