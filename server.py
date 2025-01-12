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
from verifier import verify_short_answer
from mcq_gen import generate_mcq
from shortq_gen import generate_shortq
from pinecone_fetch import pinecone_retrieval
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()
ARYN_API_KEY = os.getenv("ARYN_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

app = Flask(__name__)

@app.route('/upload-embedding', methods=['POST'])
def upload_embedding():
    try:
        # Parse request data
        data = request.get_json()
        if not data or 'file_name' not in data or 'type_of_question' not in data or 'number_of_questions' not in data or 'user_prompt_text' not in data:
            return jsonify({"error": "Invalid input. 'file_name', 'type_of_question', 'number_of_questions', and 'user_prompt_text' are required."}), 400

        file_name = data['file_name']
        type_of_question = data['type_of_question']
        number_of_questions = data['number_of_questions']
        user_prompt_text = data['user_prompt_text']

        # Access the file from the specified path
        file_path = os.path.join("/tmp", file_name)
        file_path = file_name
        print(file_path)
        if not os.path.exists(file_path):
            return jsonify({"error": f"File {file_name} does not exist at the specified path."}), 404

        # Initialize the Sycamore context
        ctx = sycamore.init(ExecMode.LOCAL)
        print("Print 1")
        # Set the embedding model and its parameters
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        max_tokens = 512
        dimensions = 384

        # Initialize the tokenizer
        tokenizer = HuggingFaceTokenizer(model_name)
        print("Print 2")
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
        print("Print 3")
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
        print("Print 4")
        # Load the same embedding model
        model_name = "all-MiniLM-L6-v2"
        embedder = SentenceTransformer(model_name)
        
        pinecone_context = pinecone_retrieval(user_prompt_text, ctx, embedder)
        # import pdb; pdb.set_trace()
        if type_of_question=="mcq":
            questions = generate_mcq(pinecone_context, number_of_questions)
        elif type_of_question=="short":
            questions = generate_shortq(pinecone_context, number_of_questions)
        # if type_of_question=="mcq":
        #     questions = generate_mcq(user_prompt_text, number_of_questions)
        # elif type_of_question=="short":
        #     questions = generate_shortq(user_prompt_text, number_of_questions)
        print("Reached here")
        return questions

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

@app.route('/verify-short', methods=['POST'])
def verify():
    try:
        # Parse request data
        data = request.get_json()
        if not data or 'question' not in data or 'answer' not in data:
            return jsonify({"error": "Invalid input. 'question' and 'answer' are required."}), 400

        question = data['question']
        user_answer = data['answer']

        # Verify the answer using verifier.py
        result = verify_short_answer(question, user_answer)

        if not result:
            return jsonify({"error": "Verification failed."}), 500

        # Return the correct answer and explanation
        return jsonify({
            "correct_answer": result.get('correct_answer'),
            "explanation": result.get('explanation')
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
