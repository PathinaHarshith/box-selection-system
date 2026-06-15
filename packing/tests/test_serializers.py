from decimal import Decimal
from django.test import TestCase
from packing.models import Product
from packing.serializers import PackRequestSerializer

class SerializerTestCase(TestCase):
    def setUp(self):
        self.prod_a = Product.objects.create(
            sku="PROD-A",
            name="Product A",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.00")
        )

    def test_pack_request_serializer_missing_items(self):
        data = {
            "order_reference": "ORD-123"
        }
        serializer = PackRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)

    def test_pack_request_serializer_negative_quantity(self):
        data = {
            "order_reference": "ORD-123",
            "items": [
                {"sku": "PROD-A", "quantity": -5}
            ]
        }
        serializer = PackRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)

    def test_pack_request_serializer_non_existent_sku(self):
        data = {
            "order_reference": "ORD-123",
            "items": [
                {"sku": "NON-EXISTENT", "quantity": 1}
            ]
        }
        serializer = PackRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)
        self.assertIn("do not exist in the database", str(serializer.errors["items"]))
