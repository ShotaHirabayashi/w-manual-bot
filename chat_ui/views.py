from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json

# Use lightweight AI service on memory-constrained environments
if getattr(settings, 'USE_LITE_AI_SERVICE', False):
    from common.ai_service_lite import AIServiceLite
    ai_service = AIServiceLite()
else:
    from common.ai_service import ai_service

def chat_view(request):
    """チャット画面のビュー"""
    return render(request, 'chat_ui/chat.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """チャットAPIエンドポイント"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        
        if not question:
            return JsonResponse({'error': '質問が入力されていません'}, status=400)
        
        # AIサービスを使用して回答を生成
        result = ai_service.chat(question)
        
        if isinstance(result, dict):
            return JsonResponse({
                'answer': result['answer'],
                'process_info': result['process_info']
            })
        else:
            # 後方互換性
            return JsonResponse({'answer': result})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': '無効なリクエストです'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'エラーが発生しました: {str(e)}'}, status=500)