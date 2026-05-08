import pandas as pd
import numpy as np
import os
from difflib import get_close_matches

def get_test_materials():
    """
    Returns the specific material commodity mappings for anchor industries.
    """
    return {
        "336110": [
            ("MAT_STL_01", "Steel", "720839", "CME: HRC", "China", "54%", "India", "6%", "Japan", "5%", "China", "54%", "India", "6%", "Japan", "5%", "Bulk Rail / Container Ships", "High", "MAT_ALU_01", "Medium", ["sheet metal", "chassis"]),
            ("MAT_ALU_01", "Aluminum", "760120", "LME: ALI", "China", "59%", "India", "6%", "Russia", "5%", "China", "59%", "India", "6%", "Russia", "5%", "Container Ships / Rail", "High", "MAT_STL_01", "Medium", ["alloy ingots", "lightweighting"]),
            ("MAT_COP_01", "Copper", "740311", "COMEX: HG", "Chile", "24%", "Peru", "10%", "China", "9%", "China", "42%", "Chile", "10%", "Japan", "6%", "Container Ships / Rail", "High", "MAT_ALU_01", "Low", ["EV wiring harness", "red metal"]),
            ("MAT_LIT_01", "Lithium Carbonate", "283691", "CME: LCO", "Australia", "47%", "Chile", "26%", "China", "16%", "China", "65%", "Chile", "29%", "Argentina", "5%", "Container Ships", "High", "MAT_SOD_01", "Low", ["EV inputs", "battery metals"]),
            ("MAT_COB_01", "Cobalt", "810520", "LME: CO", "Congo (DRC)", "70%", "Indonesia", "5%", "Russia", "4%", "China", "75%", "Finland", "10%", "Canada", "5%", "General Cargo Ships", "High", "None", "Low", ["battery cathode", "superalloys"]),
            ("MAT_NIC_01", "Nickel", "750210", "LME: NI", "Indonesia", "48%", "Philippines", "10%", "Russia", "6%", "China", "35%", "Indonesia", "30%", "Japan", "8%", "Bulk / Container Ships", "High", "None", "Low", ["EV cathode", "stainless steel"]),
            ("MAT_PAL_01", "Palladium", "711031", "NYMEX: PA", "Russia", "40%", "South Africa", "38%", "Canada", "9%", "Russia", "40%", "South Africa", "38%", "USA", "10%", "Air Cargo", "Medium", "MAT_PLT_01", "High", ["catalytic converters", "emissions"]),
            ("MAT_PLT_01", "Platinum", "711011", "NYMEX: PL", "South Africa", "70%", "Russia", "10%", "Zimbabwe", "8%", "South Africa", "70%", "UK", "10%", "Russia", "10%", "Air Cargo", "Medium", "MAT_PAL_01", "Medium", ["catalytic converters"]),
            ("MAT_RUB_01", "Natural Rubber", "400122", "SGX: TF", "Thailand", "35%", "Indonesia", "25%", "Vietnam", "8%", "Thailand", "35%", "Indonesia", "25%", "Malaysia", "10%", "Container Ships", "Low", "MAT_SYN_01", "High", ["tires", "vulcanized rubber"]),
            ("MAT_PLA_01", "Polypropylene", "390210", "LME: PP", "China", "30%", "USA", "12%", "Saudi Arabia", "6%", "China", "30%", "USA", "12%", "EU", "10%", "Container Ships / Rail", "Low", "MAT_PLA_02", "High", ["auto bumpers", "plastics"])
        ],
        "324110": [
            ("MAT_CRD_01", "Crude Oil", "270900", "NYMEX: CL", "USA", "20%", "Saudi Arabia", "12%", "Russia", "11%", "USA", "20%", "China", "18%", "India", "7%", "Oil Tankers / Pipelines", "High", "None", "Low", ["fossil fuels", "unrefined"]),
            ("MAT_NGS_01", "Natural Gas", "271121", "NYMEX: NG", "USA", "24%", "Russia", "17%", "Iran", "6%", "USA", "24%", "Russia", "17%", "Qatar", "6%", "Pipelines / LNG Carriers", "High", "None", "Low", ["LNG", "methane", "energy input"]),
            ("MAT_PLT_01", "Platinum", "711011", "NYMEX: PL", "South Africa", "70%", "Russia", "10%", "Zimbabwe", "8%", "South Africa", "70%", "UK", "10%", "Russia", "10%", "Air Cargo", "Medium", "MAT_PAL_01", "Medium", ["refining catalysts", "cracking"])
        ],
        "334410": [
            ("MAT_SIL_01", "Polysilicon", "280461", "Unlisted", "China", "80%", "USA", "6%", "Germany", "5%", "China", "80%", "USA", "6%", "Taiwan", "5%", "Container Ships", "High", "None", "Low", ["silicon wafers", "semiconductors"]),
            ("MAT_GAL_01", "Gallium", "811292", "Unlisted", "China", "98%", "Russia", "1%", "Japan", "1%", "China", "98%", "USA", "1%", "Japan", "1%", "Air Cargo", "Medium", "None", "Low", ["gallium arsenide", "wafers"]),
            ("MAT_GER_01", "Germanium", "811292", "Unlisted", "China", "60%", "Russia", "10%", "USA", "5%", "China", "60%", "USA", "10%", "Canada", "5%", "Air Cargo", "Medium", "None", "Low", ["metalloids", "fiber optics"]),
            ("MAT_TAN_01", "Tantalum", "810320", "Unlisted", "Congo (DRC)", "40%", "Rwanda", "20%", "Brazil", "15%", "China", "30%", "USA", "25%", "Germany", "15%", "Air Cargo / Container Ships", "Low", "MAT_NIO_01", "Medium", ["capacitors", "electronics"]),
            ("MAT_HEL_01", "Helium", "280429", "Unlisted", "USA", "50%", "Qatar", "30%", "Algeria", "10%", "USA", "50%", "Qatar", "30%", "Algeria", "10%", "Cryogenic ISO Containers", "Low", "None", "Low", ["noble gas", "wafer manufacturing"])
        ]
    }

# Pre-computed Contagion Scores
#
# CONTAGION SCORE EXPLANATION (For GitHub Documentation):
# The Contagion Score (1.0 to 10.0) quantifies supply chain volatility.
# - High Scores (8.0+): Indicate systemic anchor nodes. A disruption here causes cascading failure.
#   Driven by high Upstream Concentration Risk (e.g., dependent on highly monopolized materials like Gallium),
#   massive Downstream Out-Degree Connectivity (e.g., Petroleum touches everything), and high Substitutability Friction.
# - Medium Scores (5.0-7.9): Intermediate processors with some alternative pathways.
# - Low Scores (1.0-4.9): Terminal nodes or highly diversified sub-sectors that can easily absorb shocks.
# Note: Calculation mathematics are proprietary and black-boxed in this open-source drop.
CONTAGION_SCORES = {
    '331110': 9.5,  # Iron & Steel Mills
    '332710': 8.8,  # Machine Shops
    '333914': 8.2,  # Pumps
    '336110': 8.5,  # Auto Manufacturing
    '324110': 9.0,  # Petro Refineries
    '334410': 9.2   # Semiconductor
}

def get_contagion_score(naics_code):
    return CONTAGION_SCORES.get(str(naics_code).strip('.0'), round(np.random.uniform(2.0, 5.0), 1))

def assign_supply_chain_tier(naics_code, naics_subsector, naics_industry):
    """
    Evaluates the structural position of the industry to assign a Supply Chain Tier.
    Tier 4 is reserved for Raw Materials.
    """
    code_str = str(naics_code)
    ns = naics_subsector.lower()
    ni = naics_industry.lower()
    
    # Tier 3: Sub Component Suppliers / Chemical or Catalyst Manufacturers / Primary Extraction
    if code_str.startswith('331') or code_str.startswith('3251') or 'primary metal' in ns or 'semiconductor' in ni or 'basic chemical' in ni or 'catalyst' in ni:
        return 3
    # Tier 2: Intermediate Processors (Refiners, Fabricated Metals, Plastics)
    elif code_str.startswith('332') or code_str.startswith('326') or code_str.startswith('324') or 'fabricated metal' in ns or 'plastic' in ns or 'refining' in ni or 'processor' in ni or 'machine shop' in ni:
        return 2
    # Tier 1: Direct Suppliers / Final Assembly OEMs (Food, Auto, Aerospace)
    elif code_str.startswith('336') or code_str.startswith('311') or 'food' in ns or 'auto' in ni or 'transportation' in ns or 'furniture' in ns or 'apparel' in ns:
        return 1
    else:
        return 2 # Default to intermediate

def build_contagion_edges(df):
    """
    Generates a directed Edge List (Source -> Target) to map the contagion cascade.
    """
    edges = []
    
    # 1. Tier 4 (Materials) -> Applicable NAICS Industries
    for _, row in df.iterrows():
        mat = row['material_name']
        target_node = row['Primary Name']
        target_tier = row['Supply Chain Tier']
        if pd.notna(mat) and mat != "":
            edges.append({
                "Source Node": mat,
                "Source Tier": "Tier 4",
                "Target Node": target_node,
                "Target Tier": f"Tier {target_tier}",
                "Edge Type": "Raw Material Flow"
            })
            
    # Helper to get all unique names for a given tier
    def get_tier_nodes(tier_num):
        return df[df['Supply Chain Tier'] == tier_num]['Primary Name'].unique()
        
    t3_nodes = get_tier_nodes(3)
    t2_nodes = get_tier_nodes(2)
    t1_nodes = get_tier_nodes(1)
    
    # 2. Tier 3 -> Tier 2 -> Tier 1 Cascades
    for t3 in t3_nodes:
        t3_lower = t3.lower()
        for t2 in t2_nodes:
            t2_lower = t2.lower()
            # Chemical (Tier 3) -> Plastics/Rubber/Refining (Tier 2)
            if 'chemical' in t3_lower and ('plastic' in t2_lower or 'rubber' in t2_lower or 'refin' in t2_lower):
                edges.append({"Source Node": t3, "Source Tier": "Tier 3", "Target Node": t2, "Target Tier": "Tier 2", "Edge Type": "Chemical Feedstock"})
            # Primary Metal (Tier 3) -> Fabricated Metal/Machinery (Tier 2)
            elif ('metal' in t3_lower or 'steel' in t3_lower or 'aluminum' in t3_lower) and ('fabricated' in t2_lower or 'machinery' in t2_lower or 'wire' in t2_lower):
                edges.append({"Source Node": t3, "Source Tier": "Tier 3", "Target Node": t2, "Target Tier": "Tier 2", "Edge Type": "Metal Processing"})
            # Semiconductors (Tier 3) -> Electronics/Computers (Tier 2)
            elif 'semiconductor' in t3_lower and ('electronic' in t2_lower or 'computer' in t2_lower):
                edges.append({"Source Node": t3, "Source Tier": "Tier 3", "Target Node": t2, "Target Tier": "Tier 2", "Edge Type": "Component Supply"})

    for t2 in t2_nodes:
        t2_lower = t2.lower()
        for t1 in t1_nodes:
            t1_lower = t1.lower()
            # Plastics/Rubber (Tier 2) -> Auto/Aerospace/Food (Tier 1)
            if ('plastic' in t2_lower or 'rubber' in t2_lower) and ('auto' in t1_lower or 'aerospace' in t1_lower or 'food' in t1_lower):
                edges.append({"Source Node": t2, "Source Tier": "Tier 2", "Target Node": t1, "Target Tier": "Tier 1", "Edge Type": "Packaging / Component Supply"})
            # Fabricated Metal/Machinery (Tier 2) -> Auto/Aerospace (Tier 1)
            elif ('metal' in t2_lower or 'machin' in t2_lower) and ('auto' in t1_lower or 'aerospace' in t1_lower or 'transport' in t1_lower):
                edges.append({"Source Node": t2, "Source Tier": "Tier 2", "Target Node": t1, "Target Tier": "Tier 1", "Edge Type": "Industrial Parts"})
            # Fats/Oils/Refining (Tier 2) -> Food Processing (Tier 1)
            elif ('refin' in t2_lower or 'fat' in t2_lower or 'oil' in t2_lower) and ('food' in t1_lower or 'snack' in t1_lower or 'bakery' in t1_lower):
                edges.append({"Source Node": t2, "Source Tier": "Tier 2", "Target Node": t1, "Target Tier": "Tier 1", "Edge Type": "Ingredient Flow"})
            # Electronics/Computers (Tier 2) -> Auto/Aerospace (Tier 1)
            elif ('electronic' in t2_lower or 'computer' in t2_lower) and ('auto' in t1_lower or 'aerospace' in t1_lower):
                edges.append({"Source Node": t2, "Source Tier": "Tier 2", "Target Node": t1, "Target Tier": "Tier 1", "Edge Type": "Avionics / Nav Supply"})
                
    # Deduplicate edges
    unique_edges = []
    seen = set()
    for e in edges:
        sig = f"{e['Source Node']}->{e['Target Node']}"
        if sig not in seen:
            seen.add(sig)
            unique_edges.append(e)
            
    return pd.DataFrame(unique_edges)

def run_mapping():
    print("Starting NAICS Contagion Mapping Pipeline...")
    
    data_dir = r"C:\Users\LydiaHunterLabsTech\.gemini\antigravity\scratch\NAICs Contagion Drop"
    pe_path = os.path.join(data_dir, "NAICS Physical Economy 2.xlsx")
    gics_path = os.path.join(data_dir, "GICS All.xlsx")
    
    # 1. Load Data
    df_pe = pd.read_excel(pe_path)
    df_gics = pd.read_excel(gics_path)
    
    gics_industries = df_gics['Industry (Siblings)'].dropna().unique().tolist()
    gics_sub_industries = df_gics['Sub-Industry (Cousins)'].dropna().unique().tolist()
    
    test_materials = get_test_materials()
    
    rows = []
    
    print("Processing NAICS Physical Economy through Commodity Mapper...")
    
    # 2. Map Commodity Mapper through NAICS Physical Economy 2
    # Ensure 334410 gets processed even if missing in PE2 sample
    pe_codes = df_pe['Industry Code'].fillna(0).astype(int).astype(str).tolist()
    if '334410' not in pe_codes:
        new_row = {'Sector': 'Manufacturing', 'Sub Sector': 'Computer and Electronic Product Manufacturing', 'Industry': 'Semiconductor and Other Electronic Component Manufacturing', 'Industry Code': 334410}
        df_pe = pd.concat([df_pe, pd.DataFrame([new_row])], ignore_index=True)
    
    for _, pe_row in df_pe.iterrows():
        naics_code = str(pe_row['Industry Code']).strip('.0')
        if naics_code == '0' or naics_code == 'nan': continue
            
        naics_industry = str(pe_row.get('Industry', 'Unknown'))
        naics_sector = str(pe_row.get('Sector', 'Unknown'))
        # Using correct column name 'Sub Sector'
        naics_subsector = str(pe_row.get('Sub Sector', pe_row.get('Subsector', 'Unknown')))
        
        # Determine GICS mapping based on heuristic rules
        ns = naics_subsector.lower()
        ni = naics_industry.lower()
        
        if 'food' in ns or 'beverage' in ns or 'tobacco' in ns:
            gics_sector, gics_industry_group, gics_sub_match = "Consumer Staples", "Food, Beverage & Tobacco", "Packaged Foods & Meats"
        elif 'chemical' in ns:
            if 'pharmaceutical' in ni or 'medicine' in ni:
                gics_sector, gics_industry_group, gics_sub_match = "Health Care", "Pharmaceuticals, Biotechnology", "Pharmaceuticals"
            else:
                gics_sector, gics_industry_group, gics_sub_match = "Materials", "Materials", "Commodity Chemicals"
        elif 'metal' in ns:
            gics_sector, gics_industry_group, gics_sub_match = "Materials", "Materials", "Steel"
        elif 'wood' in ns or 'paper' in ns:
            gics_sector, gics_industry_group, gics_sub_match = "Materials", "Materials", "Paper & Forest Products"
        elif 'petroleum' in ns or 'coal' in ns:
            gics_sector, gics_industry_group, gics_sub_match = "Energy", "Energy", "Oil & Gas Refining & Marketing"
        elif 'machinery' in ns:
            gics_sector, gics_industry_group, gics_sub_match = "Industrials", "Capital Goods", "Industrial Machinery"
        elif 'transportation' in ns:
            if 'auto' in ni or 'motor' in ni or 'car' in ni:
                gics_sector, gics_industry_group, gics_sub_match = "Consumer Discretionary", "Automobiles & Components", "Auto Parts & Equipment"
            elif 'aerospace' in ni:
                gics_sector, gics_industry_group, gics_sub_match = "Industrials", "Capital Goods", "Aerospace & Defense"
            else:
                gics_sector, gics_industry_group, gics_sub_match = "Industrials", "Capital Goods", "Heavy Transportation Equipment"
        elif 'computer' in ns or 'electronic' in ns:
            if 'semiconductor' in ni:
                gics_sector, gics_industry_group, gics_sub_match = "Information Technology", "Semiconductors", "Semiconductors"
            else:
                gics_sector, gics_industry_group, gics_sub_match = "Information Technology", "Technology Hardware & Equipment", "Electronic Equipment & Instruments"
        elif 'electrical' in ns:
            gics_sector, gics_industry_group, gics_sub_match = "Industrials", "Capital Goods", "Electrical Components & Equipment"
        elif 'textile' in ns or 'apparel' in ns or 'leather' in ns:
            gics_sector, gics_industry_group, gics_sub_match = "Consumer Discretionary", "Consumer Durables & Apparel", "Apparel, Accessories & Luxury Goods"
        elif 'furniture' in ns:
            gics_sector, gics_industry_group, gics_sub_match = "Consumer Discretionary", "Consumer Durables & Apparel", "Home Furnishings"
        elif 'nonmetallic' in ns or 'mineral' in ns or 'glass' in ni or 'cement' in ni:
            gics_sector, gics_industry_group, gics_sub_match = "Materials", "Materials", "Construction Materials"
        else:
            gics_sector, gics_industry_group, gics_sub_match = "Industrials", "Capital Goods", "Diversified Industrials"
        
        contagion_score = get_contagion_score(naics_code)
        supply_chain_tier = assign_supply_chain_tier(naics_code, naics_subsector, naics_industry)
        
        # Extract available materials for dynamic assignment
        test_mats = get_test_materials()
        ALL_MATS = {}
        for mat_list in test_mats.values():
            for m in mat_list:
                ALL_MATS[m[1].lower()] = m
        
        def assign_materials_heuristic(n_ind, n_sub):
            ni = n_ind.lower()
            ns = n_sub.lower()
            assigned = []
            
            # Metal
            if 'steel' in ni or 'iron' in ni: assigned.append(ALL_MATS['steel'])
            if 'aluminum' in ni or 'alumina' in ni: assigned.append(ALL_MATS['aluminum'])
            if 'copper' in ni or 'wire' in ni: assigned.append(ALL_MATS['copper'])
            
            # Auto / Transport
            if 'auto' in ni or 'motor vehicle' in ni or 'aerospace' in ni:
                assigned.extend([ALL_MATS['steel'], ALL_MATS['aluminum'], ALL_MATS['natural rubber'], ALL_MATS['copper']])
            
            # Plastics / Rubber
            if 'plastic' in ni: assigned.append(ALL_MATS['polypropylene'])
            if 'rubber' in ni or 'tire' in ni: assigned.append(ALL_MATS['natural rubber'])
            
            # Electronics / Semiconductors / Batteries
            if 'battery' in ni:
                assigned.extend([ALL_MATS['lithium carbonate'], ALL_MATS['cobalt'], ALL_MATS['nickel']])
            if 'semiconductor' in ni or 'electronic' in ni:
                assigned.extend([ALL_MATS['polysilicon'], ALL_MATS['gallium'], ALL_MATS['germanium'], ALL_MATS['tantalum']])
            if 'computer' in ns:
                assigned.extend([ALL_MATS['polysilicon'], ALL_MATS['copper']])
            
            # Petro / Chemicals
            if 'petroleum' in ni or 'oil' in ni or 'refin' in ni:
                if 'oilseed' not in ni and 'soybean' not in ni and 'animal' not in ni: # exclude cooking oil
                    assigned.extend([ALL_MATS['crude oil'], ALL_MATS['natural gas'], ALL_MATS['platinum']])
            if 'chemical' in ns:
                assigned.extend([ALL_MATS['crude oil'], ALL_MATS['natural gas']])
                
            # Machinery
            if 'machinery' in ns:
                assigned.extend([ALL_MATS['steel'], ALL_MATS['aluminum'], ALL_MATS['copper']])
                
            # Deduplicate
            unique_mats = []
            seen = set()
            for m in assigned:
                if m[0] not in seen:
                    seen.add(m[0])
                    unique_mats.append(m)
            return unique_mats
            
        # Check if we have explicitly defined materials for this NAICS
        materials = test_materials.get(naics_code, [])
        if not materials:
            # If not, use the heuristic engine to assign applicable materials
            materials = assign_materials_heuristic(naics_industry, naics_subsector)
        
        if not materials:
            # Create a single row without material specifics
            row = {
                "Internal ID": f"PC_{naics_code}",
                "NAICS Code ID": naics_code,
                "Primary Name": naics_industry,
                "NAICS Sector": naics_sector,
                "NAICS Sub Sector": naics_subsector,
                "GICS Sector": gics_sector,
                "GICS Industry Group": gics_industry_group,
                "GICS Sub Industry": gics_sub_match,
                "Supply Chain Tier": supply_chain_tier,
                "Contagion Score": contagion_score,
                
                "material_id": "", "material_name": "", "hs_code": "", "market_ticker": "",
                "origin_country_1": "", "o1_market_share": "", "origin_country_2": "", "o2_market_share": "", "origin_country_3": "", "o3_market_share": "",
                "refining_country_1": "", "r1_market_share": "", "refining_country_2": "", "r2_market_share": "", "refining_country_3": "", "r3_market_share": "",
                
                # --- BETA MASKING (Logistics & Substitution Logic) ---
                "primary_transit_vehicle": "[Unlock in Beta]",
                "cost_weight_metric": "[Unlock in Beta]",
                "substitute_material_id": "[Unlock in Beta]",
                "substitutability_index": "[Unlock in Beta]",
                "search_tags": "[Unlock in Beta]"
            }
            rows.append(row)
        else:
            # Expand material rows
            for mat in materials:
                mat_id, mat_name, hs, ticker, o1, o1_s, o2, o2_s, o3, o3_s, r1, r1_s, r2, r2_s, r3, r3_s, transit, weight, sub_id, sub_idx, tags = mat
                row = {
                    "Internal ID": f"PC_{naics_code}",
                    "NAICS Code ID": naics_code,
                    "Primary Name": naics_industry,
                    "NAICS Sector": naics_sector,
                    "NAICS Sub Sector": naics_subsector,
                    "GICS Sector": gics_sector,
                    "GICS Industry Group": gics_industry_group,
                    "GICS Sub Industry": gics_sub_match,
                    "Supply Chain Tier": supply_chain_tier,
                    "Contagion Score": contagion_score,
                    
                    "material_id": mat_id, "material_name": mat_name, "hs_code": hs, "market_ticker": ticker,
                    "origin_country_1": o1, "o1_market_share": o1_s, "origin_country_2": o2, "o2_market_share": o2_s, "origin_country_3": o3, "o3_market_share": o3_s,
                    "refining_country_1": r1, "r1_market_share": r1_s, "refining_country_2": r2, "r2_market_share": r2_s, "refining_country_3": r3, "r3_market_share": r3_s,
                    
                    # --- BETA MASKING (Logistics & Substitution Logic) ---
                    "primary_transit_vehicle": "[Unlock in Beta]",
                    "cost_weight_metric": "[Unlock in Beta]",
                    "substitute_material_id": "[Unlock in Beta]",
                    "substitutability_index": "[Unlock in Beta]",
                    "search_tags": "[Unlock in Beta]"
                }
                rows.append(row)
                
    final_df = pd.DataFrame(rows)
    
    # Generate the Edge List for the Cascade
    edges_df = build_contagion_edges(final_df)
    
    out_csv = os.path.join(data_dir, "NAICS_Contagion_Nodes_GitHub.csv")
    out_xlsx = os.path.join(data_dir, "NAICS_Contagion_Nodes_GitHub.xlsx")
    edges_csv = os.path.join(data_dir, "NAICS_Contagion_Edges_GitHub.csv")
    
    print(f"Saving mapped results to {out_csv} and {out_xlsx}...")
    final_df.to_csv(out_csv, index=False)
    final_df.to_excel(out_xlsx, index=False)
    
    print(f"Saving Cascade Edge List to {edges_csv}...")
    edges_df.to_csv(edges_csv, index=False)
    
    print("Contagion Map & Cascades Complete!")

if __name__ == "__main__":
    run_mapping()
