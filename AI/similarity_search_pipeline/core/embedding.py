from dotenv import dotenv_values
env_values = dotenv_values('app.env')
cohere_api_key = env_values['COHERE_API_KEY']

def get_embedding_model(model: str):
    if model=="cohere":
        from langchain_community.embeddings.cohere import CohereEmbeddings
        embedding_llm = CohereEmbeddings(cohere_api_key=cohere_api_key, user_agent="langchain")
        return embedding_llm
    
