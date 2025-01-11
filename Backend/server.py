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
load_dotenv()
# API Keys
ARYN_API_KEY = os.getenv("ARYN_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


# Sycamore uses lazy execution for efficiency, so the ETL pipeline will only execute when running cells with specific functions.

paths = "Backend/internetwebbasics.pdf"

# Initialize the Sycamore context
ctx = sycamore.init(ExecMode.LOCAL)
# Set the embedding model and its parameters
model_name = "sentence-transformers/all-MiniLM-L6-v2"
max_tokens = 512
dimensions = 384
# Initialize the tokenizer
tokenizer = HuggingFaceTokenizer(model_name)

ds = (
    ctx.read.binary(paths, binary_format="pdf")
    # Partition and extract tables and images
    .partition(partitioner=ArynPartitioner(
        threshold="auto",
        use_ocr=True,
        extract_table_structure=True,
        extract_images=True
    ))
    # Use materialize to cache output. If changing upstream code or input files, change setting from USE_STORED to RECOMPUTE to create a new cache.
    .materialize(path="/content/materialize/partitioned", source_mode=MaterializeSourceMode.USE_STORED)
    # Merge elements into larger chunks
    .merge(merger=GreedySectionMerger(
      tokenizer=tokenizer,  max_tokens=max_tokens, merge_across_pages=False
    ))
    # Split elements that are too big to embed
    .split_elements(tokenizer=tokenizer, max_tokens=max_tokens)
)

ds.execute()

# Display the first 3 pages after chunking
show_pages(ds, limit=3)

embedded_ds = (
    # Copy document properties to each Document's sub-elements
    ds.spread_properties(["path", "entity"])
    # Convert all Elements to Documents
    .explode()
    # Embed each Document. You can change the embedding model. Make your target vector index matches this number of dimensions.
    .embed(embedder=SentenceTransformerEmbedder(model_name=model_name))
)
# To know more about docset transforms, please visit https://sycamore.readthedocs.io/en/latest/sycamore/transforms.html

# Create an instance of ServerlessSpec with the specified cloud provider and region
spec = ServerlessSpec(cloud="aws", region="us-east-1")
index_name = "sbhacks"
# Write data to a Pinecone index
embedded_ds.write.pinecone(index_name=index_name,
    dimensions=dimensions,
    distance_metric="cosine",
    index_spec=spec
)