from decimal import Decimal
from django.test import TestCase
from packing.models import Box, Product
from packing.services import PackingService

class PackingEngineTestCase(TestCase):
    def setUp(self):
        # Create standard boxes
        self.box_sm = Box.objects.create(
            name="Small Box",
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            max_weight_capacity=Decimal('5.00'),
            cost=Decimal('1.00')
        )
        self.box_md = Box.objects.create(
            name="Medium Box",
            length=Decimal('20.00'),
            width=Decimal('20.00'),
            height=Decimal('20.00'),
            max_weight_capacity=Decimal('15.00'),
            cost=Decimal('2.50')
        )
        self.box_lg = Box.objects.create(
            name="Large Box",
            length=Decimal('30.00'),
            width=Decimal('30.00'),
            height=Decimal('30.00'),
            max_weight_capacity=Decimal('50.00'),
            cost=Decimal('5.00')
        )

        # Products
        self.prod_sm = Product.objects.create(
            sku="PROD-SM",
            name="Small Widget",
            length=Decimal('5.00'),
            width=Decimal('5.00'),
            height=Decimal('5.00'),
            weight=Decimal('0.50')
        )
        self.prod_md1 = Product.objects.create(
            sku="PROD-MD1",
            name="Medium Item 1",
            length=Decimal('12.00'),
            width=Decimal('10.00'),
            height=Decimal('8.00'),
            weight=Decimal('2.00')
        )
        self.prod_md2 = Product.objects.create(
            sku="PROD-MD2",
            name="Medium Item 2",
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            weight=Decimal('3.00')
        )
        self.prod_md3 = Product.objects.create(
            sku="PROD-MD3",
            name="Medium Item 3",
            length=Decimal('8.00'),
            width=Decimal('8.00'),
            height=Decimal('8.00'),
            weight=Decimal('1.50')
        )
        self.prod_heavy = Product.objects.create(
            sku="PROD-HV",
            name="Heavy Item",
            length=Decimal('5.00'),
            width=Decimal('5.00'),
            height=Decimal('5.00'),
            weight=Decimal('8.00')
        )

    def test_volumetric_fit_single_item(self):
        # TEST 1 — Standard Volumetric Fit
        validated_data = {
            "order_reference": "ORD-001",
            "items": [{"sku": "PROD-SM", "quantity": 1}]
        }
        res = PackingService.select_box(validated_data)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["recommended_box"]["name"], "Small Box")
        self.assertEqual(res["recommended_box"]["cost"], "1.00")
        self.assertEqual(len(res["packed_items"]), 1)

    def test_multi_item_aggregation(self):
        # TEST 2 — Multi-Item Aggregation
        validated_data = {
            "order_reference": "ORD-002",
            "items": [
                {"sku": "PROD-MD1", "quantity": 1},
                {"sku": "PROD-MD2", "quantity": 1},
                {"sku": "PROD-MD3", "quantity": 1}
            ]
        }
        res = PackingService.select_box(validated_data)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["recommended_box"]["name"], "Medium Box")
        self.assertEqual(len(res["packed_items"]), 3)
        self.assertEqual(len(res["unpacked_items"]), 0)

    def test_weight_constraint_violation(self):
        # TEST 3 — Weight Constraint Violation
        validated_data = {
            "order_reference": "ORD-003",
            "items": [{"sku": "PROD-HV", "quantity": 1}]
        }
        res = PackingService.select_box(validated_data)
        self.assertEqual(res["status"], "success")
        # Small Box max weight capacity is 5.00, our item is 8.00.
        # It should skip Small Box and choose Medium Box (max capacity 15.00).
        self.assertEqual(res["recommended_box"]["name"], "Medium Box")
