from django.urls import path
from shop.shop.views import ai_enhance_description

urlpatterns = [
    path(
        "admin/api/ai-enhance/",
        ai_enhance_description,
        name="ai_enhance_description",
    ),
]