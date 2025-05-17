#!/usr/bin/env python3
"""Script to generate API documentation."""

import sys
from pathlib import Path
import logging
import re
import xml.etree.ElementTree as ET

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.api.docs.openapi import OpenAPIGenerator
from app.core.api.version_manager import VersionManager
from app.core.api.fastapi.app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSHARP_ROOT = Path(project_root, "Visual_DM/Visual_DM/Assets/Scripts/")
DOCS_OUT = Path(project_root, "docs/csharp_api.md")

CSHARP_FILE_EXT = ".cs"

# Regex to match XML doc comments and the next public member
def extract_xml_docs_from_file(filepath):
    docs = []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('///'):
            xml_lines = []
            while i < len(lines) and lines[i].strip().startswith('///'):
                xml_lines.append(lines[i].strip()[3:].strip())
                i += 1
            # Find the next non-empty, non-comment line (should be the member signature)
            while i < len(lines) and (lines[i].strip() == '' or lines[i].strip().startswith('//')):
                i += 1
            member_signature = lines[i].strip() if i < len(lines) else ''
            xml = '<root>' + '\n'.join(xml_lines) + '</root>'
            docs.append((xml, member_signature))
        else:
            i += 1
    return docs

def parse_xml_doc(xml, member_signature):
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return None
    doc = {"signature": member_signature}
    for tag in ["summary", "remarks", "example", "returns"]:
        elem = root.find(tag)
        if elem is not None:
            doc[tag] = elem.text.strip() if elem.text else ''
    doc["params"] = []
    for param in root.findall("param"):
        doc["params"].append({"name": param.attrib.get("name", ""), "desc": param.text.strip() if param.text else ''})
    return doc

def extract_all_csharp_docs():
    all_docs = []
    for cs_file in CSHARP_ROOT.rglob(f'*{CSHARP_FILE_EXT}'):
        docs = extract_xml_docs_from_file(cs_file)
        for xml, sig in docs:
            parsed = parse_xml_doc(xml, sig)
            if parsed:
                parsed["file"] = str(cs_file.relative_to(project_root))
                all_docs.append(parsed)
    return all_docs

def write_markdown(docs):
    with open(DOCS_OUT, "w", encoding="utf-8") as f:
        f.write("# C# API Documentation\n\n")
        for doc in docs:
            f.write(f"## `{doc['signature']}`\n\n")
            f.write(f"**File:** `{doc['file']}`\n\n")
            if 'summary' in doc:
                f.write(f"**Summary:** {doc['summary']}\n\n")
            if doc.get('params'):
                f.write("**Parameters:**\n")
                for p in doc['params']:
                    f.write(f"- `{p['name']}`: {p['desc']}\n")
                f.write("\n")
            if 'returns' in doc:
                f.write(f"**Returns:** {doc['returns']}\n\n")
            if 'remarks' in doc:
                f.write(f"**Remarks:** {doc['remarks']}\n\n")
            if 'example' in doc:
                f.write('**Example:**\n\n```\n')
                if doc['example']:
                    f.write(doc['example'])
                f.write('\n```\n\n')
            f.write("---\n\n")

def main():
    """Generate API documentation."""
    try:
        # Create FastAPI app to get version manager
        app = create_app()
        
        # Get version manager from app state
        version_manager = app.state.version_manager
        
        # Create OpenAPI generator
        generator = OpenAPIGenerator(version_manager)
        
        # Generate docs for all versions
        logger.info("Generating OpenAPI documentation...")
        generator.generate_all()
        logger.info("Documentation generated successfully!")
        
        # Print locations of generated files
        docs_path = Path("docs/api/openapi")
        for spec_file in docs_path.glob("*.json"):
            logger.info(f"Generated spec: {spec_file}")
            
        # New: C# XML doc extraction
        logger.info("Extracting C# XML documentation from scripts...")
        csharp_docs = extract_all_csharp_docs()
        write_markdown(csharp_docs)
        logger.info(f"C# API documentation written to {DOCS_OUT}")
        
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 