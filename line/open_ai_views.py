from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from django.conf import settings

# OpenAIの設定
embeddings_model = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY, model="text-embedding-3-small")


llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY,
                 model="gpt-4o-mini", temperature=0, max_tokens=500, top_p=0)


db = Chroma(collection_name='wdb',persist_directory="./wdb", embedding_function=embeddings_model)

prompt = PromptTemplate(
    input_variables=["document_snippet", "question"],
    template="""
あなたはドキュメントに基づいて質問に答えるアシスタントです。以下のドキュメントに基づいて質問に答えてください。
質問者は疑問形で質問してこない可能性もあり、文章を汲み取って相手が知りたいことを返してください。推測での回答は避けてください。
ドキュメントの内容はレジャーホテルのフロント業務に関するものです。できる限りドキュメントから情報を読み取り回答する意識をもってください。
もし記載にないことが問われた場合は、「わかりません。」を伝えてください。ただしあまりにも多くの質問に「わかりません。」と答えると、ユーザーに不親切だと思われるかもしれません。
文章は適切に返答し、適当な文章は返答しないようにしてください。チャットアプリへ返信するので、マークダウン記法ではなく、文章のみで返答してください。

    ドキュメント：
    {document_snippet}

    質問：{question}

    答え：
    """
)


def open_ai_chat(question):
    question_embedding = embeddings_model.embed_query(question)
    document_snippet = db.similarity_search_by_vector(question_embedding, k=3)
    snippets = [doc.page_content for doc in document_snippet]
    snippets = "\n---\n".join(snippets)
    filled_prompt = prompt.format(document_snippet=snippets, question=question)
    response = llm.invoke(filled_prompt, max_tokens=500)
    return response.content