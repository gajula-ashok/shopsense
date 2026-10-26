"""
ShopSense E-Commerce Theme Engine
Inspired by Flipkart, Amazon, and Meesho apps.
Provides theme presets, dynamic CSS generation, and reusable e-commerce UI components.
"""

from typing import Dict, Any, Tuple
import hashlib

# Curated High-Definition E-Commerce Product Images (Unsplash royalty-free CDN)
PRODUCT_IMAGES = {
    # Electronics
    "Noise-Cancelling Wireless Headphones Pro": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
    "Ultra-Slim RGB Mechanical Keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
    "Smartwatch Series 7 Titanium": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
    "Thunderbolt 4 High-Speed USB Dock": "https://images.unsplash.com/photo-1616440347437-b1c73416efc2?w=600&auto=format&fit=crop&q=80",
    "4K Ultra HD Dual-Monitor Webcam 60FPS": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",

    # Fashion
    "Organic Cotton Classic Graphic Tee": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
    "Classic Slim-Fit Stretch Denim Jeans": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&auto=format&fit=crop&q=80",
    "Lightweight Waterproof All-Weather Windbreaker": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80",
    "Merino Wool Thermal Crewneck Sweater": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&auto=format&fit=crop&q=80",

    # Books
    "Data Science & AI Engineering Handbook": "https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=600&auto=format&fit=crop&q=80",
    "Modern Web Architecture with FastAPI & React": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
    "The Art of Scalable Cloud Computing": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&auto=format&fit=crop&q=80",
    "Deep Learning Illustrated (Hardcover Edition)": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&auto=format&fit=crop&q=80",

    # Home & Kitchen
    "Ergonomic Lumbar Support Mesh Office Chair": "https://images.unsplash.com/photo-1580481077195-c328865c4046?w=600&auto=format&fit=crop&q=80",
    "Cold Brew Precision Espresso Coffee Maker": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=600&auto=format&fit=crop&q=80",
    "Ultrasonic Aroma Diffuser with Ambient LED": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=600&auto=format&fit=crop&q=80",
    "Non-Stick Ceramic Cookware 10-Piece Set": "https://images.unsplash.com/photo-1584990347449-3995874c2bc0?w=600&auto=format&fit=crop&q=80",

    # Beauty & Personal Care
    "Hydrating Vitamin C + Hyaluronic Facial Serum": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=80",
    "Organic Herbal Daily Moisturizing Cream": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80",
    "Exfoliating Mineral Himalayan Body Scrub": "https://images.unsplash.com/photo-1608248597359-2e06180630b9?w=600&auto=format&fit=crop&q=80",
    "Nourishing Botanical Night Repair Elixir": "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=600&auto=format&fit=crop&q=80",
}

CATEGORY_FALLBACK_IMAGES = {
    "Electronics": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
    "Fashion": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600&auto=format&fit=crop&q=80",
    "Books": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
    "Home & Kitchen": "https://images.unsplash.com/photo-1584990347449-3995874c2bc0?w=600&auto=format&fit=crop&q=80",
    "Beauty & Personal Care": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=80",
    "Sports & Fitness": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80",
    "General": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
}

CATEGORY_ICONS = {
    "All": "🏷️",
    "All Categories": "🏷️",
    "Electronics": "📱",
    "Fashion": "👗",
    "Books": "📚",
    "Home & Kitchen": "🏠",
    "Beauty & Personal Care": "💄",
    "Sports & Fitness": "⚽",
    "Toys & Games": "🎮",
    "General": "🛍️",
}

THEME_CONFIGS = {
    "🛍️ ShopSense Hybrid (Flipkart + Amazon + Meesho)": {
        "primary": "#2874f0",
        "primary_dark": "#1a5ecc",
        "secondary": "#fb641b",
        "accent": "#ffd814",
        "bg": "#f1f3f6",
        "card_bg": "#ffffff",
        "text_main": "#212121",
        "text_muted": "#666666",
        "border": "#e0e0e0",
        "header_grad": "linear-gradient(135deg, #2874f0 0%, #1a5ecc 60%, #124090 100%)",
        "cta_grad": "linear-gradient(90deg, #fb641b 0%, #ff7e39 100%)",
        "cta_color": "#ffffff",
        "brand_badge": "⚡ ShopSense Assured",
        "brand_badge_bg": "#ffe11b",
        "brand_badge_color": "#2874f0",
    },
    "💙 Flipkart Blue Edition": {
        "primary": "#2874f0",
        "primary_dark": "#1259c7",
        "secondary": "#fb641b",
        "accent": "#ffe500",
        "bg": "#f1f3f6",
        "card_bg": "#ffffff",
        "text_main": "#212121",
        "text_muted": "#878787",
        "border": "#e4e7eb",
        "header_grad": "linear-gradient(90deg, #2874f0 0%, #1a64db 100%)",
        "cta_grad": "linear-gradient(90deg, #fb641b 0%, #ff782d 100%)",
        "cta_color": "#ffffff",
        "brand_badge": "⭐ Plus Assured",
        "brand_badge_bg": "#ffe500",
        "brand_badge_color": "#2874f0",
    },
    "📦 Amazon Prime Edition": {
        "primary": "#131921",
        "primary_dark": "#0c1017",
        "secondary": "#ffa41c",
        "accent": "#ffd814",
        "bg": "#eaeded",
        "card_bg": "#ffffff",
        "text_main": "#0f1111",
        "text_muted": "#565959",
        "border": "#d5d9d9",
        "header_grad": "linear-gradient(135deg, #131921 0%, #232f3e 100%)",
        "cta_grad": "linear-gradient(180deg, #ffd814 0%, #f7ca00 100%)",
        "cta_color": "#0f1111",
        "brand_badge": "✓prime Delivery",
        "brand_badge_bg": "#00a8e1",
        "brand_badge_color": "#ffffff",
    },
    "💖 Meesho Pink Edition": {
        "primary": "#9f2089",
        "primary_dark": "#6a0959",
        "secondary": "#f43397",
        "accent": "#ff6f00",
        "bg": "#fcf6fb",
        "card_bg": "#ffffff",
        "text_main": "#333333",
        "text_muted": "#757575",
        "border": "#f1e5ef",
        "header_grad": "linear-gradient(135deg, #540b51 0%, #9f2089 50%, #f43397 100%)",
        "cta_grad": "linear-gradient(90deg, #9f2089 0%, #bd2c97 100%)",
        "cta_color": "#ffffff",
        "brand_badge": "🛡️ Meesho Trusted",
        "brand_badge_bg": "#e5f7f1",
        "brand_badge_color": "#038d63",
    },
}

def get_product_image(product_name: str, category: str = "General") -> str:
    """Return high-resolution photo URL matching product or fallback category."""
    if product_name in PRODUCT_IMAGES:
        return PRODUCT_IMAGES[product_name]
    for key, url in PRODUCT_IMAGES.items():
        if key.lower() in product_name.lower() or product_name.lower() in key.lower():
            return url
    return CATEGORY_FALLBACK_IMAGES.get(category, CATEGORY_FALLBACK_IMAGES["General"])

def get_product_meta(product_id: int, price: float) -> Tuple[float, int, float, int]:
    """
    Deterministically derive ratings, review counts, MRP, and discount percentage
    to create an authentic e-commerce feel.
    """
    # Deterministic hash based on product_id
    h = int(hashlib.md5(str(product_id).encode()).hexdigest(), 16)
    rating = round(3.9 + (h % 11) * 0.1, 1)  # 3.9 to 4.9
    reviews_count = 120 + (h % 3400)
    discount_pct = 18 + (h % 35)             # 18% to 52%
    mrp = round(price / (1.0 - (discount_pct / 100.0)), 2)
    return rating, reviews_count, mrp, discount_pct

def generate_ecommerce_css(theme_name: str = "🛍️ ShopSense Hybrid (Flipkart + Amazon + Meesho)") -> str:
    """Generates the full CSS stylesheet for the selected e-commerce aesthetic."""
    cfg = THEME_CONFIGS.get(theme_name, THEME_CONFIGS["🛍️ ShopSense Hybrid (Flipkart + Amazon + Meesho)"])

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {{
    --ss-primary: {cfg["primary"]};
    --ss-primary-dark: {cfg["primary_dark"]};
    --ss-secondary: {cfg["secondary"]};
    --ss-accent: {cfg["accent"]};
    --ss-bg: {cfg["bg"]};
    --ss-card-bg: {cfg["card_bg"]};
    --ss-text-main: {cfg["text_main"]};
    --ss-text-muted: {cfg["text_muted"]};
    --ss-border: {cfg["border"]};
    --ss-header-grad: {cfg["header_grad"]};
    --ss-cta-grad: {cfg["cta_grad"]};
    --ss-cta-color: {cfg["cta_color"]};
    --ss-brand-badge-bg: {cfg["brand_badge_bg"]};
    --ss-brand-badge-color: {cfg["brand_badge_color"]};
    --ss-green: #388e3c;
    --ss-green-bg: #e8f5e9;
    --ss-amber: #e65100;
    --ss-amber-bg: #fff3e0;
    --ss-red: #d32f2f;
    --ss-red-bg: #ffebee;
}}

/* Global Typography & Background */
html, body, [class*="css"], .stApp {{
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--ss-bg) !important;
    color: var(--ss-text-main) !important;
}}

/* Top Padding Reset */
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 96% !important;
}}

/* Streamlit Header Bar */
header[data-testid="stHeader"] {{
    background-color: transparent !important;
}}

/* Top Brand Navigation Bar */
.ss-navbar {{
    background: var(--ss-header-grad);
    color: #ffffff;
    border-radius: 12px;
    padding: 14px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}}
.ss-navbar-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.ss-navbar-logo {{
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.ss-navbar-tagline {{
    font-size: 0.78rem;
    color: rgba(255,255,255,0.85);
    font-weight: 500;
    font-style: italic;
}}
.ss-navbar-pill {{
    background: rgba(255,255,255,0.18);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.25);
    color: #ffffff;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}
.ss-trust-ribbon {{
    display: flex;
    gap: 20px;
    align-items: center;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.95);
    font-weight: 600;
}}

/* Category Navigation Ribbon (Flipkart/Meesho style) */
.ss-category-ribbon {{
    background: var(--ss-card-bg);
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 22px;
    border: 1px solid var(--ss-border);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 8px;
}}
.ss-category-chip {{
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--ss-text-main);
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s ease;
}}
.ss-category-chip:hover {{
    background: var(--ss-primary);
    color: #ffffff;
    border-color: var(--ss-primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(40,116,240,0.25);
}}

/* Modern Product Card (Amazon / Flipkart / Meesho aesthetic) */
.ss-product-card {{
    background: var(--ss-card-bg);
    border-radius: 12px;
    border: 1px solid var(--ss-border);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    overflow: hidden;
    transition: all 0.25s cubic-bezier(0.165, 0.84, 0.44, 1);
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
    margin-bottom: 18px;
}}
.ss-product-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.12);
    border-color: var(--ss-primary);
}}
.ss-product-img-wrap {{
    width: 100%;
    height: 190px;
    background: #fafafa;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.ss-product-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.35s ease;
}}
.ss-product-card:hover .ss-product-img {{
    transform: scale(1.05);
}}
.ss-product-discount-tag {{
    position: absolute;
    top: 10px;
    left: 10px;
    background: #388e3c;
    color: #ffffff;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.3px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}}
.ss-product-brand-tag {{
    position: absolute;
    top: 10px;
    right: 10px;
    background: var(--ss-brand-badge-bg);
    color: var(--ss-brand-badge-color);
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 800;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
.ss-product-body {{
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}}
.ss-product-category {{
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--ss-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}}
.ss-product-title {{
    font-size: 0.98rem;
    font-weight: 700;
    color: var(--ss-text-main);
    line-height: 1.35;
    margin-bottom: 8px;
    min-height: 40px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.ss-product-rating-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}}
.ss-rating-pill {{
    background: #388e3c;
    color: #ffffff;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
}}
.ss-rating-count {{
    font-size: 0.78rem;
    color: var(--ss-text-muted);
    font-weight: 500;
}}
.ss-product-price-row {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 8px;
}}
.ss-price-current {{
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--ss-text-main);
}}
.ss-price-mrp {{
    font-size: 0.85rem;
    color: var(--ss-text-muted);
    text-decoration: line-through;
}}
.ss-price-save {{
    font-size: 0.82rem;
    font-weight: 700;
    color: #388e3c;
}}
.ss-delivery-info {{
    font-size: 0.78rem;
    color: #212121;
    font-weight: 600;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.ss-delivery-badge {{
    color: #388e3c;
    font-weight: 700;
}}
.ss-vendor-name {{
    font-size: 0.75rem;
    color: var(--ss-text-muted);
    margin-bottom: 12px;
}}

/* Metric Cards (Amazon Seller Central / Flipkart Seller Hub) */
div[data-testid="stMetric"] {{
    background-color: var(--ss-card-bg) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    border: 1px solid var(--ss-border) !important;
    border-top: 4px solid var(--ss-primary) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
div[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.08) !important;
}}
div[data-testid="stMetricLabel"] {{
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    color: var(--ss-text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}}
div[data-testid="stMetricValue"] {{
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: var(--ss-text-main) !important;
}}

/* Custom Pro Metric Cards */
.ss-kpi-card {{
    background: var(--ss-card-bg);
    border-radius: 12px;
    padding: 18px 22px;
    border: 1px solid var(--ss-border);
    border-left: 5px solid var(--ss-primary);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 14px;
}}
.ss-kpi-title {{
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--ss-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.ss-kpi-value {{
    font-size: 1.85rem;
    font-weight: 800;
    color: var(--ss-text-main);
    margin: 4px 0;
}}

/* Streamlit Buttons: Flipkart Orange / Amazon Amber / Meesho Pink */
.stButton > button {{
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 9px 18px !important;
    transition: all 0.2s ease !important;
}}
.stButton > button[kind="primary"], button[data-testid="baseButton-primary"] {{
    background: var(--ss-cta-grad) !important;
    color: var(--ss-cta-color) !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.15) !important;
}}
.stButton > button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.22) !important;
    filter: brightness(1.05);
}}
.stButton > button[kind="secondary"], button[data-testid="baseButton-secondary"] {{
    background: #ffffff !important;
    color: var(--ss-text-main) !important;
    border: 1px solid var(--ss-border) !important;
}}
.stButton > button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover {{
    border-color: var(--ss-primary) !important;
    color: var(--ss-primary) !important;
    background: #fdfdfd !important;
}}

/* Forms, Inputs and Selectboxes */
.stTextInput input, .stNumberInput input {{
    border-radius: 8px !important;
    border: 1.5px solid #d5d9d9 !important;
    padding: 10px 14px !important;
    background: #ffffff !important;
    font-size: 0.95rem !important;
}}
.stTextInput input:focus, .stNumberInput input:focus {{
    border-color: var(--ss-primary) !important;
    box-shadow: 0 0 0 3px rgba(40,116,240,0.2) !important;
}}
div[data-baseweb="select"] > div {{
    border-radius: 8px !important;
    border-color: #d5d9d9 !important;
    background-color: #ffffff !important;
}}

/* Status Badges */
.status-badge-active {{
    background-color: var(--ss-green-bg);
    color: var(--ss-green);
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.8rem;
    display: inline-block;
    border: 1px solid rgba(56, 142, 60, 0.2);
}}
.status-badge-pending {{
    background-color: var(--ss-amber-bg);
    color: var(--ss-amber);
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.8rem;
    display: inline-block;
    border: 1px solid rgba(230, 81, 0, 0.2);
}}
.status-badge-suspended {{
    background-color: var(--ss-red-bg);
    color: var(--ss-red);
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.8rem;
    display: inline-block;
    border: 1px solid rgba(211, 47, 47, 0.2);
}}

/* Sidebar Customization */
[data-testid="stSidebar"] {{
    background-color: #ffffff !important;
    border-right: 1px solid var(--ss-border) !important;
}}
.ss-sidebar-header {{
    background: var(--ss-header-grad);
    border-radius: 10px;
    padding: 16px;
    color: #ffffff;
    margin-bottom: 16px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}}
.ss-sidebar-user-card {{
    background: #f8f9fa;
    border-radius: 8px;
    padding: 12px 14px;
    border: 1px solid #e9ecef;
    margin-bottom: 14px;
}}

/* Clean Dataframes */
[data-testid="stDataFrame"] {{
    border-radius: 10px !important;
    border: 1px solid var(--ss-border) !important;
    background-color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}}

/* Auth Card (Amazon / Flipkart Sign-in) */
.ss-auth-wrapper {{
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid var(--ss-border);
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    padding: 28px;
    margin: 10px auto;
}}
.ss-auth-header {{
    text-align: center;
    margin-bottom: 24px;
}}
.ss-auth-trust-footer {{
    margin-top: 24px;
    padding-top: 18px;
    border-top: 1px solid #eee;
    font-size: 0.78rem;
    color: var(--ss-text-muted);
    text-align: center;
}}

/* Trust Footer */
.ss-footer {{
    margin-top: 40px;
    padding: 24px 16px;
    background: var(--ss-card-bg);
    border-radius: 12px;
    border: 1px solid var(--ss-border);
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}}
.ss-footer-item {{
    flex: 1;
    min-width: 180px;
}}
.ss-footer-icon {{
    font-size: 1.6rem;
    margin-bottom: 6px;
}}
.ss-footer-text {{
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--ss-text-main);
}}
.ss-footer-sub {{
    font-size: 0.75rem;
    color: var(--ss-text-muted);
}}
</style>
"""

def render_top_navbar(user_name: str, role: str, theme_name: str) -> str:
    """Returns HTML for Flipkart/Amazon/Meesho style top header bar."""
    cfg = THEME_CONFIGS.get(theme_name, THEME_CONFIGS["🛍️ ShopSense Hybrid (Flipkart + Amazon + Meesho)"])
    brand_badge = cfg["brand_badge"]
    
    role_display = {"CUSTOMER": "Shopper", "VENDOR": "Seller Hub", "ADMIN": "Admin Portal"}.get(role, role)

    return f"""
<div class="ss-navbar">
    <div class="ss-navbar-brand">
        <div>
            <div class="ss-navbar-logo">
                🛍️ ShopSense
                <span class="ss-navbar-pill" style="font-size:0.7rem; padding: 2px 8px; margin-left: 6px;">
                    {brand_badge}
                </span>
            </div>
            <div class="ss-navbar-tagline">
                India's Multi-Vendor Marketplace • Fastest Delivery Guaranteed
            </div>
        </div>
    </div>
    <div class="ss-trust-ribbon">
        <span class="ss-navbar-pill">📍 Deliver to Chiru - 560001</span>
        <span class="ss-navbar-pill">👤 {user_name} ({role_display})</span>
    </div>
</div>
"""

def render_category_ribbon(active_category: str = "All") -> str:
    """Returns HTML for the quick category ribbon bar."""
    categories = [
        ("All", "🏷️ All Deals"),
        ("Electronics", "📱 Electronics"),
        ("Fashion", "👗 Fashion"),
        ("Books", "📚 Books"),
        ("Home & Kitchen", "🏠 Home & Kitchen"),
        ("Beauty & Personal Care", "💄 Beauty & Grooming"),
    ]
    chips = []
    for cat_key, cat_label in categories:
        is_active = (active_category == cat_key or (active_category == "All Categories" and cat_key == "All"))
        active_style = 'style="background: var(--ss-primary); color: #ffffff; border-color: var(--ss-primary);"' if is_active else ""
        chips.append(f'<span class="ss-category-chip" {active_style}>{cat_label}</span>')
    
    return f"""
<div class="ss-category-ribbon">
    {''.join(chips)}
</div>
"""

def render_product_card_html(product: Dict[str, Any], theme_name: str) -> str:
    """Renders a complete Amazon/Flipkart/Meesho styled product card in HTML."""
    cfg = THEME_CONFIGS.get(theme_name, THEME_CONFIGS["🛍️ ShopSense Hybrid (Flipkart + Amazon + Meesho)"])
    
    p_id = product.get("product_id", 0)
    p_name = product.get("product_name", "Product")
    category = product.get("category", "General")
    price = float(product.get("price", 0.0))
    stock = int(product.get("stock", 0))
    vendor_disp = product.get("vendor_name") or f"Vendor #{product.get('vendor_id', '')}"
    
    img_url = get_product_image(p_name, category)
    rating, reviews, mrp, discount = get_product_meta(p_id, price)
    
    # Stock badge logic
    if stock == 0:
        stock_badge = '<span class="status-badge-suspended">Out of Stock</span>'
        delivery_tag = '<span style="color:#d32f2f; font-weight:700;">Currently Unavailable</span>'
    elif stock <= 5:
        stock_badge = f'<span class="status-badge-pending">Only {stock} Left in Stock</span>'
        delivery_tag = '<span class="ss-delivery-badge">⚡ Fastest Delivery</span> by Tomorrow'
    else:
        stock_badge = f'<span class="status-badge-active">In Stock ({stock})</span>'
        delivery_tag = '<span class="ss-delivery-badge">🚚 Free Delivery</span> by Tomorrow'
    
    save_amount = round(mrp - price, 2)
    
    return f"""
<div class="ss-product-card">
    <div class="ss-product-img-wrap">
        <img src="{img_url}" alt="{p_name}" class="ss-product-img" loading="lazy" />
        <span class="ss-product-discount-tag">{discount}% OFF</span>
        <span class="ss-product-brand-tag">{cfg["brand_badge"]}</span>
    </div>
    <div class="ss-product-body">
        <div class="ss-product-category">{category}</div>
        <div class="ss-product-title" title="{p_name}">{p_name}</div>
        <div class="ss-product-rating-row">
            <span class="ss-rating-pill">★ {rating}</span>
            <span class="ss-rating-count">({reviews:,} ratings)</span>
        </div>
        <div class="ss-product-price-row">
            <span class="ss-price-current">${price:,.2f}</span>
            <span class="ss-price-mrp">${mrp:,.2f}</span>
            <span class="ss-price-save">Save ${save_amount:,.2f}</span>
        </div>
        <div class="ss-delivery-info">
            {delivery_tag}
        </div>
        <div style="margin-bottom: 8px;">
            {stock_badge}
        </div>
        <div class="ss-vendor-name">
            Sold by: <strong>{vendor_disp}</strong> • 100% Original
        </div>
    </div>
</div>
"""

def render_order_card_html(order: Dict[str, Any], theme_name: str) -> str:
    """Renders an Amazon / Flipkart style order tracking item card."""
    tx_id = order.get("transaction_id", 0)
    p_name = order.get("product_name", "Product")
    v_name = order.get("vendor_name", "Vendor")
    qty = order.get("quantity", 1)
    amt = float(order.get("amount", 0.0))
    date_str = str(order.get("transaction_date", ""))
    img_url = get_product_image(p_name)

    return f"""
<div style="background:#ffffff; border-radius:10px; border:1px solid var(--ss-border); padding:16px; margin-bottom:14px; box-shadow:0 2px 6px rgba(0,0,0,0.04); display:flex; gap:16px; align-items:center; flex-wrap:wrap;">
    <img src="{img_url}" style="width:70px; height:70px; object-fit:cover; border-radius:8px; border:1px solid #eee;" alt="{p_name}" />
    <div style="flex-grow:1; min-width:200px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-size:0.78rem; color:var(--ss-text-muted); font-weight:600;">ORDER #{tx_id} • Placed on {date_str[:10]}</span>
            <span class="status-badge-active">✅ Order Confirmed</span>
        </div>
        <div style="font-size:1.05rem; font-weight:700; color:var(--ss-text-main); margin-bottom:4px;">{p_name}</div>
        <div style="font-size:0.82rem; color:var(--ss-text-muted);">Sold by: <strong>{v_name}</strong> | Quantity: <strong>{qty}</strong></div>
    </div>
    <div style="text-align:right; min-width:110px;">
        <div style="font-size:1.3rem; font-weight:800; color:var(--ss-text-main);">${amt:,.2f}</div>
        <div style="font-size:0.78rem; color:#388e3c; font-weight:700;">🚚 Free Express Delivery</div>
    </div>
</div>
"""

def render_customer_profile_card(user_name: str, user_email: str, role: str, theme_name: str) -> str:
    """Renders Flipkart Plus / Amazon Prime customer profile card."""
    cfg = THEME_CONFIGS.get(theme_name, THEME_CONFIGS["🛍️ ShopSense Hybrid (Flipkart + Amazon + Meesho)"])
    initial = user_name[0].upper() if user_name else 'U'
    return f"""
<div style="background:#ffffff; border-radius:12px; border:1px solid var(--ss-border); padding:24px; box-shadow:0 2px 10px rgba(0,0,0,0.05); margin-bottom:20px;">
    <div style="display:flex; align-items:center; gap:20px; flex-wrap:wrap;">
        <div style="width:68px; height:68px; border-radius:50%; background:var(--ss-header-grad); color:#ffffff; display:flex; align-items:center; justify-content:center; font-size:1.8rem; font-weight:800; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
            {initial}
        </div>
        <div style="flex-grow:1; min-width:200px;">
            <div style="font-size:1.4rem; font-weight:800; color:var(--ss-text-main);">{user_name}</div>
            <div style="font-size:0.88rem; color:var(--ss-text-muted); margin-top:2px;">📧 {user_email}</div>
            <div style="margin-top:8px; display:flex; gap:8px; align-items:center;">
                <span style="background:var(--ss-brand-badge-bg); color:var(--ss-brand-badge-color); font-weight:800; font-size:0.75rem; padding:3px 10px; border-radius:12px;">{cfg["brand_badge"]}</span>
                <span class="status-badge-active">Verified {role}</span>
            </div>
        </div>
        <div style="display:flex; gap:14px; text-align:center;">
            <div style="background:#f8f9fa; padding:12px 18px; border-radius:10px; border:1px solid var(--ss-border);">
                <div style="font-size:1.25rem; font-weight:800; color:var(--ss-primary);">🪙 250</div>
                <div style="font-size:0.75rem; color:var(--ss-text-muted); font-weight:700;">SuperCoins</div>
            </div>
            <div style="background:#f8f9fa; padding:12px 18px; border-radius:10px; border:1px solid var(--ss-border);">
                <div style="font-size:1.25rem; font-weight:800; color:#388e3c;">⚡ Free</div>
                <div style="font-size:0.75rem; color:var(--ss-text-muted); font-weight:700;">Delivery All Year</div>
            </div>
        </div>
    </div>
</div>
"""

def render_trust_footer() -> str:
    """Returns HTML for the bottom trust assurance footer like Amazon/Flipkart/Meesho."""
    return """
<div class="ss-footer">
    <div class="ss-footer-item">
        <div class="ss-footer-icon">🚚</div>
        <div class="ss-footer-text">Free & Fast Delivery</div>
        <div class="ss-footer-sub">On all orders across 19,000+ pin codes</div>
    </div>
    <div class="ss-footer-item">
        <div class="ss-footer-icon">🛡️</div>
        <div class="ss-footer-text">100% Genuine Products</div>
        <div class="ss-footer-sub">Verified multi-vendor marketplace sellers</div>
    </div>
    <div class="ss-footer-item">
        <div class="ss-footer-icon">🔄</div>
        <div class="ss-footer-text">7-Day Easy Returns</div>
        <div class="ss-footer-sub">Instant hassle-free refund process</div>
    </div>
    <div class="ss-footer-item">
        <div class="ss-footer-icon">🔒</div>
        <div class="ss-footer-text">Secure Payments</div>
        <div class="ss-footer-sub">256-Bit SSL Encrypted checkout</div>
    </div>
</div>
"""
