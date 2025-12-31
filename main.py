"""
HISTORICAL QUANTUM HARDWARE DATA EXTRACTION (IBM QUANTUM)
[PT-BR] EXTRAÇÃO DE DADOS HISTÓRICOS DE HARDWARE QUÂNTICO (IBM QUANTUM)
------------------------------------------------------------------
Ramon Moreno Ferrari

Context: Article "to be defined" (CACM?)
Date: December 2025

## DESCRIPTION:
[EN]
This script performs data mining on archived IBM quantum processor
“Digital Twins” available in the Qiskit library.
The objective is to reconstruct the hardware fidelity timeline
in order to validate the transition from the “Qubit Scaling” era
to the “Quality Scaling” era.

[PT-BR]
Este script realiza uma mineração de dados em "Gêmeos Digitais" (Digital Twins)
de processadores quânticos da IBM arquivados na biblioteca Qiskit.
O objetivo é reconstruir a linha do tempo da fidelidade do hardware
para validar a transição da era de "Escala de Qubits" para "Escala de Qualidade".

## METHODOLOGY:
[EN]
1. Population-Level Study: Instead of analyzing individual chips in isolation,
   processors are grouped into “Technological Eras”
   (Falcon, Eagle R1, Eagle R3, Heron).
2. Raw Data: Calibration metrics are extracted from ALL available physical qubits
   in the snapshots (N > 1000 data points), without outlier removal,
   in order to capture the true variability of the manufacturing process (yield).
3. Extracted Physical Metrics:
   - T1 (Longitudinal Relaxation): Qubit energy lifetime.
   - T2 (Transversal Relaxation): Phase coherence lifetime (quantum memory).
   - Readout Error: Final state measurement fidelity.
[PT-BR]
1. Estudo Populacional: Em vez de analisar chips isolados, agrupamos os
   processadores em "Eras Tecnológicas" (Falcon, Eagle R1, Eagle R3, Heron).
2. Dados Brutos: Extraímos as métricas de calibração de TODOS os qubits físicos
   disponíveis nos snapshots (N > 1000 pontos de dados), sem remover outliers,
   para capturar a variabilidade real do processo de fabricação (Yield).
3. Métricas Físicas Extraídas:
   - T1 (Relaxamento Longitudinal): Tempo de vida da energia do qubit.
   - T2 (Relaxamento Transversal): Tempo de vida da coerência de fase (memória quântica).
   - Readout Error: Fidelidade da medição do estado final.

## OUTPUT:
[EN]
- Console: Statistical table with per-chip medians and generation-level aggregated means.
- CSV: File 'quantum_hardware_data.csv' containing qubit-level granular data
  for distribution plotting.
[PT-BR]
- Console: Tabela estatística com medianas por chip e média agregada por geração.
- CSV: Arquivo 'quantum_hardware_data.csv' contendo dados granulares por qubit
  para plotagem de distribuições.
"""

import csv
import os
import numpy as np

# Importamos a biblioteca de simulação que contém os digital twins dos chips reais
from qiskit_ibm_runtime.fake_provider import (
    FakeHanoiV2, FakeCairoV2, FakeKolkataV2,    # Geração Falcon (Baixa densidade, alta estabilidade inicial)
    FakeWashingtonV2,                           # Geração Eagle R1 (O "salto" de escala que custou qualidade)
    FakeSherbrooke, FakeBrisbane, FakeKyoto, FakeOsaka, # Geração Eagle R3 (Processo de fabricação amadurecido)
    FakeTorino, FakeFez, FakeMarrakesh          # Geração Heron (Nova arquitetura com acopladores ajustáveis)
)

def main():
    print("Iniciando extração de dados históricos (T1, T2, Readout)...")
    print("Carregando backends (isso pode levar alguns segundos)...")

    # Dicionário de Processadores Históricos
    # Definimos o escopo do Estudo Populacional: agrupar chips por "Era Tecnológica" para provar a evolução sistêmica
    backends_by_era = {
        "Falcon (2020/21)": [FakeHanoiV2(), FakeCairoV2(), FakeKolkataV2()],        # Substituto do Montreal (27 Qubits)
        "Eagle R1 (2022)": [FakeWashingtonV2()], # Primeiro Eagle (127 Qubits) # O único R1 puro público
        "Eagle R3 (2023)":[FakeSherbrooke(), FakeBrisbane(), FakeKyoto(), FakeOsaka()],   # Eagle Maduro (127 Qubits)
        "Heron (2024)": [FakeTorino(),FakeFez(),FakeMarrakesh()] # O estado da arte  # Heron (133 Qubits)
    }

    ## Salvando em CSV
    # Nome do arquivo onde salvaremos os dados brutos para análise estatística posterior
    filename = os.path.join("data","database-quantum-qiskit_ibm.csv")
    os.makedirs("data", exist_ok=True)
    
    # Cabeçalho do CSV definindo as métricas críticas de qualidade de hardware:
        # Era: A geração tecnológica (ex: Falcon)
        # Chip: O nome do processador (ex: Hanoi)
        # Qubit_Index: O número do qubit no chip (0, 1, 2..., N)
        # T1_us: Relaxamento térmico - Tempo de coerência T1 em microsegundos
        # T2_us: Defasagem - Tempo de coerência T2 em microsegundos
        # Readout_Error_Pct: Fidelidade de Medida - Erro de leitura em porcentagem
    header = ["Era", "Chip", "Qubit_Index", "T1_us", "T2_us", "Readout_Error_Pct"]
    
    # Lista em memória para acumular os dados antes de escrever no disco 
    all_data_rows = []

    # Configuração visual da tabela no console (feedback imediato para o pesquisador)
    print(f"\n{'Geração / Chip':<30} | {'Qubits':^6} | {'T1 Med':>10} | {'T2 Med':>10} | {'T2/T1':^7} | {'Erro Leitura':>12}")
    print("=" * 95)

    # Loop 1 (Principal): Iteração sobre as Eras Tecnológicas para traçar a evolução temporal
    for era_name, chip_list in backends_by_era.items():
        print(f"{era_name}")
        
        # Variáveis para calcular a média global da GERAÇÃO (Estatística Populacional Agregada)
        era_t1_values = []
        era_t2_values = []

        # Loop 2: Iteração sobre cada processador físico disponível na amostra
        for backend in chip_list:
            # Normalizamos o nome do chip para remover prefixos de biblioteca ("fake_sherbrooke" -> "Sherbrooke")
            # Usamos a classe do objeto para garantir o nome correto mesmo em versões diferentes do Qiskit
            raw_name = backend.__class__.__name__
            chip_name = raw_name.replace("Fake", "").replace("V2", "")
            
            # Acessamos o "Target": a representação física do chip contendo propriedades calibradas
            target = backend.target
            num_qubits = target.num_qubits
            
            # Listas temporárias para estatística do chip individual
            chip_t1 = []
            chip_t2 = []
            chip_ro = []

            # Loop 3: Iteração sobre cada Qubit Físico (o "ponto de dado" fundamental)
            for i in range(num_qubits):
                try:
                    # 1. Tenta pegar as propriedades do qubit i
                    # Se falhar aqui, o qubit não existe, então pulamos (continue)
                    props = target.qubit_properties[i]
                    if not props: continue 
                    
                    t1_val = None
                    t2_val = None
                    ro_val = None

                    # 2. Extração de T1 (Fundamental)
                    if props.t1 is not None:
                        t1_val = props.t1 * 1e6
                        chip_t1.append(t1_val)
                        era_t1_values.append(t1_val)

                    # 3. Extração de T2 (Fundamental)
                    if props.t2 is not None:
                        t2_val = props.t2 * 1e6
                        chip_t2.append(t2_val)
                        era_t2_values.append(t2_val)

                    # 4. Extração de Readout (BLOCO CORRIGIDO)
                    # Tentativa A: Padrão V2 (Propriedade direta)
                    if hasattr(props, 'readout_error') and props.readout_error is not None:
                        ro_val = props.readout_error * 100
                    
                    # Tentativa B: Padrão V2 (Dentro da instrução 'measure')
                    if ro_val is None:
                        try:
                            measure_op = target.operation_from_name('measure')
                            if measure_op:
                                op_props = measure_op.get((i,))
                                if op_props and getattr(op_props, 'error', None):
                                    ro_val = op_props.error * 100
                        except: pass

                    # Tentativa C: Padrão V1 (Legacy) - ISSO VAI SALVAR SEUS DADOS!
                    # Muitos FakeBackends V2 ainda têm o banco de dados antigo escondido aqui.
                    if ro_val is None:
                        try:
                            # Tenta acessar a API antiga direto no backend
                            if hasattr(backend, 'properties'):
                                legacy_props = backend.properties()
                                if legacy_props:
                                    ro_val = legacy_props.readout_error(i) * 100
                        except: pass
                    
                    if ro_val is not None:
                        chip_ro.append(ro_val)

                    # 5. Salva no Dataset se tiver T1 (mesmo sem RO)
                    if t1_val is not None:
                        row = [
                            era_name, 
                            chip_name, 
                            i, 
                            f"{t1_val:.4f}", 
                            f"{t2_val:.4f}" if t2_val else "", 
                            f"{ro_val:.4f}" if ro_val is not None else ""
                        ]
                        all_data_rows.append(row)

                except Exception:
                    continue # Pula apenas este qubit se algo muito grave acontecer

            # --- ESTATÍSTICA DO CHIP ---
            if chip_t1: # Se achou pelo menos 1 qubit vivo
                med_t1 = np.median(chip_t1)
                med_t2 = np.median(chip_t2) if chip_t2 else 0
                
                # Razão T2/T1
                ratio = med_t2 / med_t1 if med_t1 > 0 else 0
                
                # Readout String
                if chip_ro:
                    ro_str = f"{np.median(chip_ro):.2f}%"
                else:
                    ro_str = "N/A" # Agora aparece N/A, mas mostra T1/T2!

                print(f"  ├─ {chip_name:<20} | {len(chip_t1):^6} | {med_t1:>7.1f} µs | {med_t2:>7.1f} µs | {ratio:^7.2f} | {ro_str:>12}")
            else:
                print(f"  ├─ {chip_name:<20} | Dados insuficientes (Lista vazia)")

        # Exibição da "Média da Geração" (Estatística Populacional)
        # Isso indica se a melhoria é sistêmica da arquitetura ou sorte de um chip específico
        if era_t1_values:
            grand_t1 = np.median(era_t1_values)
            grand_t2 = np.median(era_t2_values)
            grand_ratio = grand_t2 / grand_t1
            print(f"  ➤ MÉDIA DA GERAÇÃO ({len(era_t1_values)} pts)| {'---':^6} | {grand_t1:>7.1f} µs | {grand_t2:>7.1f} µs | {grand_ratio:^7.2f} | {'---':>12}")
        
        print("-" * 95)

    # Loop final de escrita no cisco (I/O)
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_data_rows)
    
    print(f"\n[SUCESSO] Dataset salvo em: {os.path.abspath(filename)}")
    print(f"Total de Qubits processados: {len(all_data_rows)}")

if __name__ == "__main__":
    main()