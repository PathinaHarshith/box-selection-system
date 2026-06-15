from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import Box, Product
from .serializers import BoxSerializer, ProductSerializer, PackRequestSerializer, PackResponseSerializer
from .services import PackingService

class BoxViewSet(ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class PackView(APIView):
    @extend_schema(
        request=PackRequestSerializer,
        responses={
            200: PackResponseSerializer,
            422: PackResponseSerializer
        },
        description="Calculates the most optimal box and positions items inside it using a 3D bin packing algorithm."
    )
    def post(self, request, *args, **kwargs):
        serializer = PackRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = PackingService.select_box(serializer.validated_data)
        
        if result.get("status") == "success":
            response_serializer = PackResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        response_serializer = PackResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
