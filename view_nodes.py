import os
import pandas as pd

# Graceful import check for matplotlib to ensure zero-crash execution
try:
    import matplotlib.pyplot as plt  # type: ignore
    HAS_PLOTTING = True
except ImportError:
    plt = None
    HAS_PLOTTING = False

# 1. AUTO-DETECT THE PATH LOCALLY
# We search for common nodes file names in current and sub-directories.
target_files = [
    'NAICS_Contagion_Nodes_GitHub.csv',
    'NAICS_Contagion_Drop_GitHub.csv',
    'NAICS_Contagion_Nodes_Internal.csv'
]

path = ""
print("[Search] Searching for contagion nodes data file...")

# Walk through the current directory and its subdirectories
for root, dirs, files in os.walk('.'):
    # Exclude virtual envs or git folder to make it faster
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'env', 'venv', '.ipynb_checkpoints')]
    for file in files:
        if file in target_files:
            path = os.path.join(root, file)
            break
    if path:
        break

# If not found in current dir, check one level up (in case run from a subfolder)
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
    nodes_df = pd.read_csv(path)
    
    # 2. Show the top 10 Systemic Bottlenecks
    # Normalize column names just in case there are slight variations (e.g. NAICS Node ID vs NAICS Code ID)
    nodes_df.columns = [c.strip() for c in nodes_df.columns]
    
    score_col = 'Contagion Score' if 'Contagion Score' in nodes_df.columns else None
    name_col = 'Primary Name' if 'Primary Name' in nodes_df.columns else None
    tier_col = 'Supply Chain Tier' if 'Supply Chain Tier' in nodes_df.columns else None
    
    if score_col and name_col:
        print("--- TOP 10 SYSTEMIC ANCHOR NODES ---")
        cols_to_show = [name_col, score_col]
        if tier_col:
            cols_to_show.append(tier_col)
            
        top_risk = nodes_df.sort_values(by=score_col, ascending=False)[cols_to_show].head(10)
        print(top_risk.to_string(index=False))
    else:
        print("[Warning] Could not find 'Contagion Score' or 'Primary Name' columns.")
        print(f"Available columns: {list(nodes_df.columns)}")

    # 3. Simple Visualization of Risk by Tier
    if tier_col and score_col:
        if HAS_PLOTTING:
            print("\nPlotting Average Contagion Risk by Supply Chain Tier...")
            nodes_df.groupby(tier_col)[score_col].mean().plot(kind='bar', color='purple')
            plt.title('Average Contagion Risk by Supply Chain Tier')
            plt.ylabel('Mean Contagion Score')
            plt.xlabel('Supply Chain Tier')
            plt.tight_layout()
            plt.show()
        else:
            print("\nAverage Contagion Risk by Supply Chain Tier:")
            print(nodes_df.groupby(tier_col)[score_col].mean().round(2).to_string())
            print("\n[Tip] To generate a visual bar chart plot, run: pip install matplotlib")
            
    elif score_col:
        # Fallback to NAICS Sector if Supply Chain Tier is missing (e.g. in Github Drop CSV)
        group_col = 'NAICS Sector' if 'NAICS Sector' in nodes_df.columns else ('GICS Sector' if 'GICS Sector' in nodes_df.columns else None)
        if group_col:
            if HAS_PLOTTING:
                print(f"\nPlotting Average Contagion Risk by {group_col} (Supply Chain Tier not found)...")
                nodes_df.groupby(group_col)[score_col].mean().sort_values().plot(kind='barh', color='purple')
                plt.title(f'Average Contagion Risk by {group_col}')
                plt.xlabel('Mean Contagion Score')
                plt.ylabel(group_col)
                plt.tight_layout()
                plt.show()
            else:
                print(f"\nAverage Contagion Risk by {group_col} (Supply Chain Tier not found):")
                print(nodes_df.groupby(group_col)[score_col].mean().round(2).sort_values(ascending=False).to_string())
                print("\n[Tip] To generate a visual horizontal bar chart plot, run: pip install matplotlib")
else:
    print("[Error] Could not find any of the contagion files:")
    for f in target_files:
        print(f"  - {f}")
    print("\nPlease place the CSV file in the same directory as this script.")
