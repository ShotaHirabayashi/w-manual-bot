"""
Lightweight AI Service for memory-constrained environments
Disables heavy ML models when running on Render free tier
"""
import os
from typing import List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class AIServiceLite:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        # Initialize OpenAI models
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=self.openai_api_key
        )
        
        self.llm_rewrite = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            openai_api_key=self.openai_api_key
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=self.openai_api_key
        )
        
        # Initialize vector store
        persist_directory = "./chroma_db"
        self.vector_store = Chroma(
            collection_name="wdb",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        
        # Define prompts
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""あなたはEC事業者向けのヘルプデスクアシスタントです。
以下の検索結果を参考に、質問に対して正確に回答してください。

検索結果:
{context}

質問: {question}

回答を提供する際は以下の点に注意してください：
1. 検索結果に基づいて正確に回答する
2. 不明な点は推測せず「情報が見つかりませんでした」と回答する
3. 具体的で実践的なアドバイスを提供する
4. 必要に応じて手順を箇条書きで説明する

回答：
"""
        )
        
        self.rewrite_prompt = PromptTemplate(
            input_variables=["question"],
            template="""以下の質問を、検索エンジン向けに最適化してください。
重要なキーワードを抽出し、簡潔で明確な検索クエリに変換してください。

元の質問: {question}

最適化されたクエリ（日本語で、簡潔に）："""
        )
    
    def rewrite_query(self, question: str) -> str:
        """質問をリライト（軽量版）"""
        try:
            prompt = self.rewrite_prompt.format(question=question)
            response = self.llm_rewrite.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Query rewrite failed: {e}")
            return question
    
    def search_documents(self, query: str, k: int = 10) -> List[Document]:
        """ベクトル検索のみ実行（リランキングなし）"""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Document search failed: {e}")
            return []
    
    def generate_answer(self, question: str, documents: List[Document]) -> str:
        """回答生成"""
        if not documents:
            return "申し訳ございません。関連する情報が見つかりませんでした。"
        
        # ドキュメントのコンテンツを結合
        context = "\n\n".join([doc.page_content for doc in documents[:5]])
        
        # プロンプトの作成
        prompt = self.qa_prompt.format(context=context, question=question)
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"回答の生成中にエラーが発生しました: {str(e)}"
    
    def chat(self, question: str) -> str:
        """メイン処理（軽量版）"""
        try:
            # クエリのリライト
            rewritten_query = self.rewrite_query(question)
            print(f"Rewritten query: {rewritten_query}")
            
            # ドキュメント検索（リランキングなし）
            documents = self.search_documents(rewritten_query, k=5)
            
            # 回答生成
            answer = self.generate_answer(question, documents)
            
            return answer
            
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"
    
    def add_document(self, text: str, metadata: dict = None):
        """ドキュメントの追加"""
        try:
            # テキストを分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
            )
            
            documents = text_splitter.create_documents(
                texts=[text],
                metadatas=[metadata] if metadata else None
            )
            
            # ベクトルストアに追加
            self.vector_store.add_documents(documents)
            
            return True
        except Exception as e:
            print(f"Document addition failed: {e}")
            return False