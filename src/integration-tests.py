import os
import json
import hashlib
import pytest

import tools

#-some globals---
pdfs_path = "./testing/some-content"

#----------------
def test_chat_with_llm():
    questions = [
        "How you are doing?",
        "It's very sad that you don't have emotions or feelings.",
        "I like you anyway.",
        "What was my first question?"
    ]

    context = []
    for q in questions:
        msg_obj = { "role": "user", "content": q }
        context.append( msg_obj )
        res = tools.chat_with_llm(msg_obj=msg_obj)
        context.append( res.message.model_dump() )
    
    for item in context:
        print( json.dumps(item, indent=2) )

#----------------
def test_check_db_prep(): 
    tools.check_db_prep()

#----------------
# @pytest.mark.skip(reason="Switch Off")
def test_multi_pdf_into_db():
    print("\n")
    #----
    for filename in os.listdir(pdfs_path):
        pdf_path = os.path.join(pdfs_path, filename)
        content = tools.extract_pages_from_pdf(pdf_path=pdf_path)
        tools.insert_embedding_into_db(doc_name=filename, content=content)
        print(f" - {filename} : added page size = {len(content)}")
        assert len(content) > 2
    
    #----
    
#----------------
# @pytest.mark.skip(reason="Switch Off")
def test_search_vector_db():
    query_text = """
    Ein Mann der mit seinem Sohn auf dem Arm durch die Nacht reitet.
    Dem Sohn geht es nicht gut. Der Vater ist in Eile.
    """
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

    res = tools.search_vector_db(query_text=query_text.strip())

    pretty = res[0].model_dump_json(indent=2)
    print(pretty)
    # for item in res:
    #     pretty = item.model_dump_json(indent=2)
    #     print(pretty)
    

#----------------
# @pytest.mark.skip(reason="Switch Off")
def test_delete_embedding_by_embedding():
    for filename in os.listdir(pdfs_path):
        pdf_path = os.path.join(pdfs_path, filename)
        content = tools.extract_pages_from_pdf(pdf_path=pdf_path)
        for text in content:
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            tools.delete_from_db_by_hash(text_hash=text_hash)
        print(f" - {filename} : deleted page size = {len(content)}")

#----------------


#----------------

