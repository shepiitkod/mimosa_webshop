import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .ai_service import generate_premium_description


@staff_member_required
@require_POST
def ai_enhance_description(request):
    try:
        body = json.loads(request.body)
        draft_text = body.get("draft_text", "").strip()
        target_language = body.get("target_language", "французька").strip()

        if not draft_text:
            return JsonResponse({"error": "Поле draft_text порожнє."}, status=400)

        enhanced = generate_premium_description(draft_text, target_language)
        return JsonResponse({"enhanced_description": enhanced})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Невалідний JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
