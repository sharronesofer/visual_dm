#!/usr/bin/env python3
"""Script to check C# XML documentation coverage."""

import re
from pathlib import Path
from collections import defaultdict

CSHARP_ROOT = Path(__file__).parent.parent / "Visual_DM/Visual_DM/Assets/Scripts/"
DOCS_OUT = Path(__file__).parent.parent / "docs/csharp_doc_coverage.md"

CATEGORY_DIRS = {
    "UI": "UI",
    "Quest": "Quest",
}

def get_category(path):
    for cat, subdir in CATEGORY_DIRS.items():
        if subdir in str(path.parts):
            return cat
    return "Other"

PUBLIC_MEMBER_RE = re.compile(r'\bpublic\s+(class|struct|interface|enum|void|[A-Za-z0-9_<>]+)\s+([A-Za-z0-9_]+)')
XML_DOC_RE = re.compile(r'^\s*///')

def scan_file(path):
    results = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if PUBLIC_MEMBER_RE.search(lines[i]):
            # Check for XML doc in previous 3 lines
            has_doc = False
            for j in range(max(0, i-3), i):
                if XML_DOC_RE.match(lines[j]):
                    has_doc = True
                    break
            match = PUBLIC_MEMBER_RE.search(lines[i])
            member_type = match.group(1)
            member_name = match.group(2)
            results.append({
                "type": member_type,
                "name": member_name,
                "line": i+1,
                "has_doc": has_doc,
                "signature": lines[i].strip(),
            })
        i += 1
    return results

def main():
    coverage = defaultdict(lambda: {"total": 0, "documented": 0, "undocumented": 0, "members": []})
    for cs_file in CSHARP_ROOT.rglob("*.cs"):
        cat = get_category(cs_file)
        members = scan_file(cs_file)
        for m in members:
            coverage[cat]["total"] += 1
            if m["has_doc"]:
                coverage[cat]["documented"] += 1
            else:
                coverage[cat]["undocumented"] += 1
            m["file"] = str(cs_file.relative_to(CSHARP_ROOT))
            coverage[cat]["members"].append(m)
    with open(DOCS_OUT, "w", encoding="utf-8") as f:
        f.write("# C# XML Documentation Coverage Report\n\n")
        for cat, data in coverage.items():
            percent = 100 * data["documented"] / data["total"] if data["total"] else 0
            f.write(f"## {cat}\n")
            f.write(f"- Total public members: {data['total']}\n")
            f.write(f"- Documented: {data['documented']} ({percent:.1f}%)\n")
            f.write(f"- Undocumented: {data['undocumented']}\n\n")
            f.write("### Undocumented Members\n")
            for m in data["members"]:
                if not m["has_doc"]:
                    f.write(f"- `{m['file']}` line {m['line']}: `{m['signature']}`\n")
            f.write("\n---\n\n")
    print(f"Coverage report written to {DOCS_OUT}")

if __name__ == "__main__":
    main() 