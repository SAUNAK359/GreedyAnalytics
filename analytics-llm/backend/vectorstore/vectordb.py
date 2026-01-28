import chromadb

client = chromadb.Client()
collection = client.create_collection("chat_memory")

def store_vector(session_id, text):
    collection.add(
        documents=[text],
        metadatas=[{"session_id": session_id}],
        ids=[f"{session_id}_{hash(text)}"]
    )

def retrieve(session_id, query):
    return collection.query(
        query_texts=[query],
        where={"session_id": session_id}
    )
