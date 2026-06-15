from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BoxViewSet, ProductViewSet, PackView

router = DefaultRouter()
router.register('boxes', BoxViewSet, basename='box')
router.register('products', ProductViewSet, basename='product')

urlpatterns = router.urls + [
    path('pack/', PackView.as_view(), name='pack'),
]
