---
name: graphrag-knowledge
description: >
  Tích hợp Microsoft GraphRAG vào nanobot để truy vấn đồ thị tri thức MEIMS/QLTB.
  Index wiki entities, query bằng Global/Local/DRIFT search.
---

# GraphRAG Knowledge Integration

Tích hợp Microsoft GraphRAG cho nanobot để truy vấn thông minh wiki MEIMS/QLTB.

## Cài đặt

```bash
pip install graphrag
```

## Cấu trúc thư mục

```
/home/tan/.nanobot/workspace/
├── wiki/
│   ├── raw/                    # Nguồn gốc (Excel, PDF, OCR output)
│   ├── entities/               # Wiki entities (đã có)
│   ├── concepts/
│   ├── synthesis/
│   ├── graph/                  # GraphRAG output (tự động tạo)
│   │   ├── input/              # Text units cho indexer
│   │   ├── output/             # Parquet files (entities, relationships, communities)
│   │   ├── prompts/            # Custom prompts
│   │   └── config.yaml         # GraphRAG config
│   ├── index.md
│   └── log.md
└── skills/
    └── graphrag-knowledge/
        ├── SKILL.md
        ├── scripts/
        │   ├── init_graphrag.py
        │   ├── build_index.py
        │   ├── query_graphrag.py
        │   ├── sync_wiki.py
        │   └── schedule_index.py
        └── config/
            └── graphrag.yaml
```

## Config (config/graphrag.yaml)

```yaml
# GraphRAG configuration for MEIMS/QLTB
encoding_model: cl100k_base

# Input
input:
  type: file
  file_type: text
  base_dir: "wiki/raw/"
  file_encoding: utf-8
  file_pattern: "*.md"

# Output
output:
  type: file
  base_dir: "wiki/graph/output/"

# Storage
storage:
  type: file
  base_dir: "wiki/graph/output/"

# Reporting
reporting:
  type: file
  base_dir: "wiki/graph/output/reports/"

# Cache
cache:
  type: file
  base_dir: "wiki/graph/cache/"

# LLM
llm:
  type: openai_chat
  model: orfree
  api_base: "http://127.0.0.1:20128/v1"
  api_key: "${NANOBOT_ORFREE_KEY}"
  max_tokens: 4000
  temperature: 0
  top_p: 1
  n: 1
  request_timeout: 180.0

# Embeddings
embeddings:
  type: openai_embedding
  model: text-embedding-3-small
  api_base: "http://127.0.0.1:20128/v1"
  api_key: "${NANOBOT_ORFREE_KEY}"
  max_tokens: 8192

# Chunking
chunks:
  size: 1200
  overlap: 100
  group_by_columns: ["id"]

# Entity extraction
entity_extraction:
  prompt: "prompts/entity_extraction.txt"
  max_gleanings: 1
  strategy:
    type: graph_intelligence
    llm: llm
    parallelization:
      stagger: 0.5
      num_threads: 4

# Claim extraction
claim_extraction:
  enabled: true
  prompt: "prompts/claim_extraction.txt"
  max_gleanings: 1
  strategy:
    type: graph_intelligence
    llm: llm

# Community detection
community_detection:
  strategy:
    type: leiden
    max_level: 4
    seed: 0xDEADBEEF

# Community reports
community_reports:
  prompt: "prompts/community_report.txt"
  max_length: 2000
  max_input_length: 8000
  strategy:
    type: graph_intelligence
    llm: llm

# Local search
local_search:
  text_unit_prop: 0.5
  community_prop: 0.1
  conversation_history_max_turns: 5
  top_k_mapped_entities: 10
  top_k_relationships: 10
  max_tokens: 12000
  llm: llm

# Global search
global_search:
  llm: llm
  max_tokens: 12000
  data_max_tokens: 12000
  map_max_tokens: 1000
  reduce_max_tokens: 2000
  concurrency: 4

# DRIFT search
drift_search:
  llm: llm
  max_tokens: 12000
  data_max_tokens: 12000
  primer_max_tokens: 2000
  max_followups: 3
  concurrency: 4
```

## Custom Prompts (prompts/)

### entity_extraction.txt
```
Bạn là chuyên gia trích xuất thông tin thiết bị y tế cho hệ thống QLTB (Quản lý thiết bị y tế) tại bệnh viện Tâm Anh.

Từ văn bản đầu vào, hãy trích xuất:
1. **Entities**: Thiết bị y tế, khoa/phòng, nhà sản xuất, tiêu chuẩn, biên bản, người phụ trách
2. **Relationships**: thuộc về, kiểm định, bảo trì, vị trí, responsible, manufactured_by
3. **Claims**: Hạn kiểm định, trạng thái, thông số kỹ thuật, cảnh báo

Format output: JSON với fields: entity_name, entity_type, description, source_text
```

### community_report.txt
```
Tóm tắt cộng đồng thiết bị y tế cho QLTB.

Bao gồm:
- Các thiết bị chính trong cộng đồng
- Khoa/phòng liên quan
- Trạng thái kiểm định/bảo trì chung
- Rủi ro/cảnh báo (hạn HC sắp hết, thiết bị hỏng nhiều)
- Khuyến nghị hành động
```

## Scripts

### init_graphrag.py
```python
#!/usr/bin/env python3
"""Khởi tạo GraphRAG cho wiki MEIMS/QLTB."""
import subprocess
import os

WIKI_ROOT = "/home/tan/.nanobot/workspace/wiki"

def main():
    # Init GraphRAG
    subprocess.run([
        "graphrag", "init",
        "--root", WIKI_ROOT,
        "--force"
    ], check=True)
    
    # Copy custom config
    subprocess.run([
        "cp", "skills/graphrag-knowledge/config/graphrag.yaml",
        f"{WIKI_ROOT}/settings.yaml"
    ], check=True)
    
    # Copy custom prompts
    subprocess.run([
        "cp", "-r", "skills/graphrag-knowledge/prompts/",
        f"{WIKI_ROOT}/prompts/"
    ], check=True)
    
    print("GraphRAG initialized. Run build_index.py to index wiki.")

if __name__ == "__main__":
    main()
```

### build_index.py
```python
#!/usr/bin/env python3
"""Build GraphRAG index từ wiki entities."""
import subprocess
import os

WIKI_ROOT = "/home/tan/.nanobot/workspace/wiki"

def main():
    # Sync wiki entities to input format
    subprocess.run(["python3", "sync_wiki.py"], check=True)
    
    # Build index
    subprocess.run([
        "graphrag", "build",
        "--root", WIKI_ROOT,
        "--config", "settings.yaml"
    ], check=True)
    
    print("GraphRAG index built successfully.")

if __name__ == "__main__":
    main()
```

### sync_wiki.py
```python
#!/usr/bin/env python3
"""Sync wiki entities to GraphRAG input format."""
import os
import json
from pathlib import Path

WIKI_ENTITIES = "/home/tan/.nanobot/workspace/wiki/entities"
GRAPH_INPUT = "/home/tan/.nanobot/workspace/wiki/graph/input"

def extract_text_from_md(filepath):
    """Extract text content from markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    return content.strip()

def main():
    os.makedirs(GRAPH_INPUT, exist_ok=True)
    
    entities = list(Path(WIKI_ENTITIES).glob("*.md"))
    print(f"Found {len(entities)} entity files")
    
    for i, entity_file in enumerate(entities):
        text = extract_text_from_md(entity_file)
        if not text:
            continue
        
        # Create text unit
        unit = {
            "id": f"entity_{i}",
            "text": text,
            "source": str(entity_file.relative_to(WIKI_ENTITIES)),
            "metadata": {
                "type": "wiki_entity",
                "entity_name": entity_file.stem
            }
        }
        
        output_file = Path(GRAPH_INPUT) / f"{entity_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unit, f, ensure_ascii=False, indent=2)
    
    print(f"Synced {len(entities)} entities to GraphRAG input")

if __name__ == "__main__":
    main()
```

### query_graphrag.py
```python
#!/usr/bin/env python3
"""Query GraphRAG từ nanobot."""
import subprocess
import json
import sys

WIKI_ROOT = "/home/tan/.nanobot/workspace/wiki"

def query_graphrag(query: str, mode: str = "local") -> dict:
    """Query GraphRAG và trả về kết quả."""
    result = subprocess.run([
        "graphrag", "query",
        "--root", WIKI_ROOT,
        "--method", mode,
        "--query", query
    ], capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        return {"error": result.stderr}
    
    return {"response": result.stdout, "mode": mode}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 query_graphrag.py '<query>' [local|global|drift|basic]")
        sys.exit(1)
    
    query = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "local"
    
    result = query_graphrag(query, mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

### schedule_index.py
```python
#!/usr/bin/env python3
"""Cron job: Re-index GraphRAG hàng tuần."""
import subprocess
import sys

def main():
    print("Starting weekly GraphRAG re-index...")
    try:
        subprocess.run([
            "python3", "build_index.py"
        ], check=True, timeout=3600)
        print("Re-index completed successfully")
    except subprocess.TimeoutExpired:
        print("Re-index timed out")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Re-index failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Usage

```bash
# 1. Khởi tạo (chạy 1 lần)
python3 ~/.nanobot/workspace/skills/graphrag-knowledge/scripts/init_graphrag.py

# 2. Build index (chạy sau khi có entity mới)
python3 ~/.nanobot/workspace/skills/graphrag-knowledge/scripts/build_index.py

# 3. Query từ nanobot
python3 ~/.nanobot/workspace/skills/graphrag-knowledge/scripts/query_graphrag.py \
  "Tất cả máy TERUMO có hạn kiểm định < 30 ngày" local

# 4. Các mode query
# local   - Tìm kiếm entity cụ thể (mặc định)
# global  - Câu hỏi tổng quan về toàn bộ corpus
# drift   - Entity cụ thể + community context
# basic   - Vector search truyền thống
```

## Integration với nanobot

### Thêm vào 9router (MCP server)
```python
# Trong 9router config
"graphrag": {
  "command": "python3",
  "args": ["/home/tan/.nanobot/workspace/skills/graphrag-knowledge/scripts/query_graphrag.py"],
  "env": {
    "NANOBOT_ORFREE_KEY": "${NANOBOT_ORFREE_KEY}"
  }
}
```

### Gọi từ knowledge-curator
```python
# Trong knowledge-curator skill
def query_knowledge_graph(query: str) -> str:
    result = subprocess.run([
        "python3", 
        "/home/tan/.nanobot/workspace/skills/graphrag-knowledge/scripts/query_graphrag.py",
        query, "local"
    ], capture_output=True, text=True)
    return result.stdout
```

## Cron Job

```bash
# Thêm vào crontab (chạy 02:00 thứ 2 hàng tuần)
0 2 * * 1 /home/tan/.nanobot/workspace/skills/graphrag-knowledge/scripts/schedule_index.py
```

## Agent Rules

- Chỉ re-index khi có entity mới hoặc cập nhật lớn (kiểm tra `wiki/log.md`)
- Luôn dùng mode `local` cho truy vấn entity cụ thể
- Dùng mode `global` cho báo cáo tổng quan
- Cache kết quả query thường dùng
- Không index file `wiki/raw/` lớn (PDF) — chỉ index entities đã curated
- Prompt tuning: cập nhật `prompts/` khi kết quả chưa chính xác