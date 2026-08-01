#!/usr/bin/env python3
"""
Sync Nanobot Medical Wiki Markdown files into Graphify Knowledge Graph (graph.json).
Parses YAML frontmatter, wikilinks [[...]], and markdown links to construct nodes and edges.
"""

import json
import os
import re
from pathlib import Path

WORKSPACE = Path("/home/tan/.nanobot/workspace")
WIKI_DIR = WORKSPACE / "wiki"
GRAPH_FILE = WORKSPACE / "graphify-out" / "graph.json"

def parse_yaml_frontmatter(content):
    meta = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_text = parts[1]
            for line in yaml_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    meta[key] = val
    return meta

def sync_wiki():
    if not WIKI_DIR.exists():
        print(f"❌ Wiki directory not found: {WIKI_DIR}")
        return

    # Load existing graph.json or create new
    if GRAPH_FILE.exists():
        try:
            with open(GRAPH_FILE, "r", encoding="utf-8") as f:
                graph_data = json.load(f)
        except Exception:
            graph_data = {"nodes": [], "edges": [], "communities": []}
    else:
        graph_data = {"nodes": [], "edges": [], "communities": []}

    if "nodes" not in graph_data or not isinstance(graph_data["nodes"], list):
        graph_data["nodes"] = []
    if "edges" not in graph_data or not isinstance(graph_data["edges"], list):
        graph_data["edges"] = []
    if "communities" not in graph_data or not isinstance(graph_data["communities"], list):
        graph_data["communities"] = []

    existing_nodes = {n.get("id") or n.get("label"): n for n in graph_data["nodes"]}
    existing_edge_keys = set()
    for e in graph_data["edges"]:
        src = e.get("source")
        tgt = e.get("target")
        if src and tgt:
            existing_edge_keys.add(f"{src}->{tgt}")

    added_nodes = 0
    added_edges = 0

    # Scan all markdown files in wiki/
    md_files = list(WIKI_DIR.rglob("*.md"))
    print(f"🔍 Processing {len(md_files)} Wiki Markdown files...")

    for md_path in md_files:
        rel_path = str(md_path.relative_to(WORKSPACE))
        file_name = md_path.stem
        node_id = rel_path

        try:
            content = md_path.read_text(encoding="utf-8")
        except Exception:
            continue

        meta = parse_yaml_frontmatter(content)
        title = meta.get("title", file_name)
        file_type = meta.get("type", "wiki_doc")

        # Create/update Node
        node_info = {
            "id": node_id,
            "label": title,
            "file": rel_path,
            "type": file_type,
            "category": "wiki",
            "source": "wiki_sync"
        }

        if node_id not in existing_nodes:
            graph_data["nodes"].append(node_info)
            existing_nodes[node_id] = node_info
            added_nodes += 1

        # Extract [[wikilinks]]
        wikilinks = re.findall(r"\[\[(.*?)\]\]", content)
        for link in wikilinks:
            link_clean = link.strip()
            # Resolve target path
            if link_clean.startswith("entities/") or link_clean.startswith("concepts/") or link_clean.startswith("synthesis/"):
                target_id = f"wiki/{link_clean}"
            elif "/" not in link_clean:
                target_id = f"wiki/entities/{link_clean}"
            else:
                target_id = f"wiki/{link_clean}"

            if not target_id.endswith(".md"):
                target_id += ".md"

            # Create target node if missing
            if target_id not in existing_nodes:
                target_node = {
                    "id": target_id,
                    "label": link_clean,
                    "file": target_id,
                    "type": "entity",
                    "category": "wiki",
                    "source": "wiki_link"
                }
                graph_data["nodes"].append(target_node)
                existing_nodes[target_id] = target_node
                added_nodes += 1

            # Add Edge
            edge_key = f"{node_id}->{target_id}"
            if edge_key not in existing_edge_keys:
                graph_data["edges"].append({
                    "source": node_id,
                    "target": target_id,
                    "relation": "references",
                    "source_type": "wiki"
                })
                existing_edge_keys.add(edge_key)
                added_edges += 1

    # Save updated graph.json
    GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Wiki Sync Completed!")
    print(f"   Nodes mới thêm: {added_nodes}")
    print(f"   Edges mới kết nối: {added_edges}")
    print(f"   Tổng số Nodes trong đồ thị: {len(graph_data['nodes'])}")
    print(f"   Tổng số Edges trong đồ thị: {len(graph_data['edges'])}")

if __name__ == "__main__":
    sync_wiki()
