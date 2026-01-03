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

# [EN] Import the simulation library containing digital twins of real IBM quantum chips
# [PT-BR] Importamos a biblioteca de simulação que contém os digital twins dos chips reais
from qiskit_ibm_runtime.fake_provider import (
    FakeHanoiV2, FakeCairoV2, FakeKolkataV2,    # Falcon generation (low density, high initial stability)
    FakeWashingtonV2,                           # Eagle R1 generation (the scaling “leap” that came at a quality cost)
    FakeSherbrooke, FakeBrisbane, FakeKyoto, FakeOsaka, # Eagle R3 generation (mature fabrication process)
    FakeTorino, FakeFez, FakeMarrakesh          # Heron generation (new architecture with tunable couplers)
)

def main():
    print("[EN]")
    print("Iniciando extração de dados históricos (T1, T2, Readout)...")
    print("Carregando backends (isso pode levar alguns segundos)...")
    print("[PT-BR]")
    print("Starting historical data extraction (T1, T2, Readout)...")
    print("Loading backends (this may take a few seconds)...")

    # Dictionary of historical processors
    # Define the scope of the population-level study: group chips by “Technological Era” to demonstrate systemic hardware evolution rather than isolated improvements

    # Dicionário de Processadores Históricos
    # Definimos o escopo do Estudo Populacional: agrupar chips por "Era Tecnológica" para provar a evolução sistêmica

    backends_by_era = {
        "Falcon (2020/21)": [FakeHanoiV2(), FakeCairoV2(), FakeKolkataV2()],        # Proxy for Montreal (27 qubits)
        "Eagle R1 (2022)": [FakeWashingtonV2()], # First Eagle generation (127 qubits); only publicly available pure R1
        "Eagle R3 (2023)":[FakeSherbrooke(), FakeBrisbane(), FakeKyoto(), FakeOsaka()],   # Mature Eagle (127 qubits)
        "Heron (2024)": [FakeTorino(),FakeFez(),FakeMarrakesh()]  # State of the art; Heron (133 qubits)
    }

    # [EN] Save results to CSV
    # File name used to store raw qubit-level data for subsequent statistical analysis
    # [PT-BR] Salvando resultados em CSV
    # Nome do arquivo onde salvaremos os dados brutos para análise estatística posterior
    filename = os.path.join("data","database-quantum-qiskit_ibm.csv")
    os.makedirs("data", exist_ok=True)
    
    # CSV header defining the critical hardware quality metrics:
    # Era: Technological generation (e.g., Falcon)
    # Chip: Processor name (e.g., Hanoi)
    # Qubit_Index: Qubit index on the chip (0, 1, 2, ..., N)
    # T1_us: Thermal relaxation — T1 coherence time in microseconds
    # T2_us: Dephasing — T2 coherence time in microseconds
    # Readout_Error_Pct: Measurement fidelity — readout error expressed as a percentage
    header = ["Era", "Chip", "Qubit_Index", "T1_us", "T2_us", "Readout_Error_Pct"]
    
    # In-memory list to accumulate data before writing to disk
    # Lista em memória para acumular os dados antes de escrever no disco 
    all_data_rows = []

    # Console table formatting (immediate feedback for the researcher)
    print(f"\n{'Geração / Chip':<30} | {'Qubits':^6} | {'T1 Med':>10} | {'T2 Med':>10} | {'T2/T1':^7} | {'Readout_Error_Pct':>12}")
    print("=" * 95)

    # Main loop (1): iterate over technological eras to trace temporal hardware evolution
    for era_name, chip_list in backends_by_era.items():
        print(f"{era_name}")
        
        # Variables used to compute generation-level global means (aggregated population statistics)
        era_t1_values = []
        era_t2_values = []

        # Loop 2: Iterate over each physical processor available in the sample
        for backend in chip_list:
            #  Normalize the chip name to remove library prefixes
            # (e.g., "fake_sherbrooke" → "Sherbrooke")
            # The class name is used to ensure correctness across different Qiskit versions
            raw_name = backend.__class__.__name__
            chip_name = raw_name.replace("Fake", "").replace("V2", "")
            
            # Access the "Target": the physical representation of the chip containing
            # calibrated hardware properties
            target = backend.target
            num_qubits = target.num_qubits
            
            # Temporary lists for per-chip statistical aggregation
            chip_t1 = []
            chip_t2 = []
            chip_ro = []

            # Loop 3: Iterate over each physical qubit
            # (the fundamental data point of the analysis)
            for i in range(num_qubits):
                try:
                    # 1. Attempt to access the properties of qubit i
                    # If this fails, the qubit does not exist and is skipped (continue)
                    props = target.qubit_properties[i]
                    if not props: continue 
                    
                    t1_val = None
                    t2_val = None
                    ro_val = None

                    # 2. Extract T1 (fundamental)
                    if props.t1 is not None:
                        t1_val = props.t1 * 1e6
                        chip_t1.append(t1_val)
                        era_t1_values.append(t1_val)

                    # 3. Extract T2 (fundamental)
                    if props.t2 is not None:
                        t2_val = props.t2 * 1e6
                        chip_t2.append(t2_val)
                        era_t2_values.append(t2_val)
                    
                    # 4. Extract readout error 
                    # Attempt A: V2 standard (direct property access)
                    if hasattr(props, 'readout_error') and props.readout_error is not None:
                        ro_val = props.readout_error * 100
                    
                    # Attempt B: V2 standard (embedded within the 'measure' instruction)
                    if ro_val is None:
                        try:
                            measure_op = target.operation_from_name('measure')
                            if measure_op:
                                op_props = measure_op.get((i,))
                                if op_props and getattr(op_props, 'error', None):
                                    ro_val = op_props.error * 100
                        except: pass

                    # Attempt C: Legacy V1 pattern — THIS WILL SAVE YOUR DATA!
                    # Many V2 FakeBackends still retain the legacy calibration database here.

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

                    # 5. Save to the dataset if T1 is available (even if readout data is missing)
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
                    continue  # Skip only this qubit if a critical failure occurs

            # --- ESTATÍSTICA DO CHIP ---
            if chip_t1: # If at least one operational (alive) qubit was found
                med_t1 = np.median(chip_t1)
                med_t2 = np.median(chip_t2) if chip_t2 else 0
                
                # Ratio T2/T1
                ratio = med_t2 / med_t1 if med_t1 > 0 else 0
                
                # Readout String
                if chip_ro:
                    ro_str = f"{np.median(chip_ro):.2f}%"
                else:
                    ro_str = "N/A" # N/A may appear here, but T1/T2 values are still reported

                print(f"  ├─ {chip_name:<20} | {len(chip_t1):^6} | {med_t1:>7.1f} µs | {med_t2:>7.1f} µs | {ratio:^7.2f} | {ro_str:>12}")
            else:
                print(f"  ├─ {chip_name:<20} | Insufficient data (empty list)")

        # Display of the “Generation Mean” (population-level statistics)
        # Indicates whether improvements are systemic to the architecture
        # or merely due to a single exceptionally good chip
        if era_t1_values:
            grand_t1 = np.median(era_t1_values)
            grand_t2 = np.median(era_t2_values)
            grand_ratio = grand_t2 / grand_t1
            print(f"  ➤ GENERATION MEAN ({len(era_t1_values)} pts)| {'---':^6} | {grand_t1:>7.1f} µs | {grand_t2:>7.1f} µs | {grand_ratio:^7.2f} | {'---':>12}")
        
        print("-" * 95)

    # Final write loop to disk (I/O)
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_data_rows)
    


    print("[EN]")
    print(f"[SUCCESS] Dataset saved to: {os.path.abspath(filename)}")
    print(f"Total number of qubits processed: {len(all_data_rows)}")
    print("[PT-BR]")
    print(f"[SUCESSO] Dataset salvo em: {os.path.abspath(filename)}")
    print(f"Total de Qubits processados: {len(all_data_rows)}")

if __name__ == "__main__":
    main()