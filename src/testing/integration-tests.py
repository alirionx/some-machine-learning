import os
import sys
import hashlib
import mimetypes
import pytest

# some config------------------
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
import tools
from models import ChatItem

#-some globals---
content_path = "./some-content"

#----------------
# @pytest.mark.skip(reason="Switch Off")
def test_chat_with_llm():
    questions = [
        "How you are doing?",
        "It's very sad that you don't have emotions or feelings.",
        "I like you anyway.",
        "What was my first question?"
    ]

    context = []
    for q in questions:
        q_item = ChatItem(role="user", content=q )
        context.append(q_item)
        context = tools.chat_with_llm(context=context)
    
    for item in context:
        print( item.model_dump_json(indent=2) )

#----------------
# @pytest.mark.skip(reason="Switch Off")
def test_check_db_prep(): 
    tools.check_db_prep()

#----------------
# @pytest.mark.skip(reason="Switch Off")
def test_multi_chunks_into_db():
    print("\n")
    #----
    for filename in os.listdir(content_path):
        file_path = os.path.join(content_path, filename)
        mime_guess = mimetypes.guess_type(file_path)[0]
        if "pdf" in mime_guess:
            with open(file_path, "rb") as fl:
                pdf_bytes = fl.read()
            content = tools.extract_pages_from_pdf(pdf_bytes=pdf_bytes)
        elif "text" in mime_guess:
            with open(file_path, "r") as fl:
                text = fl.read()
            content = tools.extract_chunks_from_text(text=text)
        else:
            continue
        tools.insert_embedding_into_db(doc_name=filename, content=content)
        print(f" - {filename} : added page size = {len(content)}")
        assert len(content) > 2
    
    #----
    
#----------------
# @pytest.mark.skip(reason="Switch Off")
def test_search_vector_db():
    # query_text = """
    # Ein Mann der mit seinem Sohn auf dem Arm durch die Nacht reitet.
    # Dem Sohn geht es nicht gut. Der Vater ist in Eile.
    # """
    # query_text = """
    # Einer der etwas zu essen im Wasser fängt.
    # """
    # query_text = """
    # Mit Magie die Bude sauber machen.
    # """
    # query_text = """
    # mourns the fragile life and tragic death of Marilyn Monroe, 
    # portraying her as a symbol of fleeting fame
    # """
    # query_text = """
    # Holy child of god with wings and somebody had these wings in his dreams.
    # """
    query_text = """
    Democracy was invented here. A very ancient language is spoken here.
    """
    query_text = """
    The land of thinkers and poets. Automobiles come from here.
    """
    
    res = tools.search_vector_db(query_text=query_text.strip(), limit=2)

    pretty = res[0].model_dump_json(indent=2)
    # print(pretty)
    for item in res:
        pretty = item.model_dump_json(indent=2)
        print(pretty)
    

#----------------
# @pytest.mark.skip(reason="Switch Off")
def test_delete_embedding_by_embedding():
    for filename in os.listdir(content_path):
        file_path = os.path.join(content_path, filename)
        mime_guess = mimetypes.guess_type(file_path)[0]
        if "pdf" in mime_guess:
            with open(file_path, "rb") as fl:
                pdf_bytes = fl.read()
            content = tools.extract_pages_from_pdf(pdf_bytes=pdf_bytes)
        elif "text" in mime_guess:
            with open(file_path, "r") as fl:
                text = fl.read()
            content = tools.extract_chunks_from_text(text=text)
        else:
            continue
        for text in content:
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            tools.delete_from_db_by_hash(text_hash=text_hash)
        print(f" - {filename} : deleted page size = {len(content)}")

#----------------


#----------------

