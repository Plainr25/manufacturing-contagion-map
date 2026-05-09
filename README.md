# 🌐 NAICS Contagion Map: The Physical Economy Visualized

<div align="center">

### [ 📊 Launch the Interactive Dashboard ](https://huggingface.co/spaces/Plainr-26/README)

**[ 🔗 Join the June 2026 Beta Drop ](https://a7af2a54.sibforms.com/serve/MUIFAK4KiE6r-UBeNPKiGd_hFht_dPE_p8oCs2NOx53N8abu_SQe9HTVgRxIlg4HlA9cOsVmYs2pkeAZHGZ0XlDh2RBLa_bZZLLiaXPKpUTjgr72heyx-lYwgPb0B8dnkWsj7lw-M1jEOnzP7Oc8o12c0SG3UYsmQZRaWacaAWgweWru9S9fWYne4o43aByc7BqGSjRvnZcHXYcQ)**

</div>

---

Welcome to the **NAICS Contagion Intelligence Map** — an open-source pipeline mapping the vulnerability cascades of the physical economy. 

This repository bridges institutional supply chain taxonomies (NAICS) with financial market frameworks (GICS) to visualize how disruptions in upstream raw materials (Tier 4) systematically ripple down through the chain to Tier 3 nodes then to Tier 2 and finally Tier 1 

<img width="2475" height="1468" alt="image" src="https://github.com/user-attachments/assets/0daad354-8b64-4087-a03d-467fd0a34d01" />


## 📦 What's Included in the Drop?

1. **`NAICS_Contagion_Map.py`**
   The core intelligence engine. It utilizes a deterministic heuristic algorithm to classify manufacturing nodes into Supply Chain Tiers (Tier 1 to Tier 4) and generate topological edge networks.

2. **`NAICS_Contagion_Nodes_GitHub.xlsx` / `.csv`**
   The flat intelligence map. Contains 346 mapped NAICS industries, their corresponding GICS cousins, their structural Tier, and their **Contagion Score (1.0 - 10.0)**.
   *Note: Sensitive logistics data and substitutability friction metrics are masked as `[Unlock in Beta]` to protect trade-secret competitive intelligence.*

3. **`NAICS_Contagion_Edges_GitHub.csv`**
   The relational spiderweb. A generated list of 1,100+ topological edges showing the exact contagion cascade from Tier 4 (Commodity) -> Tier 3 (Primary Extractor) -> Tier 2 (Processor) -> Tier 1 (Final Assembler).

4. **`build_visualizer.py` & `NAICS_Contagion_Visualizer.html`**
   A stunning, interactive Web application generated from the data. You can open the `.html` file directly in any browser (no server required) to explore the system cascades interactively via an embedded physics-driven network engine.

## 🧠 The Intelligence Framework

### The Supply Chain Tiers
We categorize the physical economy into four distinct levels of depth:
*   **Tier 4 (Raw Materials):** Foundational commodities (e.g., Lithium, Crude Oil, Platinum).
*   **Tier 3 (Primary Converters):** Heavy extractors and baseline chemical/metal converters (e.g., Basic Chemical Mfg, Primary Metal Mfg).
*   **Tier 2 (Intermediate Processors):** Mid-stream molders and fabricators (e.g., Fabricated Metals, Plastics, Refiners).
*   **Tier 1 (Direct Suppliers / OEMs):** Final assembly and direct-to-consumer manufacturing (e.g., Auto Manufacturing, Food Processing, Aerospace).

### The Contagion Score (1.0 - 10.0)
The Contagion Score quantifies systemic volatility. 
- **High Scores (8.0+):** Indicate a systemic "anchor node". A bottleneck here causes catastrophic downstream starvation. Driven by high Upstream Concentration Risk and massive Downstream Connectivity.
- **Medium Scores (5.0-7.9):** Intermediate processors with some alternative pathways.
- **Low Scores (1.0-4.9):** Terminal nodes that can absorb localized shocks.

## 🚀 How to Use the Data
Import the `Edges` and `Nodes` CSVs directly into network visualization tools like Gephi, Neo4j, or Python's NetworkX to build an interactive, force-directed graph of macroeconomic risk.

---
If you find this industrial mapping useful for your own research, please leave a ⭐ on GitHub. It helps us keep the project open-source

---

**Contact for Enterprise Inquiry:**
Email Mark: `mark(at)plainr(dot)io`
