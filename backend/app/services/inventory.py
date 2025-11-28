from .. import schemas


def evaluate(items: list[schemas.InventoryItem]) -> schemas.InventoryResponse:
    notices: list[schemas.InventoryAdvice] = []
    recs: list[str] = []
    for item in items:
        threshold = item.reorder_point + item.reserve_qty
        if item.stock_qty <= threshold:
            recommend_qty = max(threshold - item.stock_qty, 0.0) + 0.2 * item.reorder_point
            notices.append(
                schemas.InventoryAdvice(
                    sku=item.sku,
                    action="reorder",
                    reason="stock at or below threshold",
                    recommended_qty=round(recommend_qty, 2),
                )
            )
            if "beef" in item.name.lower():
                recs.append("Consider sourcing wagyu beef for premium menu positioning")
    return schemas.InventoryResponse(notices=notices, recommendations=recs)
