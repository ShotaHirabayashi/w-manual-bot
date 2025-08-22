from common.ai_service import ai_service

def open_ai_chat(question: str) -> str:
    """共通AIサービスを使用してチャット処理"""
    result = ai_service.chat(question)
    # LINEでは回答のみを返す（後方互換性のため）
    if isinstance(result, dict):
        return result['answer']
    return result