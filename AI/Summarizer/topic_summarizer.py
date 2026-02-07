from AI.config import settings
from dotenv import dotenv_values
from prompts.summarizer_prompt import system_prompt, user_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

model = settings.SUMMARIZER_MODEL
env_values = dotenv_values("./app.env")
api_key = env_values["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(
    model=settings.SUMMARIZER_MODEL,
    google_api_key=api_key,
    temperature=0.7,
)
chat_prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt.prompt_text), ("user", user_prompt.prompt_text)]
)

chain = chat_prompt | llm


def summarize_sci_topic(sci_topic, context: str = "None"):
    response = chain.invoke({"sci_topic": sci_topic, "context": context})
    return response.content[0]["text"]


# print(summarize_sci_topic(sci_topic="Deep Learning"))
