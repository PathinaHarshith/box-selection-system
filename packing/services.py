from decimal import Decimal
from py3dbp import Packer, Bin, Item
from .models import Box, Product

class PackingService:
    @classmethod
    def select_box(cls, validated_data):
        """
        Determines the best box to fit the requested items.
        
        Step 1: Query all Box objects from DB, ordered by cost ASC.
        Step 2: For each box, instantiate py3dbp.Bin.
        Step 3: For each item x quantity, instantiate py3dbp.Item for every unit.
        Step 4: Run packer.pack(bigger_first=True, distribute_items=False).
        Step 5: A box is CAPABLE only if bin.unfitted_items == [].
        Step 6: Among all capable boxes, pick LOWEST COST.
        Step 7: Tiebreak on lowest cost -> pick HIGHEST VOLUME UTILIZATION.
        Step 8: If zero capable boxes -> return unpackable status.
        """
        order_reference = validated_data.get('order_reference')
        items_data = validated_data.get('items', [])
        
        # 1. Fetch boxes from DB, ordered by cost ASC
        boxes = Box.objects.all().order_by('cost')
        
        # Prepare products mapping to fetch details
        skus = [item['sku'] for item in items_data]
        products = Product.objects.filter(sku__in=skus)
        product_map = {p.sku: p for p in products}
        
        # 2. Iterate through boxes, looking for the best fit
        capable_boxes = []
        
        for box in boxes:
            packer = Packer()
            
            # Instantiate py3dbp.Bin with dimensions and max_weight
            # Convert Decimals to float for py3dbp
            bin_obj = Bin(
                name=str(box.id),
                width=float(box.length),
                height=float(box.width),
                depth=float(box.height),
                max_weight=float(box.max_weight_capacity)
            )
            packer.add_bin(bin_obj)
            
            # Instantiate py3dbp.Item for each unit of each item
            for item_data in items_data:
                sku = item_data['sku']
                quantity = item_data['quantity']
                product = product_map.get(sku)
                if not product:
                    continue
                for i in range(quantity):
                    packer.add_item(Item(
                        name=f"{sku}_{i}",
                        width=float(product.length),
                        height=float(product.width),
                        depth=float(product.height),
                        weight=float(product.weight)
                    ))
            
            # Run packer.pack
            packer.pack(bigger_first=True, distribute_items=False)
            
            # Check if this box is capable (bin.unfitted_items == [])
            current_bin = packer.bins[0]
            if len(current_bin.unfitted_items) == 0:
                # Calculate volume utilization percentage
                box_volume = float(box.length * box.width * box.height)
                total_packed_volume = 0.0
                total_weight = Decimal('0.00')
                packed_items_info = []
                
                for item in current_bin.items:
                    sku = item.name.split('_')[0]
                    prod = product_map[sku]
                    
                    # Convert float position back to Decimal
                    pos_x = Decimal(str(round(item.position[0], 2)))
                    pos_y = Decimal(str(round(item.position[1], 2)))
                    pos_z = Decimal(str(round(item.position[2], 2)))
                    
                    l_val = prod.length
                    w_val = prod.width
                    h_val = prod.height
                    
                    total_packed_volume += float(prod.length * prod.width * prod.height)
                    total_weight += prod.weight
                    
                    packed_items_info.append({
                        "sku": sku,
                        "position": {
                            "x": f"{pos_x:.2f}",
                            "y": f"{pos_y:.2f}",
                            "z": f"{pos_z:.2f}"
                        },
                        "dimensions": {
                            "l": f"{l_val:.2f}",
                            "w": f"{w_val:.2f}",
                            "h": f"{h_val:.2f}"
                        }
                    })
                
                utilization_percentage = round((total_packed_volume / box_volume) * 100, 1)
                
                capable_boxes.append({
                    "box": box,
                    "utilization_percentage": utilization_percentage,
                    "total_weight": total_weight,
                    "packed_items": packed_items_info
                })
        
        # If there are capable boxes, pick the best one
        if capable_boxes:
            # Sort by cost ASC, then utilization percentage DESC
            capable_boxes.sort(key=lambda x: (x['box'].cost, -x['utilization_percentage']))
            best_fit = capable_boxes[0]
            
            recommended_box = {
                "id": best_fit['box'].id,
                "name": best_fit['box'].name,
                "cost": f"{best_fit['box'].cost:.2f}",
                "utilization_percentage": best_fit['utilization_percentage'],
                "total_weight": f"{best_fit['total_weight']:.2f}"
            }
            
            # Sort packed_items to maintain consistent response ordering (e.g., SKU, then position x, y, z)
            packed_items_sorted = sorted(best_fit['packed_items'], key=lambda x: (x['sku'], x['position']['x'], x['position']['y'], x['position']['z']))
            
            return {
                "status": "success",
                "order_reference": order_reference,
                "recommended_box": recommended_box,
                "packed_items": packed_items_sorted,
                "unpacked_items": []
            }
        
        # If zero capable boxes -> return unpackable status
        unpacked_items = []
        for item_data in items_data:
            sku = item_data['sku']
            product = product_map.get(sku)
            if not product:
                continue
            
            # Check if this item alone can fit in any box
            exceeds_dimensions = True
            exceeds_weight = True
            
            for box in boxes:
                p_dims = sorted([product.length, product.width, product.height])
                b_dims = sorted([box.length, box.width, box.height])
                if p_dims[0] <= b_dims[0] and p_dims[1] <= b_dims[1] and p_dims[2] <= b_dims[2]:
                    exceeds_dimensions = False
                if product.weight <= box.max_weight_capacity:
                    exceeds_weight = False
            
            if exceeds_dimensions:
                reason = "exceeds all box dimensions"
            elif exceeds_weight:
                reason = "exceeds all box weight capacities"
            else:
                reason = "insufficient box capacity for multiple items"
                
            unpacked_items.append({
                "sku": sku,
                "reason": reason
            })
            
        return {
            "status": "unpackable",
            "message": "No available box can fit all items within dimensional and weight constraints.",
            "unpacked_items": unpacked_items
        }
