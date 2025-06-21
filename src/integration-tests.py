import os
import hashlib
import pytest

import tools

#-some globals---
pdfs_path = "./testing/some-content"

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
    query_text = """
    Einer der etwas zu essen im Wasser fängt.
    """
    query_text = """
    Mit Magie die Bude sauber machen.
    """
    res = tools.search_vector_db(query_text=query_text.strip())
    pretty = res[0].model_dump_json(indent=2)
    print(pretty)

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

