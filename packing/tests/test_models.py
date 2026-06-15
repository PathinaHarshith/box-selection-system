from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from packing.models import Box, Product

class ModelTestCase(TestCase):
    def test_decimal_precision(self):
        # Create Box with high precision decimals and check if 2-decimal rounding/storage works correctly.
        box = Box.objects.create(
            name="Precision Box",
            length=Decimal('10.123'),
            width=Decimal('20.456'),
            height=Decimal('30.789'),
            max_weight_capacity=Decimal('15.555'),
            cost=Decimal('1.234')
        )
        box.refresh_from_db()
        # Verify 2-decimal place representation
        self.assertEqual(box.length, Decimal('10.12'))
        self.assertEqual(box.width, Decimal('20.46'))
        self.assertEqual(box.height, Decimal('30.79'))
        self.assertEqual(box.max_weight_capacity, Decimal('15.56'))
        self.assertEqual(box.cost, Decimal('1.23'))

    def test_product_sku_uniqueness(self):
        Product.objects.create(
            sku="PROD-UNIQUE",
            name="Product Unique 1",
            length=Decimal("5.00"),
            width=Decimal("5.00"),
            height=Decimal("5.00"),
            weight=Decimal("1.00")
        )
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                sku="PROD-UNIQUE",
                name="Product Unique 2",
                length=Decimal("6.00"),
                width=Decimal("6.00"),
                height=Decimal("6.00"),
                weight=Decimal("2.00")
            )

    def test_str_representation(self):
        box = Box.objects.create(
            name="Standard Box",
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            max_weight_capacity=Decimal('10.00'),
            cost=Decimal('1.00')
        )
        product = Product.objects.create(
            sku="PROD-A",
            name="Standard Product",
            length=Decimal('5.00'),
            width=Decimal('5.00'),
            height=Decimal('5.00'),
            weight=Decimal('1.00')
        )
        self.assertIn("Standard Box", str(box))
        self.assertIn("PROD-A - Standard Product", str(product))
