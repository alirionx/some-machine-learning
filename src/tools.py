import os
import hashlib
import ollama
import psycopg
import pdfplumber

# some config------------------------------
DBHOST = os.environ.get("DBHOST", "localhost")
DBPORT = (os.environ.get("DBPORT", "5432"))
DBNAME = os.environ.get("DBNAME", "ollama_db")
DBUSER = os.environ.get("DBUSER", "ollama_user")
DBPASSWORD = os.environ.get("DBPASSWORD", "ollama_pass")

LLMMODEL_CHAT = os.environ.get("LLMMODEL_CHAT", "mistral")
LLMMODEL_EMBED = os.environ.get("LLMMODEL_EMBED", "avr/sfr-embedding-mistral")

#------------------------------------------
def get_pg_conn() -> psycopg.Connection:
    conn = psycopg.connect( f"""
        dbname={DBNAME} 
        user={DBUSER}  
        password={DBPASSWORD}  
        host={DBHOST}  
        port={DBPORT}
    """) 
    return conn

#--------------------
def check_db_prep():
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.commit()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id SERIAL PRIMARY KEY,
            doc_name TEXT,
            doc_index INTEGER,
            text TEXT,
            text_hash TEXT UNIQUE,
            embedding vector(4096)  
        );
        """)
    conn.commit()
    conn.close()

#--------------------
def extract_pages_from_pdf(pdf_path:str) -> list[str]:
    content = [] 
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            content.append(page.extract_text().strip())
    return content

#--------------------
def get_embedding(text:str) -> ollama.EmbeddingsResponse:
    response = ollama.embeddings(LLMMODEL_EMBED, text)
    return response

#--------------------
def insert_embedding_into_db(
        doc_name:str, doc_index:int, text:str, embedding:ollama.EmbeddingsResponse) -> str:
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute( """
        INSERT INTO embeddings (
            doc_name,
            doc_index,
            text,
            text_hash,
            embedding) VALUES (%s, %s, %s, %s, %s)
        """
        "", (doc_name, doc_index, text, text_hash, embedding.embedding)
    )
    conn.commit()
    conn.close()
    return text_hash

#--------------------
def delete_from_db_by_embedding(embedding:ollama.EmbeddingsResponse):
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM embeddings WHERE embedding = %s::vector", [embedding.embedding])
    conn.commit()
    conn.close()    

#--------------------
def search_vector_db(query_text:str, limit:int=5) -> list:
    query_embedding = get_embedding(query_text)
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT doc_name, doc_index, text, embedding <=> %s::vector AS similarity
        FROM embeddings
        ORDER BY similarity ASC
        LIMIT %s;
    """, (query_embedding.embedding, limit))
    results = cur.fetchall()
    cur.close()
    return results

#--------------------

