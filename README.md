# IBM Quantum Hardware Evolution Analysis (2020–2024)
# Análise da Evolução do Hardware Quântico IBM (2020–2024)

[EN]
This repository contains the data extraction engine used in the article  
**"Quantum Moore’s Law"**.  
The code performs a longitudinal analysis of IBM superconducting quantum processors,
using historical calibration data (*snapshots*) to quantify progress in quantum
hardware engineering.

[PT-BR]
Este repositório contém o motor de extração de dados utilizado no artigo  
**"A Lei de Moore Quântica"**.  
O código realiza uma análise longitudinal da qualidade dos processadores
supercondutores da IBM, utilizando dados históricos de calibração (*snapshots*)
para quantificar o progresso da engenharia quântica.

---

## ⚛️ What This Code Does (Scientific Perspective)
## ⚛️ O Que Este Código Faz (Visão Científica)

[EN]
Unlike benchmarks that measure only software-level performance, this script accesses
the **physical layer** of quantum processors to extract three critical metrics that
define *Quantum Utility*:

1. **$T_1$ (Relaxation Time):** The qubit’s “fuel.” Measures how long a qubit can retain
   its energy before decaying to 0. It represents a fundamental limit on algorithm
   execution time.
2. **$T_2$ (Dephasing Time):** The qubit’s “memory.” Measures how long quantum phase
   coherence is preserved. In the *Heron* processor, we observe $T_2 > T_1$ due to the
   new architecture with *tunable couplers*, a key milestone analyzed in this work.
3. **Readout Error:** The probability of error when measuring the final quantum state.

[PT-BR]
Diferente de benchmarks que medem apenas a velocidade de software, este script acessa
a **camada física** dos processadores para extrair três métricas críticas que definem a
"Utilidade Quântica":

1. **$T_1$ (Tempo de Relaxamento):** O "combustível" do qubit. Mede quanto tempo o qubit
   consegue segurar sua energia antes de decair para 0. É o limite fundamental da
   duração de um algoritmo.
2. **$T_2$ (Tempo de Defasagem):** A "memória" do qubit. Mede quanto tempo a fase quântica
   permanece intacta. No processador *Heron*, observamos $T_2 > T_1$ devido à nova
   arquitetura de acopladores ajustáveis (*Tunable Couplers*), um marco importante
   analisado aqui.
3. **Readout Error (Erro de Leitura):** A probabilidade de erro ao medir o resultado final.

---

## 🧬 Analyzed Technological Eras
## 🧬 As Eras Analisadas

[EN]
The code groups processors into four distinct technological generations to support
the thesis that hardware quality (coherence) initially declined with aggressive
scaling, but later recovered as fabrication processes matured:

- **Falcon Era (27 Qubits):** Stability reference (2020).
- **Eagle R1 Era (127 Qubits):** Rapid scaling phase, where the quality “floor” dropped
  (2021–2022).
- **Eagle R3 Era (127 Qubits):** Manufacturing maturation and recovery of coherence
  times (2023).
- **Heron Era (133 Qubits):** State of the art, focused on quality and modular
  connectivity (2024).

[PT-BR]
O código agrupa os dados em quatro gerações tecnológicas distintas para sustentar a
tese de que a qualidade (coerência) inicialmente caiu com o aumento da escala, mas se
recuperou com a maturidade do processo de fabricação:

- **Era Falcon (27 Qubits):** A referência de estabilidade (2020).
- **Era Eagle R1 (127 Qubits):** A fase de expansão rápida, onde o “piso” de qualidade
  caiu (2021–2022).
- **Era Eagle R3 (127 Qubits):** A maturação do processo de fabricação e recuperação dos
  tempos de coerência (2023).
- **Era Heron (133 Qubits):** O estado da arte, focado em qualidade e conectividade
  modular (2024).

---

## 🛠️ Technical Methodology
## 🛠️ Metodologia Técnica

[EN]
The script uses the `qiskit-ibm-runtime` library to load **Fake Backends**. These objects
are not stochastic simulations, but rather *frozen snapshots* containing real
calibration data from IBM quantum chips at specific points in time.

- **Population-Level Sampling:** Entire fleets (e.g., *Sherbrooke, Brisbane, Kyoto,
  Osaka*) are analyzed instead of single chips, ensuring statistical robustness.
- **Output:** Generates a `quantum_hardware_data.csv` file with raw, qubit-level data,
  enabling density plots (e.g., violin plots) and manufacturing *yield* analysis.

[PT-BR]
O script utiliza a biblioteca `qiskit-ibm-runtime` para carregar **Fake Backends**. Esses
objetos não são simulações aleatórias, mas sim “fotografias congeladas” (*snapshots*)
contendo dados reais de calibração dos chips em datas específicas.

- **Amostragem Populacional:** Analisamos frotas completas (ex: *Sherbrooke, Brisbane,
  Kyoto, Osaka*) em vez de chips únicos, garantindo robustez estatística.
- **Saída:** Gera um arquivo `quantum_hardware_data.csv` com dados brutos de cada qubit
  individual, permitindo a criação de gráficos de densidade (Violin Plots) e análise
  de *yield* (rendimento de fabricação).

---

## 🚀 How to Reproduce
## 🚀 Como Reproduzir

[EN]
1. Install dependencies (using `uv` or `pip` is recommended):
   ```bash
   uv add numpy qiskit-ibm-runtime
   ```

[PT-BR]
1. Instale as dependências (recomendado usar `uv` or `pip`):
   ```bash
   uv add numpy qiskit-ibm-runtime
   ```