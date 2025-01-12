
import os
def pinecone_retrieval(user_input, ctx, embedder):
    index_name = "sbhacks"

    # Query text
    query_text = user_input

    # Generate the query vector
    query_vector = embedder.encode(query_text)
    query_params = {
        "top_k": 15,
        "include_values": True,
        "include_metadata": True,
        "vector": query_vector
    }

    # Retrieve documents from Pinecone
    query_docs = ctx.read.pinecone(
        index_name=index_name,
        api_key=os.environ["PINECONE_API_KEY"],
        query=query_params,
    ).take_all()

    return "".join([doc["text_representation"] for doc in query_docs])