"""
Stock Alert System module
Provides low-stock alert detection, status indicators (GREEN, YELLOW, RED), and notifications.
"""
from app.inventory.inventory_tracking import get_low_stock_alerts

__all__ = ["get_low_stock_alerts"]
