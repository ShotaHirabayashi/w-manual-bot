# -*- coding: utf-8 -*-
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from django.conf import settings
from typing import List, Dict, Optional
import re

class AIService:
    def __init__(self):
        # OpenAI Embeddings（日本語対応）
        self.embeddings_model = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )


        # LLM設定（質問リライト用：小型）
        self.llm_rewrite = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=100
        )

        # LLM設定（最終回答生成用：中型）
        self.llm_answer = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=500
        )

        # ChromaDB（ベクトルデータベース）
        try:
            # 既存のコレクションを取得または作成
            from chromadb import PersistentClient
            client = PersistentClient(path="./wdb")
            
            # コレクションが存在するか確認
            collections = client.list_collections()
            collection_names = [c.name for c in collections]
            print(f"Available collections: {collection_names}")
            
            # 'wdb'コレクションを使用（存在しない場合は作成）
            if 'wdb' not in collection_names:
                print("Creating 'wdb' collection...")
                client.create_collection(name='wdb')
            
            self.db = Chroma(
                client=client,
                collection_name='wdb',
                embedding_function=self.embeddings_model
            )
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            # フォールバック: デフォルト設定で初期化
            self.db = Chroma(
                collection_name='wdb',
                persist_directory="./wdb",
                embedding_function=self.embeddings_model
            )

        # Cross-Encoderモデル（遅延初期化）
        self._cross_encoder = None

        # 質問リライト用プロンプト
        self.rewrite_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
以下の質問を検索に適した形にリライトしてください：
- 略語を展開（例：「利単」→「利用単位」）
- 同義語を追加
- 口語的表現を標準化

質問：{question}

リライト結果（1行で）：
"""
        )

        # 最終回答生成用プロンプト
        self.answer_prompt = PromptTemplate(
            input_variables=["documents", "question"],
            template="""
以下のドキュメントに基づいて質問に答えてください。
推測は一切せず、ドキュメントに書かれている内容のみで回答してください。
チャットアプリへ返信するので、マークダウン記法ではなく、文章のみで返答してください。

ドキュメント：
{documents}

質問：{question}

回答：
"""
        )

    @property
    def cross_encoder(self):
        """Cross-Encoderモデルの遅延初期化"""
        if self._cross_encoder is None:
            try:
                from sentence_transformers import CrossEncoder
                self._cross_encoder = CrossEncoder('sonoisa/sentence-bert-base-ja-mean-tokens-v2')
            except Exception as e:
                print(f"Warning: Cross-Encoder initialization failed: {e}")
                self._cross_encoder = None
        return self._cross_encoder

    def rewrite_query(self, question: str) -> str:
        """質問をリライト"""
        prompt = self.rewrite_prompt.format(question=question)
        response = self.llm_rewrite.invoke(prompt)
        return response.content.strip()

    def vector_search(self, query: str, doc_type: Optional[str] = None, k: int = 10) -> List[Dict]:
        """ベクトル検索（シンプル版）"""
        # メタデータフィルタ
        filter_dict = {"type": doc_type} if doc_type else None
        
        # LangChainのsimilarity_search_with_relevance_scoresを直接使用
        results = self.db.similarity_search_with_relevance_scores(
            query, 
            k=k,
            filter=filter_dict
        )
        
        # 結果を整形
        documents = []
        for doc, score in results:
            documents.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': score
            })
        
        return documents

    def rerank_documents(self, query: str, documents: List[Dict], top_n: int = 10) -> List[Dict]:
        """Cross-Encoderで再ランク（シンプル版）"""
        if not documents:
            return []
        
        # Cross-Encoderが利用できない場合は元のスコアを維持
        if self.cross_encoder is None:
            for doc in documents:
                doc['final_score'] = doc.get('score', 0.5)
            return sorted(documents, key=lambda x: x['final_score'], reverse=True)[:top_n]
        
        try:
            # Cross-Encoderで再スコアリング
            pairs = [[query, doc['content']] for doc in documents]
            scores = self.cross_encoder.predict(pairs)
            
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(scores[i])
                # ベクトルスコアと再ランクスコアを組み合わせ
                doc['final_score'] = 0.4 * doc.get('score', 0) + 0.6 * doc['rerank_score']
            
            return sorted(documents, key=lambda x: x['final_score'], reverse=True)[:top_n]
        except Exception as e:
            print(f"Warning: Cross-Encoder reranking failed: {e}")
            for doc in documents:
                doc['final_score'] = doc.get('score', 0.5)
            return sorted(documents, key=lambda x: x['final_score'], reverse=True)[:top_n]

    def check_confidence(self, documents: List[Dict]) -> tuple[bool, str]:
        """簡易的な確信度チェック"""
        if not documents:
            return False, "no_documents"
        
        # トップスコアが低い場合
        top_score = documents[0].get('final_score', 0)
        if top_score < 0.3:
            return False, "low_confidence"
        
        # 簡易的な矛盾チェック（数値の食い違い）
        if len(documents) >= 2:
            numbers_pattern = r'\d+[時間分円%枚個]'
            nums1 = set(re.findall(numbers_pattern, documents[0]['content']))
            nums2 = set(re.findall(numbers_pattern, documents[1]['content']))
            
            # 同じ単位で異なる数値があるか簡易チェック
            for n1 in nums1:
                unit1 = re.sub(r'\d+', '', n1)
                for n2 in nums2:
                    unit2 = re.sub(r'\d+', '', n2)
                    if unit1 == unit2 and n1 != n2:
                        return False, "contradiction"
        
        return True, "ok"

    def chat(self, question: str) -> dict:
        """メイン処理（シンプル版）"""
        try:
            # 1. 質問リライト
            rewritten_query = self.rewrite_query(question)
            
            # 2. ベクトル検索（QA優先）
            qa_results = self.vector_search(rewritten_query, doc_type="qa", k=10)
            search_type = 'qa'
            
            # QAが見つからない場合は全体から検索
            if not qa_results:
                qa_results = self.vector_search(rewritten_query, doc_type=None, k=10)
                search_type = 'all'
            
            # 3. 再ランク
            reranked_docs = self.rerank_documents(rewritten_query, qa_results, top_n=5)
            
            # 4. 確信度チェック
            is_confident, reason = self.check_confidence(reranked_docs)
            
            # 5. 低確信の場合はガイドラインから補完
            if not is_confident:
                guideline_results = self.vector_search(rewritten_query, doc_type="guideline", k=5)
                if guideline_results:
                    guideline_reranked = self.rerank_documents(rewritten_query, guideline_results, top_n=3)
                    reranked_docs.extend(guideline_reranked)
                    reranked_docs = sorted(reranked_docs, key=lambda x: x['final_score'], reverse=True)[:5]
            
            # 6. 最終回答生成
            if not reranked_docs:
                return {
                    'answer': "申し訳ございません。該当する情報が見つかりませんでした。",
                    'process_info': {
                        'original_query': question,
                        'rewritten_query': rewritten_query,
                        'search_type': search_type,
                        'confidence_check': None,
                        'fallback_used': False,
                        'sources_count': 0
                    }
                }
            
            # 上位文書を結合
            top_documents = reranked_docs[:3]
            documents_text = "\n---\n".join([doc['content'] for doc in top_documents])
            
            # 出典情報
            sources = []
            for doc in top_documents:
                source = doc['metadata'].get('source', '')
                doc_type = doc['metadata'].get('type', '')
                if source:
                    sources.append(f"{source}({doc_type})")
            sources_text = "、".join(sources) if sources else "マニュアル"
            
            # LLMで回答生成
            filled_prompt = self.answer_prompt.format(
                documents=documents_text,
                question=question
            )
            response = self.llm_answer.invoke(filled_prompt)
            
            return {
                'answer': f"{response.content}\n\n【参照元：{sources_text}】",
                'process_info': {
                    'original_query': question,
                    'rewritten_query': rewritten_query,
                    'search_type': search_type,
                    'confidence_check': {'is_confident': is_confident, 'reason': reason},
                    'fallback_used': not is_confident,
                    'sources_count': len(top_documents),
                    'sources': sources
                }
            }
            
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            # エラー時のフォールバック
            try:
                # シンプルなベクトル検索のみ
                results = self.db.similarity_search(question, k=3)
                if results:
                    context = "\n---\n".join([doc.page_content for doc in results])
                    filled_prompt = self.answer_prompt.format(
                        documents=context,
                        question=question
                    )
                    response = self.llm_answer.invoke(filled_prompt)
                    return {
                        'answer': response.content,
                        'process_info': {
                            'original_query': question,
                            'error_fallback': True
                        }
                    }
            except:
                pass
            
            return {
                'answer': "申し訳ございません。システムエラーが発生しました。",
                'process_info': {
                    'original_query': question,
                    'system_error': True
                }
            }

# シングルトンインスタンス
ai_service = AIService()