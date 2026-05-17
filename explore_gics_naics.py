import os
import pandas as pd

# Graceful import check for plotting libraries to prevent crashes
try:
    import matplotlib.pyplot as plt  # type: ignore
    import seaborn as sns  # type: ignore
    HAS_PLOTTING = True
except ImportError:
    plt = None
    sns = None
    HAS_PLOTTING = False

# 1. AUTO-DETECT THE PATH LOCALLY
target_files = [
    'NAICS_Contagion_Nodes_GitHub.csv',
    'NAICS_Contagion_Drop_GitHub.csv',
    'NAICS_Contagion_Nodes_Internal.csv'
]

path = ""
print("[Search] Searching for contagion nodes data file to analyze NAICS-GICS mappings...")

# Walk through the current directory and its subdirectories
for root, dirs, files in os.walk('.'):
    # Exclude virtual envs, git, and build folders
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'env', 'venv', '.ipynb_checkpoints')]
    for file in files:
        if file in target_files:
            path = os.path.join(root, file)
            break
    if path:
        break

# If not found, check one level up
if not path:
    for root, dirs, files in os.walk('..'):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'env', 'venv', '.ipynb_checkpoints')]
        for file in files:
            if file in target_files:
                path = os.path.join(root, file)
                break
        if path:
            break

if path:
    print(f"[Success] Loading data from: {path}\n")
    df = pd.read_csv(path)
    
    # Strip whitespace from column names and string values
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype(str).str.strip()

    # Determine column names in the dataset
    primary_name_col = 'Primary Name' if 'Primary Name' in df.columns else None
    gics_sub_col = 'GICS Sub Industry' if 'GICS Sub Industry' in df.columns else None
    score_col = 'Contagion Score' if 'Contagion Score' in df.columns else None
    tier_col = 'Supply Chain Tier' if 'Supply Chain Tier' in df.columns else None

    if primary_name_col and gics_sub_col:
        print("=" * 80)
        print("  PHYSICAL TO FINANCIAL ECONOMIC CROSSOVER (NAICS -> GICS)")
        print("=" * 80)
        
        # Ensure score column is numeric
        if score_col:
            df[score_col] = pd.to_numeric(df[score_col], errors='coerce')
            
        # 1. Group by GICS Financial Sub-Industry to analyze profiles
        print("\n[Data] GICS FINANCIAL SUB-INDUSTRY RISK PROFILE:")
        print("-" * 80)
        
        # Calculate count and mean contagion score per GICS Sub Industry
        gics_profile = df.groupby(gics_sub_col).agg(
            Physical_Nodes_Count=(primary_name_col, 'count'),
            Avg_Contagion_Score=(score_col, 'mean')
        ).reset_index()
        
        # Find the highest-risk individual physical node in each GICS sub-industry
        top_nodes = []
        for g_sub in gics_profile[gics_sub_col]:
            sub_df = df[df[gics_sub_col] == g_sub]
            if not sub_df.empty and score_col:
                top_node = sub_df.sort_values(by=score_col, ascending=False).iloc[0]
                top_nodes.append(f"{top_node[primary_name_col][:40].strip()} ({top_node[score_col]:.1f})")
            else:
                top_nodes.append("N/A")
        gics_profile['Top Risk Physical Node'] = top_nodes
        
        # Sort descending by contagion score
        gics_profile = gics_profile.sort_values(by='Avg_Contagion_Score', ascending=False)
        print(gics_profile.to_string(index=False))
        print("-" * 80)

        # 2. Top 10 Individual Node Systemic Risk Hotspots (Primary Name -> GICS Sub Industry)
        if score_col:
            print("\n[Hotspots] TOP 10 PHYSICAL-FINANCIAL SYSTEMIC RISK HOTSPOTS:")
            print("-" * 80)
            top_hotspots = df.sort_values(by=score_col, ascending=False).head(10)
            for idx, row in top_hotspots.iterrows():
                bar = '#' * int(row[score_col] * 2.5)
                print(f" {row[primary_name_col][:45].strip():<45} -> {row[gics_sub_col][:25].strip():<25} | {row[score_col]:.2f} {bar}")
            print("-" * 80)

        # 3. Structural Risk Matrices
        if tier_col and score_col:
            # Matrix 1: Average Contagion Score by Supply Chain Tier vs. GICS Sub-Industry
            print("\n[Risk Matrix 1] AVERAGE CONTAGION SCORE BY SUPPLY CHAIN TIER vs. GICS SUB-INDUSTRY:")
            print("-" * 80)
            matrix_avg_gics = df.pivot_table(
                values=score_col,
                index=gics_sub_col,
                columns=tier_col,
                aggfunc='mean'
            ).fillna(0)
            print(matrix_avg_gics.round(2).to_string())
            print("-" * 80)

            # Matrix 2: Highest Contagion Score by Supply Chain Tier vs. GICS Sub-Industry
            print("\n[Risk Matrix 2] HIGHEST CONTAGION SCORE BY SUPPLY CHAIN TIER vs. GICS SUB-INDUSTRY:")
            print("-" * 80)
            matrix_max_gics = df.pivot_table(
                values=score_col,
                index=gics_sub_col,
                columns=tier_col,
                aggfunc='max'
            ).fillna(0)
            print(matrix_max_gics.round(2).to_string())
            print("-" * 80)

            # Matrix 3: Average Contagion Score by Supply Chain Tier vs. NAICS Primary (Top 15)
            print("\n[Risk Matrix 3] AVERAGE CONTAGION SCORE BY SUPPLY CHAIN TIER vs. NAICS PRIMARY (Top 15 Most Systemic):")
            print("-" * 80)
            matrix_avg_naics = df.pivot_table(
                values=score_col,
                index=primary_name_col,
                columns=tier_col,
                aggfunc='mean'
            ).fillna(0)
            # Sort by maximum row risk to bubble up top vulnerabilities
            matrix_avg_naics_sorted = matrix_avg_naics.reindex(
                matrix_avg_naics.max(axis=1).sort_values(ascending=False).index
            )
            print(matrix_avg_naics_sorted.head(15).round(2).to_string())
            print(f"... showing top 15 of {len(matrix_avg_naics)} NAICS Primary industries (ordered by peak risk) ...")
            print("-" * 80)

            # Matrix 4: Highest Contagion Score by Supply Chain Tier vs. NAICS Primary (Top 15)
            print("\n[Risk Matrix 4] HIGHEST CONTAGION SCORE BY SUPPLY CHAIN TIER vs. NAICS PRIMARY (Top 15 Most Systemic):")
            print("-" * 80)
            matrix_max_naics = df.pivot_table(
                values=score_col,
                index=primary_name_col,
                columns=tier_col,
                aggfunc='max'
            ).fillna(0)
            # Sort by maximum row risk to bubble up top vulnerabilities
            matrix_max_naics_sorted = matrix_max_naics.reindex(
                matrix_max_naics.max(axis=1).sort_values(ascending=False).index
            )
            print(matrix_max_naics_sorted.head(15).round(2).to_string())
            print(f"... showing top 15 of {len(matrix_max_naics)} NAICS Primary industries (ordered by peak risk) ...")
            print("-" * 80)

            # Heatmap Visualization Dashboard if packages are available
            if HAS_PLOTTING:
                fig, axes = plt.subplots(1, 2, figsize=(24, 11))
                
                # Subplot 1: Average Contagion Risk Heatmap
                sns.heatmap(matrix_avg_gics, annot=True, cmap='coolwarm', fmt=".2f", ax=axes[0], cbar_kws={'label': 'Mean Contagion Score'})
                axes[0].set_title('Average Contagion Risk by GICS Sub-Industry & Supply Chain Tier', fontsize=14, fontweight='bold', pad=10)
                axes[0].set_ylabel('GICS Sub Industry', fontsize=12)
                axes[0].set_xlabel('Supply Chain Tier (1 = Immediate, 3 = Deep Tier)', fontsize=12)
                
                # Subplot 2: Highest Contagion Risk Heatmap
                sns.heatmap(matrix_max_gics, annot=True, cmap='coolwarm', fmt=".2f", ax=axes[1], cbar_kws={'label': 'Max Contagion Score'})
                axes[1].set_title('Highest Contagion Risk by GICS Sub-Industry & Supply Chain Tier', fontsize=14, fontweight='bold', pad=10)
                axes[1].set_ylabel('')  # Clear label for side-by-side neatness
                axes[1].set_xlabel('Supply Chain Tier (1 = Immediate, 3 = Deep Tier)', fontsize=12)
                
                plt.suptitle('Physical-Financial Economy Crossover Contagion Analytics Dashboard', fontsize=18, fontweight='bold', y=0.98)
                plt.tight_layout()
                
                output_image = 'naics_gics_risk_heatmaps.png'
                plt.savefig(output_image, dpi=150)
                print(f"\n[Plot] Heatmap dashboard successfully generated and saved as: {output_image}")
                plt.show()
            else:
                print("\n[Tip] To generate beautiful visual heatmap subplots, run: pip install matplotlib seaborn")
    else:
        print("[Error] Could not locate 'Primary Name' or 'GICS Sub Industry' columns in the dataset.")
        print(f"Available columns: {list(df.columns)}")
else:
    print("[Error] Could not find any of the contagion files:")
    for f in target_files:
        print(f"  - {f}")
    print("\nPlease place the CSV file in the same directory as this script.")
