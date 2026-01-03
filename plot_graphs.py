"""
HISTORICAL QUANTUM HARDWARE DATA EXTRACTION (IBM QUANTUM)
[PT-BR] EXTRAÇÃO DE DADOS HISTÓRICOS DE HARDWARE QUÂNTICO (IBM QUANTUM)
------------------------------------------------------------------
Ramon Moreno Ferrari

Context: Article "to be defined" (CACM?)
Date: December 2025

## DESCRIPTION:
[EN]
Extracts and visualizes historical roadmap data to analyze the evolution
of physical qubit counts, highlighting the strategic shift from
pure scaling to quality/utility.
[PT-BR]
Visualização de dados históricos de roadmaps para analisar a evolução
do número de qubits físicos, destacando a mudança estratégica de
foco de pura escala para qualidade/utilidade.
------------------------------------------------------------------

"""

import pandas as pd
import numpy as np
from plotnine import *
import os

# --- CONFIGURATION / CONFIGURAÇÃO ---
DATA_PATH = os.path.join("data", "database-quantum-qubits.csv")
FIGURES_PATH = os.path.join("figures")

os.makedirs(FIGURES_PATH, exist_ok=True)

def load_and_clean_data():
    """
    [EN] Loads raw CSV data, cleans numeric columns (handling 'K' or ','), and types columns.
    [PT-BR] Carrega dados CSV, limpa colunas numéricas (tratando 'K' ou ',') e tipa colunas.
    """
    if not os.path.exists(DATA_PATH):
        print(f"[WARNING] File {DATA_PATH} not found.")
        return None
    else:
        df = pd.read_csv(DATA_PATH)

    df = df.rename(columns={
        "Year (Roadmap)": "Roadmap_Year",
        "Qubit counts": "Qubits",
        "Expected Qubit Counts": "Status"
    })
    
    # --- DATA CLEANING / LIMPEZA DE DADOS ---
    # [EN] Critical step: Convert "7.5K" or "10,000" strings to floats.
    # [PT-BR] Passo crítico: Converter strings "7.5K" ou "10,000" para floats.
    if df['Qubits'].dtype == object:
        # Remove commas (e.g., "10,000" -> "10000")
        df['Qubits'] = df['Qubits'].astype(str).str.replace(',', '')
        
        # Handle 'K' multiplier (e.g., "7.5K" -> "7500")
        # Finds rows with 'K', extracts number, multiplies by 1000
        mask_k = df['Qubits'].astype(str).str.contains('K', case=False)
        
        # Apply logic only to rows with 'K'
        df.loc[mask_k, 'Qubits'] = df.loc[mask_k, 'Qubits']\
            .astype(str).str.replace('K', '', case=False)\
            .astype(float) * 1000
    
    # Force conversion to numeric
    df['Qubits'] = pd.to_numeric(df['Qubits'], errors='coerce')
    
    # Drop invalid rows
    df = df.dropna(subset=['Qubits'])

    df["Roadmap_Year"] = df["Roadmap_Year"].astype(str)
    
    return df

def calculate_regression_data(df):
    """
    [EN] Performs log-linear regression and prepares LEGEND LABELS.
         Now, the 'label_text' is formatted to be a Legend Entry (Series Name),
         not a text annotation.
    [PT-BR] Realiza regressão log-linear e prepara RÓTULOS DE LEGENDA.
            Agora, o 'label_text' é formatado para ser uma Entrada de Legenda (Nome da Série),
            não uma anotação de texto.
    """
    reg_lines = []
    # No longer need separate label dataframe, as the label is part of the line data now
    # [PT-BR] Não precisamos mais de dataframe de rótulo separado, pois o rótulo faz parte dos dados da linha agora

    def process_fit(sub_df, roadmap_year, group_id, trend_name_short):
        if len(sub_df) < 2: return
        
        # Fit logic
        x = sub_df['Year'].values
        y = np.log2(sub_df['Qubits'].values)
        slope, intercept = np.polyfit(x, y, 1)
        
        # Generate Line
        x_range = np.array([x.min(), x.max()])
        y_pred = 2**(slope * x_range + intercept)
        
        # Calculate Rate for the Legend String
        if slope > 0:
            months = 12 / slope
            # Create a descriptive string for the legend
            # Ex: "Legacy (Double: 10.5 mo)"
            legend_str = f"{trend_name_short} (Double: {months:.1f} months)"
        else:
            legend_str = f"{trend_name_short} (No Growth)"
        
        line_data = pd.DataFrame({
            'Year': x_range,
            'Qubits': y_pred,
            'Roadmap_Year': roadmap_year,
            'Group_ID': group_id,
            'Legend_Label': legend_str # <--- New Column for Color Mapping
        })
        reg_lines.append(line_data)

    print("\n[DEBUG] Starting Regression Calculations...")

    # --- SCENARIO 1: Roadmap 2020 ---
    process_fit(df[df['Roadmap_Year'] == '2020'], '2020', 'Main', '2020 Roadmap')

    # --- SCENARIO 2: Roadmap 2022 ---
    df_2022 = df[(df['Roadmap_Year'] == '2022') & (df['Label'] != 'Heron')]
    process_fit(df_2022, '2022', 'Main', '2022 Roadmap')

    # --- SCENARIO 3: Roadmap 2025 (Split Trends) ---
    target_year = '2025' 
    if target_year not in df['Roadmap_Year'].unique():
        target_year = df['Roadmap_Year'].max()

    if target_year in df['Roadmap_Year'].unique():
        # Trend A: Old (Falcon -> Condor)
        df_old = df[
            (df['Roadmap_Year'] == target_year) & 
            (df['Year'] <= 2023) & 
            (~df['Label'].str.contains('Nighthawk', case=False, na=False)) &
            (df['Label'] != 'Heron')
        ]
        process_fit(df_old, target_year, 'Old_Trend', '2025 Roadmap')

        # Trend B: New (Nighthawk)
        df_new = df[
            (df['Roadmap_Year'] == target_year) & 
            (df['Label'].str.contains('Nighthawk', case=False, na=False))
        ]
        process_fit(df_new, target_year, 'New_Trend', '2025 Roadmap - Nighthawk')

    # Return only the lines dataframe (labels are now integrated as columns)
    return pd.concat(reg_lines) if reg_lines else pd.DataFrame(), None

def plot_roadmap_evolution(df, df_reg_lines, _ignored_labels):
    """
    [EN] Generates the chart with MANUAL COLORS for regressions.
    [PT-BR] Gera o gráfico com CORES MANUAIS para as regressões.
    """
    
    df['Label_Full'] = df.apply(lambda row: f"{row['Label']}\n({int(row['Qubits'])})", axis=1)

    # --- DEFINIÇÃO DE CORES MANUAIS ---
    # Coloque aqui as cores hexadecimais que você quer.
    # A ordem de atribuição geralmente é alfabética pelo nome da tendência:
    # 1. Legacy... (Ex: Vermelho para força bruta antiga)
    # 2. Trend 2020... (Ex: Azul padrão)
    # 3. Trend 2022... (Ex: Roxo)
    # 4. Utility... (Ex: Verde para a nova era sustentável)
    my_colors = ["#3498db", "#e74c3c", "#9b59b6", "#2ecc71"] 

    chart = (
        ggplot()
        
        # --- LAYER 1: REGRESSION LINES ---
        + geom_line(data=df_reg_lines, 
                    mapping=aes(x='Year', y='Qubits', color='Legend_Label', group='Group_ID'),
                    linetype='dashed', size=1.2, alpha=0.8)
        
        # --- LAYER 3: DATA POINTS ---
        + geom_point(data=df, 
                     mapping=aes(x='Year', y='Qubits', shape='Status'), 
                     color="#2c3e50", fill="#2c3e50", size=3.5)
        
        # --- LAYER 4: TEXT LABELS ---
        + geom_text(data=df,
                    mapping=aes(x='Year', y='Qubits', label='Label_Full'), 
                    nudge_y=0.25, size=7, color="#34495e", lineheight=0.9)
        
        # --- SCALES ---
        + facet_wrap('~Roadmap_Year', ncol=3, scales='free_x')
        
        + scale_y_continuous(
            trans='log2', 
            breaks=[32, 128, 512, 1024, 4096, 8192, 16384], 
            labels=["32", "128", "512", "1k", "4k", "8k", "16k"], 
            name="Physical Qubits (Log Scale)"
        )
        
        + scale_x_continuous(breaks=lambda limits: range(int(limits[0]), int(limits[1]) + 1), name="Year")
        
        # --- MUDANÇA AQUI: CORES MANUAIS ---
        + scale_color_manual(values=my_colors, name="Doubling Trends")
        
        + scale_shape_manual(values={"Executed": "o", "Forecast": "^"}, name="Project Status")
        
        + theme_bw()
        + theme(
            figure_size=(16, 7),
            #text=element_text(family="sans-serif"),
            axis_text_x=element_text(rotation=45, hjust=1, size=12),
            strip_background=element_rect(fill="#f0f2f5"), 
            strip_text=element_text(weight='bold', size=11),
            panel_grid_minor=element_blank(),
            legend_position="right", # Legenda na direita
            legend_key=element_blank(),
            legend_title=element_text(weight='bold'),
            text=element_text(family="Open Sans Semicondensed"),
            # 1. Título Principal (Aumentei para 22 e deixei negrito)
            plot_title=element_text(size=18, weight='bold'),
            # 2. Títulos dos Eixos ("Year", "Qubits") (Aumentei para 16)
            axis_title=element_text(size=16),
            # 3. Textos dos Eixos (Os números/anos) (Aumentei para 12)
            axis_text_y=element_text(size=12)
        )
        + labs(title="Quantum Supply Scaling: The Trajectory of Qubit Volume (IBM Roadmaps)")
    )
    
    return chart

def plot_standalone_2022(df, df_reg_lines):
    """
    [EN] Standalone chart for 2022 with LEGEND ON THE RIGHT.
    [PT-BR] Gráfico independente para 2022 com LEGENDA NA DIREITA.
    """
    
    df_2022 = df[df['Roadmap_Year'] == '2022'].copy()
    reg_2022 = df_reg_lines[df_reg_lines['Roadmap_Year'] == '2022'].copy()
    
    df_2022['Label_Full'] = df_2022.apply(lambda row: f"{row['Label']}\n({int(row['Qubits'])})", axis=1)

    # --- MUDANÇA DE COR AQUI ---
    # Coloque o código Hexadecimal da cor que você deseja.
    # Exemplos:
    # Vermelho: "#e74c3c"
    # Roxo:     "#8e44ad"
    # Laranja:  "#e67e22"
    # Azul IBM: "#3498db"
    
    my_single_color = ["#e74c3c"] # <--- TROQUE ESSE CÓDIGO PELA COR DESEJADA

    chart = (
        ggplot()
        + geom_line(data=reg_2022, 
                    mapping=aes(x='Year', y='Qubits', color='Legend_Label', group='Group_ID'),
                    linetype='dashed', size=1.2, alpha=0.8)
        
        + geom_point(data=df_2022, 
                     mapping=aes(x='Year', y='Qubits', shape='Status'), 
                     color="#2c3e50", fill="#2c3e50", size=4)
        
        + geom_text(data=df_2022,
                    mapping=aes(x='Year', y='Qubits', label='Label_Full'), 
                    nudge_y=0.25, size=7, color="#34495e", lineheight=0.9)
        
        + scale_y_continuous(
            trans='log2', 
            breaks=[32, 128, 512, 1024, 4096], 
            labels=["32", "128", "512", "1k", "4k"], 
            name="Physical Qubits (Log Scale)"
        )
        
        + scale_x_continuous(breaks=lambda limits: range(int(limits[0]), int(limits[1]) + 1), name="Year")
        
        # Aqui ele aplica a cor que você definiu acima
        + scale_color_manual(values=my_single_color, name="Doubling Trend")
        
        + scale_shape_manual(values={"Executed": "o", "Forecast": "^"}, name="Project Status")
        
        + theme_bw()
        + theme(
            figure_size=(16, 7),
            text=element_text(family="Open Sans Semicondensed"),
            axis_text_x=element_text(rotation=45, hjust=1, size=12),
            panel_grid_minor=element_blank(),
            legend_position="right", 
            legend_title=element_text(weight='bold'),

            # 1. Título Principal (Aumentei para 22 e deixei negrito)
            plot_title=element_text(size=18, weight='bold', ha='left'),
            
            # 2. Títulos dos Eixos ("Year", "Qubits") (Aumentei para 16)
            axis_title=element_text(size=16),
            
            # 3. Textos dos Eixos (Os números/anos) (Aumentei para 12)
            axis_text_y=element_text(size=12)
        )
        + labs(title="IBM Quantum Roadmap: The 2022 Perspective on Qubit Scaling")
    )
    
    return chart

if __name__ == "__main__":
    print("Loading data... / Carregando dados...")
    df = load_and_clean_data()
    
    if df is not None:
        print("Calculating regressions... / Calculando regressões...")
        df_lines, df_labels = calculate_regression_data(df)
        
        # 1. GENERATE THE FULL 3-PANEL CHART (Original)
        print("\nGenerating full comparison chart... / Gerando gráfico completo...")
        plot_full = plot_roadmap_evolution(df, df_lines, None)
        plot_full.save(os.path.join(FIGURES_PATH, "roadmap_evolution_full.png"), width=16, height=7, dpi=300)
        plot_full.save(os.path.join(FIGURES_PATH, "roadmap_evolution_full.pdf"), width=16, height=7)
        
        # 2. GENERATE THE 2022 STANDALONE CHART (New)
        print("Generating 2022 standalone chart... / Gerando gráfico 2022 isolado...")
        plot_2022 = plot_standalone_2022(df, df_lines)
        
        # Save with specific filename
        file_2022_png = os.path.join(FIGURES_PATH, "roadmap_2022_detail.png")
        file_2022_pdf = os.path.join(FIGURES_PATH, "roadmap_2022_detail.pdf")
        
        plot_2022.save(file_2022_png, width=10, height=7, dpi=300)
        plot_2022.save(file_2022_pdf, width=10, height=7)
        
        print(f"Done! Saved:\n - {file_2022_png}")