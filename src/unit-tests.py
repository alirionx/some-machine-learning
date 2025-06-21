import os
import hashlib
import tools

# some config------------------

#------------------------------
def test_check_db_prep(): 
    tools.check_db_prep()

#-----------
def test_get_embedding():
    text = open("./testing/erlkoenig.txt", "r").read()
    res = tools.get_embedding(text=text.strip())
    print(f"embedding len: {len(res.embedding)}")

#-----------
# @pytest.mark.skip(reason="Switch Off")
def test_insert_embedding_into_db():
    doc_name = "erlkoenig.txt"
    doc_path = os.path.join("./testing", doc_name)
    text = open(doc_path, "r").read()
    tools.insert_embedding_into_db(doc_name=doc_name, content=[text])
    
#-----------
# @pytest.mark.skip(reason="Switch Off")
def test_delete_embedding_by_hash():
    doc_name = "erlkoenig.txt"
    doc_path = os.path.join("./testing", doc_name)
    text = open(doc_path, "r").read()
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    tools.delete_from_db_by_hash(text_hash=text_hash)

#-----------
def test_extract_pages_from_pdf():
    pdf_path = "./testing/some-content/goethe_gedichte.pdf"
    content = tools.extract_pages_from_pdf(pdf_path=pdf_path)
    print(f"\n - page_size = {len(content)}")
    assert len(content) > 2

#-----------
def test_chat_with_llm():
    msg_obj = {
        "role": "user", 
        "content": "How you are doing?"
    }
    res = tools.chat_with_llm(msg_obj=msg_obj)
    assert "message" in res 
    print(res.message)

#-----------
