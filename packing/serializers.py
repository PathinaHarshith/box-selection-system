from rest_framework import serializers
from .models import Box, Product

class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PackItemSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField(min_value=1)


class PackRequestSerializer(serializers.Serializer):
    order_reference = serializers.CharField(max_length=100)
    items = serializers.ListField(
        child=PackItemSerializer(),
        allow_empty=False
    )

    def validate_items(self, value):
        # Extract all SKUs and validate in bulk to avoid N+1 queries
        skus = [item['sku'] for item in value]
        existing_skus = set(
            Product.objects.filter(sku__in=skus).values_list('sku', flat=True)
        )
        
        missing_skus = [sku for sku in skus if sku not in existing_skus]
        if missing_skus:
            raise serializers.ValidationError(
                f"The following SKU(s) do not exist in the database: {', '.join(missing_skus)}"
            )
        return value


class RecommendedBoxSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    utilization_percentage = serializers.FloatField()
    total_weight = serializers.DecimalField(max_digits=10, decimal_places=2)


class PackedItemPositionSerializer(serializers.Serializer):
    x = serializers.DecimalField(max_digits=10, decimal_places=2)
    y = serializers.DecimalField(max_digits=10, decimal_places=2)
    z = serializers.DecimalField(max_digits=10, decimal_places=2)


class PackedItemDimensionsSerializer(serializers.Serializer):
    l = serializers.DecimalField(max_digits=10, decimal_places=2)
    w = serializers.DecimalField(max_digits=10, decimal_places=2)
    h = serializers.DecimalField(max_digits=10, decimal_places=2)


class PackedItemSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=100)
    position = PackedItemPositionSerializer()
    dimensions = PackedItemDimensionsSerializer()


class UnpackedItemSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=100)
    reason = serializers.CharField(max_length=255)


class PackResponseSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=20)
    order_reference = serializers.CharField(max_length=100, required=False)
    recommended_box = RecommendedBoxSerializer(required=False, allow_null=True)
    packed_items = PackedItemSerializer(many=True, required=False)
    unpacked_items = UnpackedItemSerializer(many=True, required=False)
    message = serializers.CharField(max_length=255, required=False)
