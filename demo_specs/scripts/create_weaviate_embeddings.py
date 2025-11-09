#!/usr/bin/env python3
"""
Infrastructure as Spec - Weaviate Embedding and Chunking Script

This script processes all demo specifications, chunks them, creates embeddings using LM Studio,
and uploads them to Weaviate for RAG-based querying.

Requirements:
- LM Studio running locally on port 1234 with an embedding model loaded
- Weaviate running on localhost:8080 (via docker-compose)
- Python packages: requests, weaviate-client, python-dotenv

Usage:
    python create_weaviate_embeddings.py
"""

import os
import json
import glob
import requests
from pathlib import Path
from typing import List, Dict, Any
import weaviate
from weaviate.util import generate_uuid5
import time

# Configuration
LM_STUDIO_URL = "http://localhost:1234/v1/embeddings"
WEAVIATE_URL = "http://localhost:8080"
DEMO_SPECS_DIR = Path(__file__).parent.parent
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class LMStudioEmbedder:
    """Handles embedding generation via LM Studio"""

    def __init__(self, model_name: str = "text-embedding-nomic-embed-text-v1.5"):
        self.model_name = model_name
        self.session = requests.Session()

    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using LM Studio"""
        payload = {
            "input": text,
            "model": self.model_name,
            "encoding_format": "float"
        }

        try:
            response = self.session.post(LM_STUDIO_URL, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "data" in data and len(data["data"]) > 0:
                return data["data"][0]["embedding"]
            else:
                raise ValueError(f"No embedding data in response: {data}")

        except requests.exceptions.RequestException as e:
            print(f"Error calling LM Studio: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self.embed_text(text) for text in texts]

class WeaviateManager:
    """Manages Weaviate schema and data operations"""

    def __init__(self, url: str):
        self.client = weaviate.Client(url)

    def create_schema(self):
        """Create the InfraSpec schema class"""
        schema_class = {
            "class": "InfraSpec",
            "description": "Infrastructure as Spec documents with embeddings",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The chunked content from infrastructure specs"
                },
                {
                    "name": "source_file",
                    "dataType": ["string"],
                    "description": "Path to the source file"
                },
                {
                    "name": "file_type",
                    "dataType": ["string"],
                    "description": "Type of specification file (openapi, kubernetes, etc.)"
                },
                {
                    "name": "chunk_index",
                    "dataType": ["int"],
                    "description": "Index of this chunk within the file"
                }
            ],
            "vectorizer": "none"  # We'll provide our own vectors
        }

        try:
            self.client.schema.create_class(schema_class)
            print("✅ Created InfraSpec schema class")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️  InfraSpec schema already exists")
            else:
                raise e

    def upload_chunk(self, content: str, source_file: str, file_type: str,
                    chunk_index: int, vector: List[float]):
        """Upload a single chunk with its embedding"""
        data_object = {
            "content": content,
            "source_file": source_file,
            "file_type": file_type,
            "chunk_index": chunk_index
        }

        # Generate deterministic UUID based on content
        obj_uuid = generate_uuid5(data_object)

        try:
            self.client.data_object.create(
                data_object=data_object,
                class_name="InfraSpec",
                uuid=obj_uuid,
                vector=vector
            )
            return True
        except Exception as e:
            print(f"❌ Failed to upload chunk {chunk_index} from {source_file}: {e}")
            return False

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

        # Break if we're at the end
        if end >= len(text):
            break

    return chunks

def load_file_content(file_path: Path) -> str:
    """Load and extract content from various file types"""
    try:
        if file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    data = json.load(f)
                    return json.dumps(data, indent=2)
                else:
                    return f.read()
        elif file_path.suffix.lower() == '.log':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_path.suffix.lower() == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_path.suffix.lower() == '.py':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_path.suffix.lower() == '.tf':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Try to read as text
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"⚠️  Failed to load {file_path}: {e}")
        return ""

def get_file_type(file_path: Path) -> str:
    """Determine the type of spec file"""
    parent_dir = file_path.parent.name
    if parent_dir in ['openapi', 'kubernetes', 'policies', 'logs', 'scenarios', 'scripts', 'terraform', 'gitlab-ci', 'monitoring']:
        return parent_dir
    elif 'openapi' in str(file_path):
        return 'openapi'
    elif 'k8s' in str(file_path).lower() or 'kubernetes' in str(file_path).lower():
        return 'kubernetes'
    elif 'policy' in str(file_path).lower():
        return 'policies'
    elif '.log' in str(file_path):
        return 'logs'
    else:
        return 'other'

def process_demo_specs(embedder: LMStudioEmbedder, weaviate_mgr: WeaviateManager):
    """Process all demo specs and upload to Weaviate"""
    print("🔍 Discovering demo specification files...")

    # Find all relevant files
    patterns = [
        "**/*.json",
        "**/*.yaml",
        "**/*.yml",
        "**/*.md",
        "**/*.log",
        "**/*.py",
        "**/*.tf"
    ]

    all_files = []
    for pattern in patterns:
        all_files.extend(DEMO_SPECS_DIR.glob(pattern))

    # Filter out unwanted files
    exclude_patterns = ['__pycache__', '.git', 'node_modules']
    files_to_process = []

    for file_path in all_files:
        if any(excl in str(file_path) for excl in exclude_patterns):
            continue
        if file_path.name.startswith('.'):
            continue
        files_to_process.append(file_path)

    print(f"📁 Found {len(files_to_process)} files to process")

    total_chunks = 0
    successful_uploads = 0

    for file_path in files_to_process:
        print(f"📄 Processing: {file_path.relative_to(DEMO_SPECS_DIR)}")

        content = load_file_content(file_path)
        if not content.strip():
            continue

        # Chunk the content
        chunks = chunk_text(content)
        file_type = get_file_type(file_path)
        relative_path = str(file_path.relative_to(DEMO_SPECS_DIR))

        print(f"   📦 Created {len(chunks)} chunks")

        # Process chunks in batches for efficiency
        batch_size = 5
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i+batch_size]

            try:
                # Generate embeddings for batch
                vectors = embedder.embed_batch(batch_chunks)

                # Upload each chunk
                for j, (chunk, vector) in enumerate(zip(batch_chunks, vectors)):
                    chunk_index = i + j
                    success = weaviate_mgr.upload_chunk(
                        content=chunk,
                        source_file=relative_path,
                        file_type=file_type,
                        chunk_index=chunk_index,
                        vector=vector
                    )
                    if success:
                        successful_uploads += 1

                total_chunks += len(batch_chunks)
                print(f"   ✅ Uploaded batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")

            except Exception as e:
                print(f"   ❌ Failed to process batch starting at chunk {i}: {e}")
                continue

    print("\n📊 Processing Summary:")
    print(f"   Files processed: {len(files_to_process)}")
    print(f"   Total chunks: {total_chunks}")
    print(f"   Successful uploads: {successful_uploads}")

def main():
    """Main execution function"""
    print("🚀 Infrastructure as Spec - Weaviate Embedding Setup")
    print("=" * 60)

    # Check LM Studio connectivity
    print("🔗 Checking LM Studio connection...")
    try:
        embedder = LMStudioEmbedder()
        # Test with a simple embedding
        test_vector = embedder.embed_text("test")
        print(f"✅ LM Studio connected (embedding dimension: {len(test_vector)})")
    except Exception as e:
        print(f"❌ Cannot connect to LM Studio: {e}")
        print("   Make sure LM Studio is running on localhost:1234 with an embedding model loaded")
        print("   Recommended models: nomic-embed-text, text-embedding-ada-002, or similar")
        return 1

    # Check Weaviate connectivity
    print("🔗 Checking Weaviate connection...")
    try:
        weaviate_mgr = WeaviateManager(WEAVIATE_URL)
        if weaviate_mgr.client.is_ready():
            print("✅ Weaviate connected")
        else:
            print("❌ Weaviate not ready")
            return 1
    except Exception as e:
        print(f"❌ Cannot connect to Weaviate: {e}")
        print("   Make sure Weaviate is running on localhost:8080")
        return 1

    # Create schema
    print("📋 Setting up Weaviate schema...")
    weaviate_mgr.create_schema()

    # Process all specs
    print("⚙️  Processing demo specifications...")
    process_demo_specs(embedder, weaviate_mgr)

    print("\n🎉 Setup complete!")
    print("💡 You can now query your infrastructure specs using RAG in Open WebUI")
    print("   Example queries:")
    print("   - 'Which APIs require authentication?'")
    print("   - 'Show me network policy violations'")
    print("   - 'What are the payment service configurations?'")

    return 0

if __name__ == "__main__":
    exit(main())