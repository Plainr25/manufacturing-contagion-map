import pandas as pd
import json
import os

def generate_html():
    print("Loading Contagion Data...")
    
    # Load data from the current directory
    df_nodes = pd.read_csv("NAICS_Contagion_Nodes_GitHub.csv")
    df_edges = pd.read_csv("NAICS_Contagion_Edges_GitHub.csv")
    
    # Build Vis.js Nodes
    nodes = []
    seen_nodes = set()
    
    # Map colors to Tiers
    color_map = {
        'Tier 4': '#ff9f43', # Orange for Raw Materials
        'Tier 3': '#ee5253', # Red for Primary
        'Tier 2': '#9b59b6', # Purple for Intermediate
        'Tier 1': '#3498db'  # Blue for Final
    }
    
    # Process edges to get all nodes
    for _, e in df_edges.iterrows():
        src = e['Source Node']
        src_tier = e['Source Tier']
        tgt = e['Target Node']
        tgt_tier = e['Target Tier']
        
        if src not in seen_nodes:
            seen_nodes.add(src)
            nodes.append({
                "id": src,
                "label": src,
                "group": src_tier,
                "color": color_map.get(src_tier, '#bdc3c7'),
                "value": 20 if src_tier == 'Tier 4' else 10,
                "title": f"<b>{src}</b><br>{src_tier}"
            })
            
        if tgt not in seen_nodes:
            seen_nodes.add(tgt)
            # Find contagion score for target
            node_data = df_nodes[df_nodes['Primary Name'] == tgt]
            score = 5.0
            if not node_data.empty:
                score = float(node_data.iloc[0]['Contagion Score'])
                
            nodes.append({
                "id": tgt,
                "label": tgt,
                "group": tgt_tier,
                "color": color_map.get(tgt_tier, '#bdc3c7'),
                "value": score * 3, # Scale for visualization
                "title": f"<b>{tgt}</b><br>{tgt_tier}<br>Contagion Score: {score}"
            })
            
    # Build Vis.js Edges
    edges = []
    for _, e in df_edges.iterrows():
        edges.append({
            "from": e['Source Node'],
            "to": e['Target Node'],
            "title": e['Edge Type'],
            "arrows": "to",
            "color": {"color": "rgba(255,255,255,0.2)", "highlight": "rgba(255,255,255,0.8)"}
        })
        
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    
    # --- STUNNING HTML TEMPLATE (Dark Mode, Glassmorphism) ---
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NAICS Contagion Intelligence Map</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            display: flex;
            height: 100vh;
        }}
        
        #mynetwork {{
            flex-grow: 1;
            height: 100%;
            outline: none;
        }}
        
        /* Glassmorphism Sidebar */
        .sidebar {{
            width: 380px;
            height: 100%;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            padding: 40px 30px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            z-index: 10;
            box-shadow: -10px 0 30px rgba(0,0,0,0.5);
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: 800;
            margin: 0 0 10px 0;
            background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }}
        
        .header p {{
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        
        .legend {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 30px;
        }}
        
        .legend-title {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            font-size: 14px;
        }}
        
        .color-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 12px;
            box-shadow: 0 0 10px currentColor;
        }}
        
        .node-info {{
            margin-top: auto;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.05);
            display: none;
        }}
        
        .node-info h3 {{ margin: 0 0 10px 0; font-size: 16px; color: #fff; }}
        .node-info p {{ margin: 5px 0; font-size: 13px; color: #cbd5e1; }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            background: rgba(255,255,255,0.1);
            margin-top: 10px;
        }}
        
        /* Floating branding */
        .brand {{
            position: absolute;
            bottom: 30px;
            left: 30px;
            font-size: 12px;
            color: rgba(255,255,255,0.3);
            pointer-events: none;
            letter-spacing: 2px;
            font-weight: 600;
        }}
    </style>
</head>
<body>

    <div id="mynetwork"></div>
    <div class="brand">NAICS CONTAGION INTELLIGENCE</div>
    
    <div class="sidebar">
        <div class="header">
            <h1>Contagion Cascade</h1>
            <p>Interactive mapping of systemic vulnerability across the NAICS physical economy. Nodes are sized by Contagion Score.</p>
        </div>
        
        <div class="legend">
            <div class="legend-title">Supply Chain Hierarchy</div>
            <div class="legend-item"><div class="color-dot" style="color: #ff9f43; background: #ff9f43;"></div> Tier 4: Raw Commodity</div>
            <div class="legend-item"><div class="color-dot" style="color: #ee5253; background: #ee5253;"></div> Tier 3: Primary Extractor</div>
            <div class="legend-item"><div class="color-dot" style="color: #9b59b6; background: #9b59b6;"></div> Tier 2: Intermediate Processor</div>
            <div class="legend-item"><div class="color-dot" style="color: #3498db; background: #3498db;"></div> Tier 1: Final Assembly</div>
        </div>
        
        <div class="node-info" id="nodeInfo">
            <h3 id="ni-title">Node Name</h3>
            <p id="ni-tier">Tier: --</p>
            <p id="ni-score">Contagion Score: --</p>
            <div class="badge" id="ni-badge">Systemic Node</div>
        </div>
    </div>

    <script type="text/javascript">
        // Inject Data
        var nodes = new vis.DataSet({nodes_json});
        var edges = new vis.DataSet({edges_json});

        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        
        var options = {{
            nodes: {{
                shape: 'dot',
                font: {{ color: '#ffffff', size: 12, face: 'Inter', strokeWidth: 2, strokeColor: '#0f172a' }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                smooth: {{ type: 'continuous' }}
            }},
            physics: {{
                forceAtlas2Based: {{
                    gravitationalConstant: -80,
                    centralGravity: 0.005,
                    springLength: 200,
                    springConstant: 0.04,
                    damping: 0.65
                }},
                maxVelocity: 8,
                solver: 'forceAtlas2Based',
                timestep: 0.15,
                stabilization: {{ iterations: 150 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};

        var network = new vis.Network(container, data, options);
        
        // Interaction Events for the sidebar
        network.on("selectNode", function (params) {{
            if (params.nodes.length == 1) {{
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                
                document.getElementById('nodeInfo').style.display = 'block';
                document.getElementById('ni-title').innerText = node.label;
                document.getElementById('ni-tier').innerText = node.group;
                
                // Extract score from title or set to NA
                var score = "N/A";
                if(node.title.includes("Contagion Score")) {{
                    score = node.title.split("Contagion Score: ")[1];
                    document.getElementById('ni-badge').style.display = parseFloat(score) > 8.0 ? 'inline-block' : 'none';
                    if(parseFloat(score) > 8.0) document.getElementById('ni-badge').innerText = 'Critical Anchor Node';
                }} else {{
                    document.getElementById('ni-badge').style.display = 'none';
                }}
                document.getElementById('ni-score').innerText = "Contagion Score: " + score;
            }}
        }});
        
        network.on("deselectNode", function (params) {{
            document.getElementById('nodeInfo').style.display = 'none';
        }});
    </script>
</body>
</html>
"""
    
    out_path = "NAICS_Contagion_Visualizer.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Visualization generated successfully at: {out_path}")

if __name__ == "__main__":
    generate_html()
