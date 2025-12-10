def parsePDF(path:str)-> list:
    """ takes PDF file path and returns PDF parsed pages"""
    from langchain_community.document_loaders import PyPDFLoader
    llm_loader = PyPDFLoader(path)
    pages = llm_loader.load_and_split()
    return pages