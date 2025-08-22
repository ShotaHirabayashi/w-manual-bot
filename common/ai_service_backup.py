from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from django.conf import settings
from rank_bm25 import BM25Okapi
import re
import os
from typing import List, Dict, Tuple

# MeCab辞書パスの設定
os.environ.setdefault('MECABRC', '/opt/homebrew/etc/mecabrc')

class AIService:
    def __init__(self):
        # OpenAI設定
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
            model="gpt-4o-mini",  # 必要に応じてgpt-4oに変更
            temperature=0, 
            max_tokens=500
        )

        # データベース設定（既存のDBを使用、メタデータで区別）
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
        filled_prompt = self.rewrite_prompt.format(question=question)
        response = self.llm_rewrite.invoke(filled_prompt)
        return response.content

    def hybrid_search(self, query: str, doc_type: str = None, k: int = 10) -> List[Dict]:
        """ハイブリッド検索（BM25 + ベクトル）"""
        # ベクトル検索
        query_embedding = self.embeddings_model.embed_query(query)
        
        # メタデータフィルタ付き検索
        filter_dict = {"type": doc_type} if doc_type else None
        vector_results = self.db.similarity_search_by_vector_with_relevance_scores(
            query_embedding, 
            k=k * 2,  # BM25と組み合わせるため多めに取得
            filter=filter_dict
        )
        
        # ドキュメント取得（BM25用）
        all_docs = self.db.get(where=filter_dict) if filter_dict else self.db.get()
        
        if not all_docs['documents']:
            return []
        
        # BM25検索
        texts = all_docs['documents']
        metadatas = all_docs['metadatas']
        ids = all_docs['ids']
        
        # 日本語トークナイズ
        try:
            import MeCab
            # より詳細な解析のためのオプション設定
            # -O wakati: 分かち書き出力
            # -F %f[6]: 原形を出力（語幹正規化）
            mecab = MeCab.Tagger('-Owakati')
            mecab_detailed = MeCab.Tagger('-F%m\\t%f[6]\\t%f[0]\\n -E\\n')
            
            def tokenize_japanese(text):
                try:
                    # 基本的な分かち書き
                    wakati_result = mecab.parse(text).strip()
                    if not wakati_result:
                        return text.split()
                    
                    # より詳細な解析で品詞情報も取得
                    detailed_result = mecab_detailed.parse(text)
                    
                    tokens = []
                    meaningful_pos = ['名詞', '動詞', '形容詞', '副詞', '連体詞', '感動詞']
                    
                    for line in detailed_result.split('\\n'):
                        if line.strip() and '\\t' in line:
                            parts = line.split('\\t')
                            if len(parts) >= 3:
                                surface = parts[0]  # 表層形
                                base_form = parts[1] if parts[1] != '*' else surface  # 原形
                                pos = parts[2]  # 品詞
                                
                                # 意味のある品詞のみを抽出し、原形を使用
                                if any(meaningful in pos for meaningful in meaningful_pos):
                                    # ひらがな1文字や記号は除外
                                    if len(base_form) > 1 or not (base_form.isascii() or base_form in 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'):
                                        tokens.append(base_form)
                                elif len(surface) > 1:  # その他でも2文字以上は含める
                                    tokens.append(surface)
                    
                    # フォールバック：詳細解析に失敗した場合は分かち書き結果を使用
                    if not tokens:
                        tokens = wakati_result.split()
                    
                    # さらなるフィルタリング
                    filtered_tokens = []
                    stop_words = {'です', 'ます', 'である', 'だ', 'で', 'に', 'を', 'が', 'は', 'の', 'と', 'から', 'まで', 'より', 'て', 'た', 'し', 'ば', 'ん'}
                    
                    for token in tokens:
                        # ストップワード除去
                        if token not in stop_words and len(token) > 1:
                            filtered_tokens.append(token)
                    
                    return filtered_tokens if filtered_tokens else wakati_result.split()
                    
                except Exception as e:
                    print(f"MeCab detailed analysis failed: {e}")
                    # 基本的な分かち書きにフォールバック
                    try:
                        result = mecab.parse(text).strip()
                        return result.split() if result else text.split()
                    except:
                        return text.split()
                        
        except (ImportError, Exception) as e:
            print(f"Warning: MeCab not available, using simple tokenization: {e}")
            # MeCabが利用できない場合の高度な分割
            def tokenize_japanese(text):
                import re
                # 日本語の文字種に基づく簡易分割
                # ひらがな、カタカナ、漢字、英数字の境界で分割
                pattern = r'[\\u3040-\\u309F]+|[\\u30A0-\\u30FF]+|[\\u4E00-\\u9FAF]+|[a-zA-Z0-9]+|[0-9０-９]+'
                tokens = re.findall(pattern, text)
                return tokens if tokens else text.split()
        
        tokenized_texts = [tokenize_japanese(text) for text in texts]
        tokenized_query = tokenize_japanese(query)
        
        if tokenized_texts and tokenized_query:
            bm25 = BM25Okapi(tokenized_texts)
            bm25_scores = bm25.get_scores(tokenized_query)
        else:
            bm25_scores = [0] * len(texts)
        
        # スコア統合
        doc_scores = {}
        
        # ベクトル検索結果のスコアを記録
        for doc, score in vector_results:
            doc_id = doc.metadata.get('id', doc.page_content[:50])
            doc_scores[doc_id] = {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'vector_score': score,
                'bm25_score': 0
            }
        
        # BM25スコアを追加
        for i, (text, metadata, doc_id) in enumerate(zip(texts, metadatas, ids)):
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    'content': text,
                    'metadata': metadata,
                    'vector_score': 0,
                    'bm25_score': bm25_scores[i]
                }
            else:
                doc_scores[doc_id]['bm25_score'] = bm25_scores[i]
        
        # 統合スコア計算
        combined_results = []
        for doc_id, scores in doc_scores.items():
            # 正規化
            max_vector = max([s['vector_score'] for s in doc_scores.values()])
            max_bm25 = max([s['bm25_score'] for s in doc_scores.values()])
            
            normalized_vector = scores['vector_score'] / max(1, max_vector)
            normalized_bm25 = scores['bm25_score'] / max(1, max_bm25)
            
            combined_score = 0.6 * normalized_vector + 0.4 * normalized_bm25
            
            combined_results.append({
                'content': scores['content'],
                'metadata': scores['metadata'],
                'score': combined_score
            })
        
        return sorted(combined_results, key=lambda x: x['score'], reverse=True)[:k]

    def rerank_documents(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Cross-Encoderで再ランク"""
        if not documents:
            return []
        
        try:
            if self.cross_encoder is None:
                # Cross-Encoderが利用できない場合は元のスコアを維持
                for doc in documents:
                    doc['rerank_score'] = doc.get('score', 0.5)
                return documents
                
            pairs = [[query, doc['content']] for doc in documents]
            scores = self.cross_encoder.predict(pairs)
            
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(scores[i])
            
            return sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
        except Exception as e:
            print(f"Warning: Cross-Encoder reranking failed: {e}")
            # フォールバック：元のスコアを使用
            for doc in documents:
                doc['rerank_score'] = doc.get('score', 0.5)
            return documents

    def check_confidence_and_consistency(self, query: str, documents: List[Dict]) -> Tuple[bool, str]:
        """低確信/矛盾/要素不足の判定"""
        if not documents:
            return False, "no_documents"
        
        # 低確信：上位スコアが閾値以下
        top_score = documents[0].get('final_score', 0)
        if top_score < 0.3:
            return False, "low_confidence"
        
        # 上位3件を対象に検証
        top_docs = documents[:3]
        
        # 矛盾チェック：数値の食い違い
        numbers_pattern = r'\d+[時間分円%枚個]'
        extracted_numbers = []
        
        for doc in top_docs:
            numbers = re.findall(numbers_pattern, doc['content'])
            if numbers:
                extracted_numbers.append(set(numbers))
        
        # 同じ単位の数値が異なる場合は矛盾
        if len(extracted_numbers) > 1:
            for i in range(len(extracted_numbers) - 1):
                for j in range(i + 1, len(extracted_numbers)):
                    set1, set2 = extracted_numbers[i], extracted_numbers[j]
                    # 同じ単位で異なる数値があるかチェック
                    for num1 in set1:
                        unit1 = re.sub(r'\d+', '', num1)
                        for num2 in set2:
                            unit2 = re.sub(r'\d+', '', num2)
                            if unit1 == unit2 and num1 != num2:
                                return False, "contradiction"
        
        # 要素不足：質問の重要キーワードが文書に含まれているか
        important_keywords = self.extract_important_keywords(query)
        if important_keywords:
            combined_text = ' '.join([doc['content'] for doc in top_docs])
            keyword_coverage = sum(
                1 for keyword in important_keywords 
                if keyword in combined_text
            )
            
            if keyword_coverage < len(important_keywords) * 0.5:
                return False, "insufficient_elements"
        
        return True, "ok"

    def extract_important_keywords(self, query: str) -> List[str]:
        """質問から重要キーワードを抽出"""
        keywords = []
        
        # ドメイン固有の重要用語
        important_terms = [
            '利用単位', '利単', '有効期限', '料金', '時間', '予約', 
            'キャンセル', 'チェックイン', 'チェックアウト', '清掃',
            '延長', '割引', 'サービス', '部屋', 'フロント'
        ]
        
        for term in important_terms:
            if term in query:
                keywords.append(term)
        
        return keywords

    def chat(self, question: str) -> dict:
        """メイン処理 - プロセス情報付きで返却"""
        try:
            # 1. 質問リライト
            rewritten_query = self.rewrite_query(question)
            
            # プロセス情報を格納
            process_info = {
                'original_query': question,
                'rewritten_query': rewritten_query,
                'search_type': 'qa',
                'confidence_check': None,
                'fallback_used': False,
                'sources_count': 0
            }
            
            # 2. ハイブリッド検索（QA優先）
            qa_results = self.hybrid_search(rewritten_query, doc_type="qa", k=5)
            
            # QAが見つからない場合は全体から検索
            if not qa_results:
                qa_results = self.hybrid_search(rewritten_query, doc_type=None, k=5)
                process_info['search_type'] = 'all'
            
            # 3. 再ランク
            reranked_docs = self.rerank_documents(rewritten_query, qa_results)
            
            # 4. スコア設定（メタデータブーストは廃止）
            for doc in reranked_docs:
                doc['final_score'] = doc.get('rerank_score', doc.get('score', 0))
            boosted_docs = sorted(reranked_docs, key=lambda x: x['final_score'], reverse=True)
            
            # 5. 低確信/矛盾/要素不足の判定
            is_confident, reason = self.check_confidence_and_consistency(question, boosted_docs)
            process_info['confidence_check'] = {'is_confident': is_confident, 'reason': reason}
            
            # 6. フォールバック（必要時）
            if not is_confident:
                process_info['fallback_used'] = True
                # 経営指針から検索
                guideline_results = self.hybrid_search(rewritten_query, doc_type="guideline", k=3)
                
                if guideline_results:
                    guideline_reranked = self.rerank_documents(rewritten_query, guideline_results)
                    # スコア設定
                    for doc in guideline_reranked:
                        doc['final_score'] = doc.get('rerank_score', doc.get('score', 0))
                    
                    # 既存の結果と統合
                    boosted_docs.extend(guideline_reranked)
                    boosted_docs = sorted(boosted_docs, key=lambda x: x['final_score'], reverse=True)[:5]
            
            # 7. 最終回答生成
            if not boosted_docs:
                return {
                    'answer': "申し訳ございません。該当する情報が見つかりませんでした。",
                    'process_info': process_info
                }
            
            # 上位文書を結合
            top_documents = boosted_docs[:3]
            documents_text = "\n---\n".join([doc['content'] for doc in top_documents])
            
            # 出典情報を構築
            sources = []
            for doc in top_documents:
                source = doc['metadata'].get('source', '')
                doc_type = doc['metadata'].get('type', '')
                if source:
                    sources.append(f"{source}({doc_type})")
            sources_text = "、".join(sources) if sources else "マニュアル"
            process_info['sources_count'] = len(top_documents)
            process_info['sources'] = sources
            
            filled_prompt = self.answer_prompt.format(
                documents=documents_text,
                question=question
            )
            
            response = self.llm_answer.invoke(filled_prompt)
            
            # 回答とプロセス情報を返却
            return {
                'answer': f"{response.content}\n\n【参照元：{sources_text}】",
                'process_info': process_info
            }
            
        except Exception as e:
            # エラーハンドリング
            import traceback
            print(f"Error in chat: {str(e)}")
            print(traceback.format_exc())
            
            # フォールバック（従来の単純な検索）
            try:
                question_embedding = self.embeddings_model.embed_query(question)
                document_snippet = self.db.similarity_search_by_vector(question_embedding, k=3)
                snippets = [doc.page_content for doc in document_snippet]
                snippets_text = "\n---\n".join(snippets)
                
                # 従来のプロンプトを使用
                simple_prompt = PromptTemplate(
                    input_variables=["document_snippet", "question"],
                    template="""
あなたはドキュメントに基づいて質問に答えるアシスタントです。以下のドキュメントに基づいて質問に答えてください。
推測での回答は避けてください。チャットアプリへ返信するので、マークダウン記法ではなく、文章のみで返答してください。

ドキュメント：
{document_snippet}

質問：{question}

答え：
"""
                )
                
                filled_prompt = simple_prompt.format(document_snippet=snippets_text, question=question)
                response = self.llm_answer.invoke(filled_prompt)
                return {
                    'answer': response.content,
                    'process_info': {'original_query': question, 'error_fallback': True}
                }
                
            except Exception as fallback_error:
                return {
                    'answer': "申し訳ございません。システムエラーが発生しました。しばらくしてから再度お試しください。",
                    'process_info': {'original_query': question, 'system_error': True}
                }

# シングルトンインスタンス
ai_service = AIService()