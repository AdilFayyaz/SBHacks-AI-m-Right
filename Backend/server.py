
from flask import Flask, request, jsonify
import pyarrow.fs
import sycamore
import json
import os
from pinecone import Pinecone
from sycamore.functions.tokenizer import HuggingFaceTokenizer
from sycamore.llms import OpenAIModels, OpenAI
from sycamore.transforms import COALESCE_WHITESPACE
from sycamore.transforms.merge_elements import GreedySectionMerger
from sycamore.transforms.partition import ArynPartitioner
from sycamore.transforms.embed import SentenceTransformerEmbedder
from sycamore.materialize_config import MaterializeSourceMode
from sycamore.utils.pdf_utils import show_pages
from sycamore.transforms.summarize_images import SummarizeImages
from sycamore.context import ExecMode
from pinecone import ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ARYN_API_KEY = os.getenv("ARYN_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

app = Flask(__name__)

@app.route('/upload-embedding', methods=['POST'])
def upload_embedding():
    try:
        # Get file from the request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        # Save the file temporarily
        file_path = os.path.join("/tmp", file.filename)
        file.save(file_path)

        # Initialize the Sycamore context
        ctx = sycamore.init(ExecMode.LOCAL)

        # Set the embedding model and its parameters
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        max_tokens = 512
        dimensions = 384

        # Initialize the tokenizer
        tokenizer = HuggingFaceTokenizer(model_name)

        # Process the document
        ds = (
            ctx.read.binary(file_path, binary_format="pdf")
            .partition(partitioner=ArynPartitioner(
                threshold="auto",
                use_ocr=True,
                extract_table_structure=True,
                extract_images=True
            ))
            .materialize(path="/tmp/materialize/partitioned", source_mode=MaterializeSourceMode.RECOMPUTE)
            .merge(merger=GreedySectionMerger(
                tokenizer=tokenizer, max_tokens=max_tokens, merge_across_pages=False
            ))
            .split_elements(tokenizer=tokenizer, max_tokens=max_tokens)
        )

        ds.execute()

        # Embed the processed document
        embedded_ds = (
            ds.spread_properties(["path", "entity"])
            .explode()
            .embed(embedder=SentenceTransformerEmbedder(model_name=model_name))
        )

        # Create Pinecone index spec
        spec = ServerlessSpec(cloud="aws", region="us-east-1")
        index_name = "sbhacks"

        # Write embeddings to Pinecone
        embedded_ds.write.pinecone(
            index_name=index_name,
            dimensions=dimensions,
            distance_metric="cosine",
            index_spec=spec
        )

        return jsonify({"message": "File successfully processed and embeddings uploaded to Pinecone."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
