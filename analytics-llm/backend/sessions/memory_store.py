from vectorstore.vectordb import store_vector

def save_chat(session_id, message):
    store_vector(session_id, message)
