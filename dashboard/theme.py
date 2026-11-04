"""
ShopSense E-Commerce Theme Engine
Provides theme presets, dynamic CSS generation, and reusable marketplace UI components.
"""

from typing import Dict, Any, Tuple
import hashlib
import re

try:
    from app.inventory.exact_images import EXACT_PRODUCT_IMAGE_MAP
except Exception:
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from app.inventory.exact_images import EXACT_PRODUCT_IMAGE_MAP
    except Exception:
        EXACT_PRODUCT_IMAGE_MAP = {}

# Pexels CDN helper - works without referrer restrictions in Streamlit
def _px(photo_id: int) -> str:
    return f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w=600"

# Keyword-to-Image Matching using Pexels (loads reliably in Streamlit iframes)
PRODUCT_KEYWORD_PATTERNS = [
    # Electronics - most specific first
    (r"noise.cancell|over.ear.*head|wireless.*headphone|headphone|earphone|earbud", _px(3394650)),
    (r"bluetooth.*speaker|portable.*speaker|waterproof.*speaker|speaker",           _px(1706694)),
    (r"rgb.*keyboard|mechanical.*keyboard|gaming.*keyboard|keyboard",               _px(2115256)),
    (r"wireless.*mouse|ergonomic.*mouse|gaming.*mouse|mouse\b",                     _px(1037995)),
    (r"gan.*charg|65w.*charg|fast.*charg|wireless.*charg.*pad",                     _px(4526408)),
    (r"type-c.*cable|lightning.*cable|braided.*cable|usb.*cable",                   _px(4526418)),
    (r"thunderbolt|usb.*hub|usb-c.*hub|quad.*display",                              _px(4526430)),
    (r"webcam|web.*cam|streamer.*cam",                                               _px(4126743)),
    (r"smartwatch|fitness.*band|smart.*band|spO2|heart.*rate",                      _px(393047)),
    (r"gaming.*laptop|rtx.*laptop|gaming.*beast",                                   _px(777001)),
    (r"ultrabook|thin.*light.*laptop|slim.*laptop",                                 _px(7974681)),
    (r"laptop|notebook|study.*laptop|student.*laptop",                              _px(18105)),
    (r"5g.*flagship|flagship.*phone|prime.*pro",                                    _px(607812)),
    (r"smartphone|mobile.*phone|5g.*phone|amoled.*phone|iphone|samsung",           _px(1092644)),
    (r"power.*bank|portable.*charg.*bank",                                          _px(4526403)),
    (r"screen.*protect|tempered.*glass",                                            _px(404280)),
    (r"armor.*case|phone.*case|mobile.*case|shockproof.*case",                     _px(1034662)),
    (r"tripod|selfie.*stick",                                                       _px(1500355)),
    (r"car.*mount|car.*phone.*mount|magnetic.*mount",                               _px(5187260)),
    (r"flash.*drive|otg.*drive|usb.*drive|pendrive",                               _px(4526416)),
    (r"hdmi.*adapt|usb.*hdmi|display.*adapt",                                       _px(4526414)),
    (r"extension.*board|power.*strip|surge.*protect",                               _px(4526412)),
    (r"cooling.*pad|laptop.*cooler",                                                _px(5082579)),
    (r"laptop.*stand|aluminum.*stand|ergonomic.*stand",                             _px(1714208)),
    (r"laptop.*sleeve|laptop.*bag|neoprene.*sleeve",                                _px(1649771)),
    (r"robot.*vacuum|vacuum.*clean",                                                _px(3637786)),
    (r"wireless.*charg.*pad|charging.*pad",                                         _px(4526422)),
    (r"power.*adapter|multi.*pin.*adapter",                                         _px(4526427)),
    (r"numeric.*keypad|accountant.*keypad",                                         _px(1772973)),

    # Fashion - Ethnic / Indian wear (most specific first)
    (r"kurta|kurti|anarkali|chikankari|embroid.*kurti",                             _px(8285390)),
    (r"saree|banarasi.*silk|silk.*saree",                                           _px(1536619)),
    (r"palazzo|tunic.*set|palazzo.*tunic",                                          _px(8285357)),
    (r"nehru.*jacket|festive.*waistcoat|kurta.*pyjama",                             _px(1656684)),
    (r"linen.*kurta|casual.*kurta|cotton.*kurta",                                   _px(8285390)),

    # Fashion - Outerwear (before generic shirt/tshirt)
    (r"windbreaker|hooded.*outdoor.*jacket|waterproof.*jacket",                     _px(8386432)),
    (r"blazer|wool.*blend.*blazer|business.*blazer",                                _px(1656684)),
    (r"hoodie|zip.*up.*hoodie|fleece.*zip",                                         _px(6311423)),
    (r"waistcoat|cardigan|sweater",                                                 _px(1656684)),

    # Fashion - Tops
    (r"graphic.*t.shirt|round.*neck.*t|classic.*tee",                              _px(1043474)),
    (r"polo.*t.shirt|men.*polo|polo.*collar",                                       _px(9558738)),
    (r"sports.*bra|high.*support.*bra",                                             _px(4498481)),
    (r"blouse|embellish.*blouse|sleeveless.*top",                                   _px(3622574)),
    (r"nightwear|satin.*night|night.*set",                                          _px(6311417)),
    (r"women.*sweatshirt|trendy.*sweat|ladies.*sweat",                              _px(3622554)),
    (r"sweatshirt|crewneck.*sweat",                                                 _px(3622554)),

    # Fashion - Shirts
    (r"linen.*shirt|formal.*shirt|oxford.*shirt|button.*down.*shirt",              _px(297933)),
    (r"cotton.*shirt|casual.*shirt|regular.*fit.*shirt",                            _px(3622608)),
    (r"shirt\b",                                                                    _px(297933)),

    # Fashion - Jeans / Trousers
    (r"ripped.*jean|skinny.*jean|distressed.*denim",                               _px(4210858)),
    (r"denim.*jean|jeans\b|denim\b",                                               _px(1598507)),
    (r"chino|flat.*front.*trouser|formal.*trouser",                                 _px(4210851)),
    (r"jogger|trackpant|track.*pant|sweatpant",                                     _px(8386434)),
    (r"compression.*tight|active.*tight|sports.*tight",                             _px(8386440)),

    # Fashion - Women dresses
    (r"midi.*dress|wrap.*dress|chiffon.*dress|floral.*dress",                       _px(1536619)),
    (r"jegging|high.*rise.*slim.*fit",                                              _px(1598505)),

    # Footwear
    (r"running.*shoes|mesh.*running|lightweight.*running",                          _px(2529148)),
    (r"canvas.*sneaker|low.*top.*canvas|classic.*sneaker",                          _px(1598508)),
    (r"oxford.*shoe|derby.*shoe|formal.*oxford|leather.*formal.*shoe",             _px(336372)),
    (r"trekking|hiking.*boot|waterproof.*boot",                                     _px(1456706)),
    (r"flip.*flop|chappal|daily.*wear.*slipp",                                      _px(1598506)),
    (r"block.*heel|party.*pump|embellish.*pump|heels\b",                            _px(3622555)),
    (r"loafer|slip.*on.*women|women.*loafer",                                       _px(1598509)),
    (r"sandal|strappy.*flat|flat.*sandal",                                          _px(1458492)),
    (r"slide|eva.*slide|slip.*on.*slide",                                           _px(3622560)),
    (r"sports.*shoes|velcro.*sport|men.*sport.*shoe",                               _px(2529148)),
    (r"shoes\b|boots\b",                                                            _px(2529148)),

    # Fashion Accessories
    (r"bifold.*wallet|leather.*wallet|casual.*wallet|wallet\b",                     _px(1152077)),
    (r"braided.*belt|leather.*belt|reversible.*belt|belt\b",                        _px(1152078)),
    (r"aviator|polarized.*sunglass|uv400.*sunglass|sunglasses\b",                   _px(1572387)),
    (r"canvas.*backpack|everyday.*backpack|casual.*backpack|backpack\b",            _px(1553793)),
    (r"stainless.*watch|analog.*watch|classic.*watch|watch\b",                     _px(190819)),
    (r"boxer.*short|men.*boxer|underwear",                                          _px(8386438)),

    # Home Appliances
    (r"microwave|grill.*oven",                                                      _px(5824569)),
    (r"juicer|centrifugal.*juicer",                                                 _px(4397290)),
    (r"mixer.*grinder|wet.*grinder",                                                _px(1640777)),
    (r"air.*fryer|digital.*air.*fryer",                                             _px(5946476)),
    (r"electric.*kettle|glass.*kettle|cordless.*kettle",                            _px(4397293)),
    (r"air.*purifier|hepa.*purifier",                                               _px(4397297)),
    (r"tower.*fan|ceiling.*fan|speed.*fan|fan\b",                                   _px(4397300)),
    (r"steam.*iron|anti.*drip.*iron|iron\b",                                        _px(4397303)),
    (r"water.*purifier|ro.*uv|reverse.*osmosis",                                    _px(4397306)),
    (r"water.*dispenser|hot.*cold.*dispenser",                                      _px(4397309)),
    (r"car.*washer|pressure.*washer|high.*pressure.*spray",                         _px(4397312)),
    (r"mosquito.*trap|insect.*killer|trapper.*lamp",                                _px(4397315)),

    # Kitchen
    (r"cookware.*set|non.*stick.*set|tawa.*set|induction.*cookware|granito",       _px(4397320)),
    (r"pressure.*cooker|induction.*cooker",                                         _px(4397323)),
    (r"cast.*iron.*skillet|skillet|griller\b",                                      _px(4397326)),
    (r"knife.*set|kitchen.*knife",                                                  _px(4397329)),
    (r"spatula|silicone.*utensil|cooking.*utensil",                                 _px(4397332)),
    (r"vegetable.*chopper|5-in-1.*chopper|dicer",                                   _px(4397335)),
    (r"food.*storage|airtight.*container|bpa.*free",                               _px(4397338)),
    (r"dish.*rack|drying.*rack",                                                    _px(4397341)),
    (r"aroma.*diffuser|ultrasonic.*diffuser|essential.*oil.*diffus",               _px(4397344)),
    (r"water.*bottle|insulated.*bottle|stainless.*bottle",                          _px(4397347)),

    # Furniture
    (r"mesh.*office.*chair|ergonomic.*chair|high.*back.*mesh|high.*back.*desk",    _px(1957478)),
    (r"armchair|velvet.*arm|velvet.*chair",                                         _px(1866149)),
    (r"recliner|sofa.*chair|foldable.*recliner",                                    _px(1866149)),
    (r"writing.*desk|study.*desk|solid.*wood.*desk",                               _px(1957477)),
    (r"dining.*table|glass.*top.*dining|extendable.*table",                        _px(1350789)),
    (r"tv.*unit|entertainment.*unit|floating.*tv",                                  _px(1350790)),
    (r"fabric.*sofa|3-seater.*sofa|sofa.*ottoman|sofa\b",                           _px(1350789)),
    (r"bed.*frame|platform.*bed|upholster.*bed|queen.*bed",                         _px(1350788)),
    (r"bedsheet|cotton.*bedsheet|reversible.*bedsheet",                             _px(1350787)),
    (r"pillow|memory.*foam.*pillow",                                                _px(1350786)),
    (r"wardrobe|sliding.*wardrobe|4-door.*wardrobe",                               _px(1350785)),
    (r"shoe.*rack|3-tier.*rack|wooden.*shoe.*rack",                                 _px(1350784)),
    (r"chair\b|desk.*chair|office.*chair",                                          _px(1957478)),
    (r"table\b|dining\b|desk\b",                                                   _px(1350789)),
    (r"bed\b",                                                                      _px(1350788)),

    # Beauty & Personal Care
    (r"vitamin.*c.*serum|brightening.*serum|hyaluronic.*serum",                     _px(3685523)),
    (r"niacinamide|pore.*minimiz|zinc.*serum",                                      _px(3685525)),
    (r"face.*wash|foaming.*face|salicylic.*face",                                   _px(3685521)),
    (r"moisturizing.*cream|ceramide|peptide.*cream|moisturizer",                    _px(3685519)),
    (r"sunscreen|spf.*50|sun.*gel|sun.*protect",                                    _px(3685517)),
    (r"body.*scrub|papaya.*scrub|brightening.*scrub",                               _px(3685515)),
    (r"shampoo|keratin.*shampoo|anti.*frizz.*shampoo",                              _px(3735969)),
    (r"hair.*oil|bhringraj|hair.*growth.*oil",                                      _px(3735965)),
    (r"hair.*straightener|ceramic.*straightener|ionic.*straight",                   _px(3735961)),
    (r"lipstick|bullet.*lip|matte.*lip",                                            _px(3735957)),
    (r"beard.*oil|beard.*soften|jojoba.*beard",                                     _px(3735953)),
    (r"serum\b",                                                                    _px(3685523)),
    (r"lotion\b|cream\b|skin.*care",                                               _px(3685519)),

    # Grocery
    (r"basmati.*rice|royal.*basmati|aged.*rice|rice\b",                             _px(1537538)),
    (r"toor.*dal|arhar.*dal|lentil|dal\b",                                          _px(1640776)),
    (r"mustard.*oil|kachi.*ghani",                                                  _px(1640775)),
    (r"desi.*ghee|a2.*ghee|cow.*ghee|ghee\b",                                      _px(1640774)),
    (r"wild.*honey|forest.*honey|raw.*honey|honey\b",                              _px(1640773)),
    (r"california.*almond|almond\b",                                                _px(1640772)),
    (r"cashew.*nut|roasted.*cashew|kaju",                                           _px(1640771)),
    (r"peanut.*butter|dark.*choc.*peanut",                                          _px(1640770)),
    (r"black.*tea|ctc.*tea|assam.*tea|chai\b|tea\b",                               _px(1640769)),
    (r"filter.*coffee|south.*indian.*coffee|ground.*coffee|coffee\b",              _px(1640768)),
    (r"oil\b|cooking.*oil",                                                         _px(1640775)),
    (r"ghee\b",                                                                     _px(1640774)),

    # Sports & Fitness
    (r"rubber.*dumbbell|dumbbell.*set|adjustable.*dumbbell|dumbbell\b",            _px(1552252)),
    (r"yoga.*mat|eva.*yoga|non.*slip.*mat",                                         _px(4056535)),
    (r"pull.*up.*bar|doorway.*bar|chin.*up.*bar",                                   _px(1552253)),
    (r"resistance.*band|loop.*band|exercise.*band",                                 _px(4056538)),
    (r"skipping.*rope|jump.*rope|speed.*rope",                                      _px(4056541)),
    (r"gym.*gloves|weightlifting.*gloves|padded.*gloves",                           _px(4056544)),
    (r"massage.*roller|foam.*roller|roller.*stick",                                 _px(4056547)),
    (r"badminton.*racket|carbon.*fiber.*racket|racket\b",                           _px(4056550)),
    (r"protein.*shaker|gym.*shaker|shaker.*bottle",                                 _px(4056553)),
    (r"hydration.*pack|hydropack|running.*backpack",                                _px(4056556)),

    # Books
    (r"atomic.*habit|high.*performance.*habit",                                     _px(4170448)),
    (r"psychology.*wealth|financial.*freedom",                                      _px(4170451)),
    (r"data.*struct|algorithm.*easy|python.*algo",                                  _px(4170454)),
    (r"machine.*learning|deep.*learning|ml.*guide",                                 _px(4170457)),
    (r"fastapi|react.*microservice",                                                _px(4170460)),
    (r"database.*internal|distributed.*system",                                     _px(4170463)),
    (r"clean.*code|enterprise.*system",                                             _px(4170466)),
    (r"cloud.*architect|docker.*microservice",                                      _px(4170469)),
    (r"indian.*polity|governance.*exam|upsc",                                       _px(4170472)),
    (r"ancient.*indian|heritage.*architect",                                        _px(4170475)),
    (r"book\b|novel\b|handbook\b|blueprint\b|guide\b",                             _px(4170448)),
]

# Legacy dictionary retained for direct exact-name lookups
PRODUCT_IMAGES = {}

CATEGORY_FALLBACK_IMAGES = {
    "Electronics":          _px(3394650),
    "Mobiles":              _px(607812),
    "Laptops":              _px(18105),
    "Accessories":          _px(393047),
    "Fashion":              _px(1043474),
    "Men's Clothing":       _px(1043474),
    "Women's Clothing":     _px(8285390),
    "Footwear":             _px(2529148),
    "Books":                _px(4170448),
    "Home & Kitchen":       _px(5824569),
    "Home Appliances":      _px(5824569),
    "Furniture":            _px(1957478),
    "Kitchen Products":     _px(4397320),
    "Beauty & Personal Care": _px(3685523),
    "Sports & Fitness":     _px(1552252),
    "Grocery":              _px(1537538),
    "General":              _px(1043474),
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

DEFAULT_THEME = "🛍️ ShopSense Modern (Default)"

THEME_CONFIGS = {
    "🛍️ ShopSense Modern (Default)": {
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
    "💙 Royal Blue Edition": {
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
        "brand_badge": "⭐ ShopSense Plus",
        "brand_badge_bg": "#ffe500",
        "brand_badge_color": "#2874f0",
    },
    "📦 Dark Slate Edition": {
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
        "brand_badge": "✓ Express Delivery",
        "brand_badge_bg": "#00a8e1",
        "brand_badge_color": "#ffffff",
    },
    "💖 Vibrant Magenta Edition": {
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
        "brand_badge": "🛡️ Verified Seller",
        "brand_badge_bg": "#e5f7f1",
        "brand_badge_color": "#038d63",
    },
}

def get_theme_config(theme_name: str) -> Dict[str, Any]:
    """Safely retrieves theme configuration with backward-compatible fallback."""
    if theme_name in THEME_CONFIGS:
        return THEME_CONFIGS[theme_name]
    legacy_map = {
        "🛍️ ShopSense Hybrid (Flipkart + Amazon + Meesho)": "🛍️ ShopSense Modern (Default)",
        "💙 Flipkart Blue Edition": "💙 Royal Blue Edition",
        "📦 Amazon Prime Edition": "📦 Dark Slate Edition",
        "💖 Meesho Pink Edition": "💖 Vibrant Magenta Edition",
    }
    resolved = legacy_map.get(theme_name, DEFAULT_THEME)
    return THEME_CONFIGS.get(resolved, THEME_CONFIGS[DEFAULT_THEME])

def get_product_image(product_name: str, category: str = "General", image_url: str = None) -> str:
    """Return high-resolution photo URL specifically matched to the product title, image_url, or category."""
    # 0. If direct image_url is provided and valid, use it first (DB values take priority)
    if image_url and isinstance(image_url, str) and image_url.strip().startswith("http"):
        return image_url.strip()

    if not product_name:
        return CATEGORY_FALLBACK_IMAGES.get(category, CATEGORY_FALLBACK_IMAGES.get("General", _px(1043474)))

    # Strip vendor edition suffixes: (Apex Edition), (Aura Edition), (Heritage Edition), etc.
    base_name = re.sub(r"\s*\([^)]*Edition\)", "", product_name).strip()
    base_name = re.sub(r"\s*\([^)]*\)\s*$", "", base_name).strip()

    # 1. Exact match in inventory map (old system - kept for compatibility)
    if product_name in EXACT_PRODUCT_IMAGE_MAP:
        return EXACT_PRODUCT_IMAGE_MAP[product_name]
    if base_name in EXACT_PRODUCT_IMAGE_MAP:
        return EXACT_PRODUCT_IMAGE_MAP[base_name]

    # 2. Check legacy dictionary match if any
    if product_name in PRODUCT_IMAGES:
        return PRODUCT_IMAGES[product_name]

    # 3. Check keyword regex patterns against base title (Pexels-based)
    name_clean = base_name.lower()
    for pattern, url in PRODUCT_KEYWORD_PATTERNS:
        if re.search(pattern, name_clean):
            return url

    # 4. Check keyword regex patterns against raw title
    raw_clean = product_name.lower().strip()
    for pattern, url in PRODUCT_KEYWORD_PATTERNS:
        if re.search(pattern, raw_clean):
            return url

    # 5. Category Fallback
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

def generate_ecommerce_css(theme_name: str = DEFAULT_THEME) -> str:
    """Generates the full CSS stylesheet for the selected e-commerce aesthetic."""
    cfg = get_theme_config(theme_name)

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

/* Category Navigation Ribbon */
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

/* Modern Product Card */
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
    background: #ffffff;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    box-sizing: border-box;
}}
.ss-product-img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
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

/* Metric Cards (Seller Hub / Analytics Portal) */
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

/* Streamlit Action Buttons */
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

/* Auth Card (Clean Sign-in) */
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
    """Returns HTML for top brand navigation bar."""
    cfg = get_theme_config(theme_name)
    brand_badge = cfg["brand_badge"]
    
    role_map = {"CUSTOMER": "Customer", "VENDOR": "Vendor", "ADMIN": "Admin"}
    role_display = role_map.get(role, str(role))

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
    """Renders a complete modern product card in HTML."""
    cfg = get_theme_config(theme_name)
    
    p_id = product.get("product_id", 0)
    p_name = product.get("product_name", "Product")
    category = product.get("category", "General")
    price = float(product.get("price", 0.0))
    stock = int(product.get("stock", 0))
    vendor_disp = product.get("vendor_name") or f"Vendor #{product.get('vendor_id', '')}"
    p_image = product.get("image_url")
    
    img_url = get_product_image(p_name, category, image_url=p_image)
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
    """Renders an order tracking item card."""
    tx_id = order.get("transaction_id", 0)
    p_name = order.get("product_name", "Product")
    v_name = order.get("vendor_name", "Vendor")
    qty = order.get("quantity", 1)
    amt = float(order.get("amount", 0.0))
    date_str = str(order.get("transaction_date", ""))
    img_url = get_product_image(p_name, image_url=order.get("image_url"))

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

def render_customer_profile_card(user_name: str, user_email: str, role: str, theme_name: str, phone: str = None) -> str:
    """Renders customer profile card."""
    cfg = get_theme_config(theme_name)
    initial = user_name[0].upper() if user_name else 'U'
    phone_html = f"<div style='font-size:0.88rem; color:var(--ss-text-muted); margin-top:2px;'>📞 {phone}</div>" if phone else ""
    return f"""
<div style="background:#ffffff; border-radius:12px; border:1px solid var(--ss-border); padding:24px; box-shadow:0 2px 10px rgba(0,0,0,0.05); margin-bottom:20px;">
    <div style="display:flex; align-items:center; gap:20px; flex-wrap:wrap;">
        <div style="width:68px; height:68px; border-radius:50%; background:var(--ss-header-grad); color:#ffffff; display:flex; align-items:center; justify-content:center; font-size:1.8rem; font-weight:800; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
            {initial}
        </div>
        <div style="flex-grow:1; min-width:200px;">
            <div style="font-size:1.4rem; font-weight:800; color:var(--ss-text-main);">{user_name}</div>
            <div style="font-size:0.88rem; color:var(--ss-text-muted); margin-top:2px;">📧 {user_email}</div>
            {phone_html}
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
    """Returns HTML for the bottom trust assurance footer."""
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
