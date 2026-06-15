# Box Selection System

An automated 3D bin-packing API for selecting optimal shipping boxes and mapping item placement coordinates.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%20LTS-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14-red)](https://www.django-rest-framework.org/)
[![py3dbp](https://img.shields.io/badge/Packing-py3dbp-orange)](https://pypi.org/project/py3dbp/)

---

## 3. System Overview

In e-commerce warehousing, shipping costs are heavily driven by both package dimensions (dimensional weight) and actual package weight. Shipping items in unnecessarily large boxes leads to high shipping fees (wasted air) and excessive packing material consumption. 

This system automates box selection by:
- Taking an order reference and list of products with their quantities.
- Performing a 3D physical bin-packing simulation of all items inside each available box.
- Evaluating boxes against dimensional, orientation, and weight limit constraints.
- Selecting the single lowest-cost box capable of holding the order, falling back to volume-utilization as a tie-breaker.

---

## 4. Setup & Installation

Follow these steps to set up and run the project locally:

```bash
# Clone the repository
git clone https://github.com/[YOUR_GITHUB_USERNAME]/box-selection-system
cd box-selection-system

# Create a python virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat

# Install package dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Load local seed fixtures (5 Box sizes and 6 Products)
python manage.py loaddata fixtures/sample_data.json

# Launch development server
python manage.py runserver
```

---

## 5. Running Tests

Execute the 14-test suite validating models precision, serializer schemas, packing constraints, and views:

```bash
python manage.py test --verbosity=2
```

---

## 6. API Endpoints

All endpoints are registered under `/api/v1/`:

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/boxes/` | List all available shipping boxes |
| `POST` | `/api/v1/boxes/` | Create a new box configuration |
| `GET` | `/api/v1/boxes/{id}/` | Retrieve a specific box's details |
| `PUT` | `/api/v1/boxes/{id}/` | Update an existing box's details |
| `DELETE` | `/api/v1/boxes/{id}/` | Delete a box config |
| `GET` | `/api/v1/products/` | List all registered products |
| `POST` | `/api/v1/products/` | Register a new product |
| `GET` | `/api/v1/products/{id}/` | Retrieve product details |
| `PUT` | `/api/v1/products/{id}/` | Update product details |
| `DELETE` | `/api/v1/products/{id}/` | Delete a product from inventory |
| `POST` | `/api/v1/pack/` | Calculate the optimal box recommendation |
| `GET` | `/api/schema/` | Fetch the OpenAPI 3 schema YAML/JSON |
| `GET` | `/api/docs/` | Interactive Swagger UI API documentation |

> [!NOTE]
> The `/api/v1/pack/` endpoint returns HTTP 200 OK on a successful box recommendation, and HTTP 422 Unprocessable Entity when items cannot fit into any available box (status: "unpackable").

---

## 7. Example Curl Commands

### 7.1. Create a Shipping Box
```bash
curl -X POST http://127.0.0.1:8000/api/v1/boxes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Ultra-Box", "length": "15.00", "width": "12.00", "height": "10.00", "max_weight_capacity": "25.00", "cost": "2.10"}'
```

### 7.2. Create a Product
```bash
curl -X POST http://127.0.0.1:8000/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{"sku": "PROD-WID-NEW", "name": "Novelty Widget", "length": "6.00", "width": "4.00", "height": "3.00", "weight": "0.75"}'
```

### 7.3. Request Box Packing Recommendation
```bash
curl -X POST http://127.0.0.1:8000/api/v1/pack/ \
  -H "Content-Type: application/json" \
  -d '{"order_reference": "ORD-101", "items": [{"sku": "PROD-WID-SM", "quantity": 2}, {"sku": "PROD-WID-MD", "quantity": 1}]}'
```

### 7.4. Access Swagger UI Documentation
Open the following URL in any browser:
```
http://127.0.0.1:8000/api/docs/
```

---

## 8. Example Request & Response for `/api/v1/pack/`

### Request Payload (`POST`)
```json
{
  "order_reference": "ORD-202",
  "items": [
    {
      "sku": "PROD-WID-SM",
      "quantity": 2
    },
    {
      "sku": "PROD-WID-MD",
      "quantity": 1
    }
  ]
}
```

### Response Payload (`200 OK` - Success)
```json
{
  "status": "success",
  "order_reference": "ORD-202",
  "recommended_box": {
    "id": 2,
    "name": "Medium Box",
    "cost": "2.50",
    "utilization_percentage": 32.2,
    "total_weight": "5.50"
  },
  "packed_items": [
    {
      "sku": "PROD-WID-MD",
      "position": {
        "x": "0.00",
        "y": "0.00",
        "z": "0.00"
      },
      "dimensions": {
        "l": "12.00",
        "w": "10.00",
        "h": "10.00"
      }
    },
    {
      "sku": "PROD-WID-SM",
      "position": {
        "x": "0.00",
        "y": "10.00",
        "z": "0.00"
      },
      "dimensions": {
        "l": "5.00",
        "w": "5.00",
        "h": "5.00"
      }
    },
    {
      "sku": "PROD-WID-SM",
      "position": {
        "x": "12.00",
        "y": "0.00",
        "z": "0.00"
      },
      "dimensions": {
        "l": "5.00",
        "w": "5.00",
        "h": "5.00"
      }
    }
  ],
  "unpacked_items": []
}
```

---

## 9. Architecture Notes

### Why `py3dbp`?
The `py3dbp` library implements a heuristic 3D bin-packing algorithm (based on the first-fit-decreasing strategy). Unlike simple volume calculations (which ignore item orientations and collisions), `py3dbp` simulates physical placement in a 3D coordinate space. This guarantees that items are physically capable of being nested inside the box.

### Why `DecimalField`?
Standard floats suffer from floating-point arithmetic imprecision (drift), making comparisons unreliable (e.g., `0.1 + 0.2 != 0.3`). In spatial computations, a tiny drift could result in a product falsely failing a dimensional constraint. The project uses Python `Decimal` and Django `DecimalField` in the persistence layer, converting to float strictly when passing parameters to `py3dbp` and back to `Decimal` when preparing JSON API responses.

### Selection & Tie-Breaker Logic
1. **Cost-First**: Boxes are evaluated in ascending order of their unit cost (`cost` ASC).
2. **First Fit**: The cheapest box that can physically contain all items within dimensions and weight capacity is preferred.
3. **Volume Tie-Break**: If multiple boxes have identical costs, the algorithm chooses the box with the **highest volume utilization percentage** (minimizes wasted air).

---

## 10. License

This project is licensed under the terms of the [MIT License](LICENSE).
