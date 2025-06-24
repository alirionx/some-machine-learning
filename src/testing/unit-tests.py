import os
import sys
import hashlib

# some config------------------
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
import tools
from models import ChatItem

#------------------------------
def test_check_db_prep(): 
    tools.check_db_prep()

#-----------
def test_chat_with_llm():
    item = ChatItem(
        role="user",
        content="How you are doing?"
    )
    response = tools.chat_with_llm(context=[item])
    print(response)

#-----------
def test_get_embedding():
    text = open("./erlkoenig.txt", "r").read()
    res = tools.get_embedding(text=text.strip())
    print(f"embedding len: {len(res.embedding)}")

#-----------
# @pytest.mark.skip(reason="Switch Off")
def test_insert_embeddings_into_db():
    doc_name = "erlkoenig.txt"
    doc_path = os.path.join("./", doc_name)
    text = open(doc_path, "r").read()
    tools.insert_embeddings_into_db(doc_name=doc_name, content=[text])
    
#-----------
# @pytest.mark.skip(reason="Switch Off")
def test_delete_embedding_by_hash():
    doc_name = "erlkoenig.txt"
    doc_path = os.path.join("./", doc_name)
    text = open(doc_path, "r").read()
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    tools.delete_from_db_by_hash(text_hash=text_hash)

#-----------
def test_extract_extract_chunks_from_text():
    with open( "./some-content/coutries.txt", "r") as f:
        text = f.read()
    content = tools.extract_chunks_from_text(text=text)
    print(f"\n - page_size = {len(content)}")
    assert len(content) > 2

#-----------
def test_extract_pages_from_pdf():
    with open( "./some-content/goethe_gedichte.pdf", "rb") as f:
        pdf_bytes = f.read()
    content = tools.extract_pages_from_pdf(pdf_bytes=pdf_bytes)
    print(f"\n - page_size = {len(content)}")
    assert len(content) > 2


#-----------
