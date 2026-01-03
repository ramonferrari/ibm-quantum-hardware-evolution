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


## Library Import and Environment Setup
## [PT-BR] Importação de Bibliotecas e Configuração do Ambiente
import pandas as pd
import numpy as np
from plotnine import *
import os

# --- CONFIGURATION
# --- CONFIGURAÇÃO 
# using os.path.join ensures compatibility across Windows/Linux/Mac
DATA_PATH = os.path.join("data", "database-quantum-qubits.csv")
FIGURES_PATH = os.path.join("figures")

# ensure the output directory exists to prevent IOErrors later
os.makedirs(FIGURES_PATH, exist_ok=True)

def load_and_clean_data():
    """
    [EN] Loads raw CSV data, cleans numeric columns (handling 'K' or ','), and types columns.
    [PT-BR] Carrega dados CSV, limpa colunas numéricas (tratando 'K' ou ',') e tipa colunas.
    """
    ## File Existence Check and Loading
    ## [PT-BR] Verificação de Existência de Arquivo e Carregamento
    if not os.path.exists(DATA_PATH):
        print(f"[WARNING] File {DATA_PATH} not found.")
        return None
    else:
        df = pd.read_csv(DATA_PATH)

    # renaming columns early simplifies downstream access (dot notation compatible)
    df = df.rename(columns={
        "Year (Roadmap)": "Roadmap_Year",
        "Qubit counts": "Qubits",
        "Expected Qubit Counts": "Status"
    })
    
    ## Data Sanitization (String to Float Conversion)
    ## [PT-BR] Higienização de Dados (Conversão de String para Float)

    # Critical step: Convert "7.5K" or "10,000" strings to floats.
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
    
    ## Final Type Enforcement and Validation
    ## [PT-BR] Aplicação Final de Tipos e Validação
    # Force conversion to numeric, turning unparseable data into NaN

    df['Qubits'] = pd.to_numeric(df['Qubits'], errors='coerce')
    
    # Drop invalid rows (essential for log scale plotting later)
    df = df.dropna(subset=['Qubits'])

    # Drop invalid rows (essential for log scale plotting later)
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


    ## Helper Function for Curve Fitting
    ## [PT-BR] Função Auxiliar para Ajuste de Curvas
    def process_fit(sub_df, roadmap_year, group_id, trend_name_short):
        # ensure we have enough points to fit a line
        if len(sub_df) < 2: return
        
        # Fit logic: Log-Linear Regression (Moore's Law style)
        # We fit Y = log2(Qubits) vs X = Year to find the doubling rate
        
        x = sub_df['Year'].values
        y = np.log2(sub_df['Qubits'].values)
        slope, intercept = np.polyfit(x, y, 1)
        
        # Generate Line points for plotting (start and end only)
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

    ## Scenario 1: 2020 Roadmap (Baseline)
    ## [PT-BR] Cenário 1: Roadmap 2020 (Linha de Base)
    process_fit(df[df['Roadmap_Year'] == '2020'], '2020', 'Main', '2020 Roadmap')

    ## Scenario 2: 2022 Roadmap (Filtering Outliers)
    ## [PT-BR] Cenário 2: Roadmap 2022 (Filtrando Outliers)

    # Exclude 'Heron' as it represents a shift to quality over quantity, 
    # which would skew the regression of the scaling trend.

    df_2022 = df[(df['Roadmap_Year'] == '2022') & (df['Label'] != 'Heron')]
    process_fit(df_2022, '2022', 'Main', '2022 Roadmap')

    ## Scenario 3: 2025 Roadmap (Divergent Trends)
    ## [PT-BR] Cenário 3: Roadmap 2025 (Tendências Divergentes)
    target_year = '2025' 
    if target_year not in df['Roadmap_Year'].unique():
        target_year = df['Roadmap_Year'].max()

    if target_year in df['Roadmap_Year'].unique():
        # Trend A: The "Legacy" scaling path (Falcon -> Condor)
        # Excludes new architectures (Nighthawk) and modular chips (Heron)

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
    # Using concatenation handles empty lists gracefully
    return pd.concat(reg_lines) if reg_lines else pd.DataFrame(), None

## Full Roadmap Evolution Plotting
## [PT-BR] Plotagem da Evolução Completa dos Roadmaps
def plot_roadmap_evolution(df, df_reg_lines, _ignored_labels):
    """
    [EN] Generates the chart with MANUAL COLORS for regressions.
    [PT-BR] Gera o gráfico com CORES MANUAIS para as regressões.
    """
    
    ## Data Preparation for Plotting
    ## [PT-BR] Preparação dos Dados para Plotagem
    # Pre-formatting labels prevents clutter inside the plot definition
    df['Label_Full'] = df.apply(lambda row: f"{row['Label']}\n({int(row['Qubits'])})", axis=1)

    # --- PALETTE CONFIGURATION / CONFIGURAÇÃO DA PALETA ---
    # [EN] Manual hex codes assigned to specific trend lines
    # [PT-BR] Códigos hex manuais atribuídos a linhas de tendência específicas

    # 1. Legacy (Blue), 2. Trend 2020 (Red), 3. Trend 2022 (Purple), 4. Utility (Green)

    my_colors = ["#3498db", "#e74c3c", "#9b59b6", "#2ecc71"] 

    chart = (
        ggplot()
        
        ## Layer 1: Regression Lines (Background)
        ## [PT-BR] Camada 1: Linhas de Regressão (Fundo)
        + geom_line(data=df_reg_lines, 
                    mapping=aes(x='Year', y='Qubits', color='Legend_Label', group='Group_ID'),
                    linetype='dashed', size=1.2, alpha=0.8)
        
        ## Layer 2: Data Points (Middle)
        ## [PT-BR] Camada 2: Pontos de Dados (Meio)
        + geom_point(data=df, 
                     mapping=aes(x='Year', y='Qubits', shape='Status'), 
                     color="#2c3e50", fill="#2c3e50", size=3.5)
        
        ## Layer 3: Text Annotations (Foreground)
        ## [PT-BR] Camada 3: Anotações de Texto (Frente)
        + geom_text(data=df,
                    mapping=aes(x='Year', y='Qubits', label='Label_Full'), 
                    nudge_y=0.25, size=9, color="#34495e", lineheight=0.9)
        
        ## Structural Faceting
        ## [PT-BR] Facetamento Estrutural
        # 'scales=free_x' allows each panel to have its own year range
        + facet_wrap('~Roadmap_Year', ncol=3, scales='free_x')
        
        ## Axis Scaling Configuration
        ## [PT-BR] Configuração de Escala dos Eixos
        + scale_y_continuous(
            trans='log2', 
            breaks=[32, 128, 512, 1024, 4096, 8192, 16384], 
            labels=["32", "128", "512", "1k", "4k", "8k", "16k"], 
            name="Physical Qubits (Log Scale)"
        )
        
        # [EN] Dynamic X-Axis Logic (Asymmetric Cushion)
        # [PT-BR] Lógica Dinâmica do Eixo X (Almofada Assimétrica)
        + scale_x_continuous(
            # Lambda ensures breaks are always integers based on data limits
            breaks=lambda limits: range(int(limits[0]), int(limits[1]) + 1),
            
            name="Year",
            
            # Lambda calculates dynamic limits: adds 1.5 years padding to the right for labels
            limits=lambda l: (l[0] - 0.9, l[1] + 0.9),
            
            # Expand=0 forces strict adherence to the limits calculated above
            expand=(0, 0)
        )
        
        ## Legend & Color Mapping
        ## [PT-BR] Mapeamento de Legenda e Cores
        + scale_color_manual(values=my_colors, name="Doubling Trends")
        + scale_shape_manual(values={"Executed": "o", "Forecast": "^"}, name="Project Status")
        
        ## Theme & Design System
        ## [PT-BR] Tema e Sistema de Design
        + theme_bw()
        + theme(
            figure_size=(16, 7),
            text=element_text(family="Open Sans Semicondensed"),

            # Grid & Backgrounds
            panel_grid_minor=element_blank(),
            plot_background=element_rect(fill='None', color='None'),  # Remove fundo da imagem total
            panel_background=element_rect(fill='None', color='None'), # Remove fundo da área do gráfico
            strip_background=element_rect(fill="#f0f2f5"), 

            # Typography Hierarchy
            axis_text_x=element_text(rotation=45, hjust=1, size=12),
             # Título Principal 
            plot_title=element_text(size=18, weight='bold'),
            # Títulos dos Eixos ("Year", "Qubits") 
            axis_title=element_text(size=16),
            # Textos dos Eixos (Os números/anos) 
            axis_text_y=element_text(size=12),
            strip_text=element_text(weight='bold', size=11),

            # Legend Styling
            legend_position="right", # Legenda na direita
            legend_background=element_rect(fill='None'),
            legend_key=element_blank(),
            legend_title=element_text(weight='bold')
        )
        + labs(title="Quantum Supply Scaling: The Trajectory of Qubit Volume (IBM Roadmaps)")
    )
    
    return chart

def plot_standalone_2022(df, df_reg_lines):
    """
    [EN] Standalone chart for 2022 with legend on the right.
    [PT-BR] Gráfico independente para 2022 com legenda na direita.
    """
    
    ## Data Isolation and Preparation
    ## [PT-BR] Isolamento e Preparação dos Dados
    # Using .copy() is essential to avoid SettingWithCopy warnings when modifying df later

    df_2022 = df[df['Roadmap_Year'] == '2022'].copy()
    reg_2022 = df_reg_lines[df_reg_lines['Roadmap_Year'] == '2022'].copy()
    
    # Pre-formatting the label with newline characters for vertical stacking
    df_2022['Label_Full'] = df_2022.apply(lambda row: f"{row['Label']}\n({int(row['Qubits'])})", axis=1)

    # --- VISUAL CONFIGURATION / CONFIGURAÇÃO VISUAL ---
    # [EN] Single color for the trend line (Red for high visibility)
    # [PT-BR] Cor única para a linha de tendência (Vermelho para alta visibilidade)
    my_single_color = ["#e74c3c"] # <--- trocar código pela cor desejada
    
    # [EN] Dynamic Padding Calculation for X-Axis
    # [PT-BR] Cálculo Dinâmico de Espaçamento (Padding) para o Eixo X
    # We explicitly calculate limits to ensure text labels fit within the plot area.
    min_year = int(df_2022['Year'].min())
    max_year = int(df_2022['Year'].max())
    
    # Adding 0.5 padding on both sides creates a balanced "cushion"
    limit_min = min_year - 0.5
    limit_max = max_year + 0.5

    chart = (
        ggplot()
        ## Layer 1: Trend Line
        ## [PT-BR] Camada 1: Linha de Tendência
        + geom_line(data=reg_2022, 
                    mapping=aes(x='Year', y='Qubits', color='Legend_Label', group='Group_ID'),
                    linetype='dashed', size=1.2, alpha=0.8)

        ## Layer 2: Data Points
        ## [PT-BR] Camada 2: Pontos de Dados
        + geom_point(data=df_2022, 
                     mapping=aes(x='Year', y='Qubits', shape='Status'), 
                     color="#2c3e50", fill="#2c3e50", size=4)
        
        ## Layer 3: Text Labels
        ## [PT-BR] Camada 3: Rótulos de Texto
        + geom_text(data=df_2022,
                    mapping=aes(x='Year', y='Qubits', label='Label_Full'), 
                    nudge_y=0.25, size=9, color="#34495e", lineheight=0.9)
        
        ## Axis Scales
        ## [PT-BR] Escalas dos Eixos
        + scale_y_continuous(
            trans='log2', 
            breaks=[32, 128, 512, 1024, 4096], 
            labels=["32", "128", "512", "1k", "4k"], 
            name="Physical Qubits (Log Scale)"
        )
        
        + scale_x_continuous(
            # Using the pre-calculated limits creates a stable viewport
            limits=[limit_min, limit_max],
            breaks=range(min_year, max_year + 2), 
            name="Year"
        )
        
        ## Legend Configuration
        ## [PT-BR] Configuração da Legenda
        + scale_color_manual(values=my_single_color, name="Doubling Trend")
        + scale_shape_manual(values={"Executed": "o", "Forecast": "^"}, name="Project Status")
        
        ## Theme & Design System
        ## [PT-BR] Tema e Sistema de Design
        + theme_bw()
        + theme(
            figure_size=(16, 7),
            text=element_text(family="Open Sans Semicondensed"),

            # Layout & Alignment
            legend_position="right", 
            axis_text_x=element_text(rotation=45, hjust=1, size=12),

            # Typography
            plot_title=element_text(size=18, weight='bold', ha='center'),
            plot_subtitle=element_text(size=14, ha='center', margin={'b': 15}),
            axis_title=element_text(size=16),
            axis_text_y=element_text(size=12),
            legend_title=element_text(weight='bold'),

            # Backgrounds & Grids (Transparency)
            panel_grid_minor=element_blank(),
            legend_background=element_rect(fill='None'),
            plot_background=element_rect(fill='None', color='None'),  # Remove fundo da imagem total
            panel_background=element_rect(fill='None', color='None') # Remove fundo da área do gráfico
        )
        + labs(
            title="Quantum Supply Scaling",
            subtitle="Projected Qubit Counts in the 2022 Perspective (IBM Quantum Roadmap)"
        )
    )
    
    return chart

## Graphical Abstract Generation (High Contrast/Thumbnail)
## [PT-BR] Geração do Resumo Gráfico (Alto Contraste/Miniatura)
def plot_graphical_abstract(df, df_reg_lines):

    """
    [EN] Graphical Abstract - Adjusted Layout.
         - Colors: Purple Circles (Executed) vs Pink Triangles (Forecast).
    """
    
    ## Data Preparation & Filtering
    ## [PT-BR] Preparação e Filtragem de Dados
    # We create copies to ensure we are working with a distinct slice of memory
    df_2022 = df[df['Roadmap_Year'] == '2022'].copy()
    reg_2022 = df_reg_lines[df_reg_lines['Roadmap_Year'] == '2022'].copy()
    
    # --- VISUAL CONSTANTS / CONSTANTES VISUAIS ---
    abstract_color = "#aa0069" 
    
    # [EN] Mapping dictionaries for specific visual encoding
    # [PT-BR] Dicionários de mapeamento para codificação visual específica    
    point_colors = {
        "Executed": "#8e44ad", # Roxo
        "Forecast": "#ff79cb"  # Rosa
    }
    
    point_shapes = {
        "Executed": "o", 
        "Forecast": "^"
    }
    
    # Text annotation content
    reg_text = "Doubling Rate:\n~10 Months"

    chart = (
        ggplot()

        ## Layer 1: Trend Line (Thick & Dashed)
        ## [PT-BR] Camada 1: Linha de Tendência (Grossa e Tracejada)
        + geom_line(data=reg_2022, 
                    mapping=aes(x='Year', y='Qubits', group='Group_ID'),
                    color=abstract_color,
                    linetype='dashed', size=2.5, alpha=0.9)

        ## Layer 2: Data Points (The Focus)
        ## [PT-BR] Camada 2: Pontos de Dados (O Foco)
        # Critical Design Choice: 
        # We use 'fill' inside AES for data coding (Pink/Purple).
        # We use 'color' outside AES for a static dark border (#2c3e50).
        + geom_point(data=df_2022, 
                     mapping=aes(x='Year', y='Qubits', 
                                 shape='Status', 
                                 fill='Status'), # Preenchimento mapeado
                     color="#2c3e50",            # Borda fixa escura (para contraste)
                     stroke=1.5,                 # Borda grossa
                     size=9)
        
        ## Layer 3: Manual Annotation
        ## [PT-BR] Camada 3: Anotação Manual
        # Positioned manually (x=2021, y=300) to sit cleanly in empty space
        + annotate("text", x=2021, y=300, 
                   label=reg_text, color=abstract_color, 
                   size=16, 
                   fontweight="bold", 
                   ha='center')
        
        ## Scales (Logarithmic & Manual Mappings)
        ## [PT-BR] Escalas (Logarítmicas e Mapeamentos Manuais)
        + scale_y_continuous(
            trans='log2', 
            breaks=[32, 128, 512, 1024, 4096, 16384], 
            labels=["32", "128", "512", "1k", "4k", "16k"], 
            name="Physical Qubits"
        )
        
        + scale_x_continuous(
            breaks=range(2019, 2027,2), 
            name="Year"
        )
        
        # Mapeia as formas (Círculo e Triângulo)
        + scale_shape_manual(values=point_shapes, name="Project Status")
        # Mapeia as cores (Roxo e Rosa)
        + scale_fill_manual(values=point_colors, name="Project Status")
        
       ## Theme: High Contrast / Large Fonts
        ## [PT-BR] Tema: Alto Contraste / Fontes Grandes
        + theme_bw()
        + theme(
            figure_size=(8, 8),
            text=element_text(family="Open Sans Semicondensed"),

            # Removal of backgrounds for transparency            
            plot_background=element_rect(fill='None', color='None'),
            panel_background=element_rect(fill='None', color='None'),
            legend_background=element_rect(fill='None', color='None'),
            
            # Title Hierarchy (Bold and Large)
            plot_title=element_text(size=32, weight='bold', ha='center'),
            plot_subtitle=element_text(size=24, ha='center', margin={'b': 20}),
            
            # Axis Typography
            axis_title=element_text(size=24, weight='bold'),
            axis_text=element_text(size=20,color="black"),
            
            # Legend Positioning (Inside Plot, Top-Left)
            legend_justification=('left', 'top'),
            legend_position=(0.075, 0.92),
            legend_title=element_text(size=16, weight='bold'),
            legend_text=element_text(size=16),
            legend_key=element_blank(),

            # Borders and Grids
            panel_border=element_rect(color="black", size=1.5),
            axis_ticks=element_line(size=2, color="black"),
            panel_grid_major=element_line(size=1.2, color="#a2a2a2"), 
        )
        + labs(
            title="Quantum Moore's Law",
            subtitle="Supply Scaling (IBM Roadmap)"
        )
    )
    
    return chart

## Main Execution Logic
## [PT-BR] Lógica Principal de Execução
if __name__ == "__main__":
    print("Loading data... / Carregando dados...")

    # 1. ETL Pipeline Trigger
    df = load_and_clean_data()
    
    # Safety check: prevent execution if data loading failed
    if df is not None:
        print("Calculating regressions... / Calculando regressões...")
        # Calculate trends once, reuse for all charts
        # Returns tuple: (lines_dataframe, ignored_labels)
        df_lines, df_labels = calculate_regression_data(df)
        
        # --- OUTPUT 1: FULL COMPARISON CHART ---        
        print("\nGenerating full comparison chart... / Gerando gráfico completo...")
        plot_full = plot_roadmap_evolution(df, df_lines, None)

        # Standard academic width (16x7) for broad landscape views
        # Transparent background allows flexible placement in layouts
        plot_full.save(os.path.join(FIGURES_PATH, "roadmap_evolution_full.png"), width=16, height=7, dpi=300,transparent=True)
        plot_full.save(os.path.join(FIGURES_PATH, "roadmap_evolution_full.pdf"), width=16, height=7,dpi=300,transparent=True)
        
        # --- OUTPUT 2: 2022 STANDALONE DETAIL ---
        print("Generating 2022 standalone chart... / Gerando gráfico 2022 isolado...")
        plot_2022 = plot_standalone_2022(df, df_lines)
        
        # Save with specific filename
        file_2022_png = os.path.join(FIGURES_PATH, "roadmap_2022_detail.png")
        file_2022_pdf = os.path.join(FIGURES_PATH, "roadmap_2022_detail.pdf")
        
        # Reduced width (10x7) keeps focus tight on the single timeline
        plot_2022.save(file_2022_png, width=10, height=7, dpi=300,transparent=True)
        plot_2022.save(file_2022_pdf, width=10, height=7,dpi=300,transparent=True)

        # --- OUTPUT 3: GRAPHICAL ABSTRACT ---
        print("Generating Graphical Abstract...")
        plot_abstract = plot_graphical_abstract(df, df_lines)
        
        file_abstract_png = os.path.join(FIGURES_PATH, "roadmap_2022_graphical_abstract.png")
        file_abstract_pdf = os.path.join(FIGURES_PATH, "roadmap_2022_graphical_abstract.pdf")
        
        # Near-square aspect ratio (8x9) is standard for thumbnails/sidebars
        plot_abstract.save(file_abstract_png, width=8, height=9, dpi=300, transparent=True)
        plot_abstract.save(file_abstract_pdf, width=8, height=9, transparent=True)
        
        print(f"Done! Saved:\n - {file_2022_png}")