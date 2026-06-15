from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from packing.models import Box, Product

class PackingViewsTestCase(APITestCase):
    def setUp(self):
        # Create standard boxes
        self.box_sm = Box.objects.create(
            name="Small Box",
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            max_weight_capacity=Decimal('10.00'),
            cost=Decimal('1.00')
        )
        self.box_a = Box.objects.create(
            name="Box A",
            length=Decimal('10.00'),
            width=Decimal('10.00'),
            height=Decimal('10.00'),
            max_weight_capacity=Decimal('10.00'),
            cost=Decimal('2.00')
        )
        self.box_b = Box.objects.create(
            name="Box B",
            length=Decimal('12.00'),
            width=Decimal('12.00'),
            height=Decimal('12.00'),
            max_weight_capacity=Decimal('10.00'),
            cost=Decimal('1.50')
        )

        self.prod_sm = Product.objects.create(
            sku="PROD-SM",
            name="Small Item",
            length=Decimal('5.00'),
            width=Decimal('5.00'),
            height=Decimal('5.00'),
            weight=Decimal('1.00')
        )
        self.prod_giant = Product.objects.create(
            sku="PROD-GIANT",
            name="Giant Item",
            length=Decimal('100.00'),
            width=Decimal('100.00'),
            height=Decimal('100.00'),
            weight=Decimal('50.00')
        )

    def test_box_crud(self):
        url = reverse('box-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(url, {
            "name": "Another Box",
            "length": "15.00",
            "width": "15.00",
            "height": "15.00",
            "max_weight_capacity": "25.00",
            "cost": "3.50"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_crud(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cost_optimization(self):
        # TEST 4 — Cost Optimization
        # Same order physically fits Box A (cost=2.00) AND Box B (cost=1.50).
        # Assert: API returns Box B. Test HTTP 200 + response JSON structure.
        # Note: We delete self.box_sm first so it doesn't fit in box_sm (cost=1.00) and only leaves Box A and Box B as capable options.
        self.box_sm.delete()
        
        url = reverse('pack')
        payload = {
            "order_reference": "ORD-004",
            "items": [{"sku": "PROD-SM", "quantity": 1}]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Structure assertions
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["order_reference"], "ORD-004")
        self.assertEqual(response.data["recommended_box"]["name"], "Box B")
        self.assertEqual(response.data["recommended_box"]["cost"], "1.50")
        self.assertIn("packed_items", response.data)
        self.assertEqual(len(response.data["packed_items"]), 1)

    def test_unpackable_edge_case(self):
        # TEST 5 — Unpackable Edge Case
        # Item dimensions exceed ALL available boxes.
        # Assert: API returns status="unpackable", HTTP 422, unpacked_items list is non-empty.
        url = reverse('pack')
        payload = {
            "order_reference": "ORD-005",
            "items": [{"sku": "PROD-GIANT", "quantity": 1}]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["status"], "unpackable")
        self.assertTrue(len(response.data["unpacked_items"]) > 0)
        self.assertEqual(response.data["unpacked_items"][0]["sku"], "PROD-GIANT")
        self.assertEqual(response.data["unpacked_items"][0]["reason"], "exceeds all box dimensions")

    def test_malformed_payload_validation(self):
        # TEST 6 — Malformed Payload Validation
        url = reverse('pack')

        # a) missing "items" field
        payload_missing = {"order_reference": "ORD-006A"}
        response = self.client.post(url, payload_missing, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", response.data)

        # b) negative quantity
        payload_neg = {
            "order_reference": "ORD-006B",
            "items": [{"sku": "PROD-SM", "quantity": -2}]
        }
        response = self.client.post(url, payload_neg, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", response.data)

        # c) non-existent SKU
        payload_nonexistent = {
            "order_reference": "ORD-006C",
            "items": [{"sku": "NON-EXISTENT", "quantity": 1}]
        }
        response = self.client.post(url, payload_nonexistent, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", response.data)
