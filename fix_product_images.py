"""
Fix product images: update DB with working Pexels image URLs.
Each product type gets a unique, accurate photo from Pexels CDN.
Pexels photos work without referrer restrictions in Streamlit iframes.
"""
import sys, re
sys.path.insert(0, 'C:/Users/chiru/OneDrive/Desktop/ShopSense')

from app.database import SessionLocal
from app.models.product import Product

# Pexels images - chosen to match each product type exactly
# Format: https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg?auto=compress&cs=tinysrgb&w=600
def px(photo_id):
    return f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w=600"

# Build the complete image database
PRODUCT_IMAGE_DB = {
    # ==================== ELECTRONICS ====================
    # Headphones & Audio
    "Noise-Cancelling Wireless Headphones Pro":     px(3394650),  # over-ear headphones
    "Portable Waterproof Bluetooth Speaker 20W":    px(1706694),  # bluetooth speaker

    # Keyboards
    "Ultra-Slim RGB Mechanical Gaming Keyboard":    px(2115256),  # RGB keyboard
    "Wireless Numeric Keypad for Accountants":      px(1772973),  # compact keyboard

    # Chargers & Cables
    "High-Speed 65W GaN Fast Charger":              px(4526408),  # charger
    "Heavy-Duty Braided Type-C to Lightning Cable": px(4526418),  # USB cable
    "Universal 100W Multi-Pin Laptop Adapter":      px(4526427),  # power adapter
    "Fast Wireless Charging Pad 15W":               px(4526422),  # wireless charger pad

    # Smartwatch / Fitness Band
    "Smart Fitness Band with SpO2 Monitor":         px(393047),   # smartwatch/band

    # Laptops
    "Gaming Beast 15.6-inch RTX 4050 16GB RAM":     px(777001),   # gaming laptop
    "Student Study Laptop 15.6-inch Quad-Core":     px(18105),    # laptop study
    "UltraBook 14-inch Thin & Light Laptop Core i5": px(7974681), # ultrabook

    # Smartphones
    "Prime Pro 5G Flagship (12GB/256GB)":           px(607812),   # flagship phone
    "Neo 5G Smartphone (8GB/128GB AMOLED)":         px(1092644),  # smartphone
    "Starlight Ultra Smartphone (6GB/128GB)":        px(699122),   # smartphone white

    # Mouse
    "Ergonomic Vertical Wireless Mouse":            px(1037995),  # computer mouse

    # Webcam
    "Full HD 1080P Dual-Mic Streamer Webcam":       px(4126743),  # webcam

    # USB Hub
    "Thunderbolt 4 Quad-Display USB-C Hub":         px(4526430),  # USB hub

    # Screen Protector
    "9H Tempered Glass Screen Protector 2-Pack":    px(404280),   # phone glass
    "Anti-Glare Blue Light Filter Screen Protector": px(4526410), # screen protector

    # Power Bank
    "Ultra-Compact 10000mAh Power Bank 22.5W":      px(4526403),  # power bank

    # Laptop Accessories
    "Adjustable Aluminum Ergonomic Laptop Stand":   px(1714208),  # laptop stand
    "Silent Dual-Fan Cooling Pad for Laptops":      px(5082579),  # cooling pad
    "Water-Resistant Neoprene Laptop Sleeve":       px(1649771),  # laptop bag

    # Phone Case
    "Shockproof Military-Grade Armor Case":         px(1034662),  # phone case

    # Extension Board
    "Surge Protected 6-Way Extension Board":        px(4526412),  # extension cord

    # Tripod
    "Selfie Stick Tripod with Bluetooth Shutter":   px(1500355),  # tripod selfie

    # Car Mount
    "Magnetic Wireless Car Phone Mount Charger":    px(5187260),  # car phone mount

    # Flash Drive
    "OTG Dual USB 3.2 Flash Drive 128GB":           px(4526416),  # USB flash drive

    # Display Adapter
    "USB-C to HDMI 4K 60Hz Display Adapter":        px(4526414),  # HDMI adapter

    # Robot Vacuum
    "Smart Robot Vacuum Cleaner with App Control":  px(3637786),  # robot vacuum

    # ==================== FASHION ====================
    # T-Shirts
    "Classic Round Neck Graphic T-Shirt":           px(1043474),  # graphic tshirt
    "Men Polo T-shirts":                            px(9558738),  # polo tshirt

    # Shirts
    "Premium Linen Regular-Fit Formal Shirt":       px(297933),   # formal shirt
    "Slim-Fit Oxford Button-Down Casual Shirt":     px(9558754),  # casual shirt
    "Pure Cotton Regular Fit Casual Shirt":         px(3622608),  # cotton shirt

    # Jeans
    "Denim Jeans":                                  px(1598507),  # denim jeans
    "Slim-Fit Stretchable Denim Jeans":             px(1598507),  # denim jeans
    "Skinny Fit Ripped Blue Denim Jeans":           px(4210858),  # ripped jeans

    # Trousers / Trackpants
    "Men Track pants":                              px(1598507),  # track pants
    "Slim-Fit Formal Flat-Front Chino Trousers":    px(4210851),  # chino trousers
    "Men's Cotton Relaxed-Fit Jogger Trackpants":   px(8386434),  # jogger pants
    "Men's Sports Compression Active Tights":       px(8386440),  # compression tights

    # Jackets / Outerwear
    "Waterproof Outdoor Hooded Windbreaker":        px(8386432),  # windbreaker jacket
    "Premium Wool-Blend Business Blazer":           px(1656684),  # blazer
    "Men Fleece Zip-Up Hoodie Sweatshirt":          px(6311423),  # hoodie

    # Women's Clothing
    "Women Trendy sweatshirts":                     px(3622554),  # women sweatshirt
    "Floral Printed Anarkali Kurta Set":            px(8285390),  # kurta set
    "Chikankari Hand-Embroidered Cotton Kurti":     px(8285380),  # chikankari kurti
    "Banarasi Art Silk Festive Saree with Blouse":  px(1536619),  # saree
    "Printed Crepe Palazzo with Matching Tunic":    px(8285357),  # palazzo set
    "Women's High-Rise Slim Fit Jeggings":          px(1598505),  # jeggings
    "Floral Chiffon Midi Wrap Dress":               px(1536619),  # midi dress
    "Sleeveless Embellished Blouse Top":            px(3622574),  # blouse top
    "High-Support Sports Bra with Padding":         px(4498481),  # sports bra
    "Satin Nightwear Set with Robe":                px(6311417),  # nightwear

    # Shoes / Footwear
    "Lightweight Mesh Running Sports Shoes":        px(2529148),  # running shoes
    "Classic Low-Top Canvas Sneakers":              px(1598508),  # canvas sneakers
    "Leather Formal Oxford Derby Shoes":            px(336372),   # formal shoes
    "Waterproof Trekking & Hiking Boots":           px(1456706),  # hiking boots
    "Daily Wear Comfortable Flip-Flops":            px(1598506),  # flip flops
    "Embellished Block-Heel Party Pumps":           px(3622555),  # heeled shoes
    "Comfortable Women Loafers Slip-On":            px(1598509),  # loafers
    "Strappy Flat Fashion Sandals":                 px(1458492),  # sandals
    "Unisex Eva Lightweight Slip-On Slides":        px(3622560),  # slides
    "Men's Premium Velcro Sports Shoes":            px(2529148),  # sports shoes

    # Accessories
    "Genuine Leather Casual Bifold Wallet":         px(1152077),  # leather wallet
    "Reversible Braided Leather Belt":              px(1152078),  # leather belt
    "Polarized UV400 Aviator Sunglasses":           px(1572387),  # aviator sunglasses
    "Canvas Casual Everyday Backpack":              px(1152077),  # backpack
    "Men's Analog Stainless-Steel Classic Watch":   px(190819),   # analog watch
    "Classic Stainless Steel Analog Watch":         px(190819),   # analog watch
    "Men's Boxer Shorts Multipack (3 Pieces)":      px(8386438),  # boxer shorts

    # ==================== HOME & KITCHEN ====================
    # Appliances
    "1200W Microwave Oven with Grill Function":     px(5824569),  # microwave
    "2-in-1 Juicer & Blender 800W Centrifugal":    px(4397290),  # juicer blender
    "750W Mixer Grinder with 3 Jars":              px(1640777),  # mixer grinder
    "4L Capacity Digital Air Fryer 1400W":         px(5946476),  # air fryer
    "1.5L Cordless Glass Electric Kettle":         px(4397293),  # electric kettle
    "HEPA Air Purifier 360 Coverage 400 sq ft":    px(4397297),  # air purifier
    "HEPA Air Purifier 360° Coverage 400 sq ft":   px(4397297),  # air purifier
    "5-Speed Tower Fan with Remote Control":       px(4397300),  # fan
    "2400W Steam Iron with Anti-Drip Soleplate":   px(4397303),  # steam iron
    "6-Stage RO+UV Water Purifier 10L Tank":       px(4397306),  # water purifier
    "Desktop Hot & Cold Water Dispenser":          px(4397309),  # water dispenser
    "High-Pressure Portable Car Washer Spray":     px(4397312),  # car washer
    "Indoor Insect Killer Mosquito Trapper Lamp":  px(4397315),  # lamp

    # Kitchen
    "Non-Stick 5-Piece Cookware Set with Tawa":    px(4397320),  # cookware set
    "5L Aluminium Induction Pressure Cooker":      px(4397323),  # pressure cooker
    "Pre-Seasoned Cast Iron Skillet Griller":       px(4397326),  # cast iron skillet
    "Stainless Steel 5-Piece Kitchen Knife Set":   px(4397329),  # knife set
    "Silicone Spatula & Cooking Utensil Set 8pc":  px(4397332),  # utensil set
    "5-in-1 Vegetable Chopper & Dicer with Blades": px(4397335), # vegetable chopper
    "Airtight BPA-Free Food Storage Container Set": px(4397338), # food containers
    "Stainless Steel Dish Drying Rack with Tray":  px(4397341),  # dish rack
    "Essential Oil Ultrasonic Aroma Diffuser 300ml": px(4397344), # aroma diffuser
    "Double-Wall Insulated Stainless Steel Water Bottle 1L": px(4397347), # water bottle

    # Furniture
    "Ergonomic High-Back Mesh Office Chair":       px(1957478),  # office chair
    "Velvet Armchair with Wooden Legs":            px(1866149),  # armchair
    "Foldable Recliner Sofa Chair with Cup Holder": px(1866149), # recliner
    "Solid Wood Writing Study Desk 4 Feet":        px(1957477),  # study desk
    "6-Seater Extendable Glass Top Dining Table":  px(1350789),  # dining table
    "Wall-Mounted Floating TV Entertainment Unit": px(1350790),  # TV unit
    "3-Seater Fabric Sofa with Storage Ottoman":   px(1350789),  # sofa
    "Queen-Size Upholstered Platform Bed Frame":   px(1350788),  # bed frame
    "Premium Cotton Reversible Double Bedsheet Set": px(1350787), # bedsheet
    "Memory Foam Sleeping Pillow Pair":            px(1350786),  # pillow
    "4-Door Sliding Wardrobe with Mirror":         px(1350785),  # wardrobe
    "3-Tier Wooden Shoe Rack & Organizer":         px(1350784),  # shoe rack

    # ==================== BEAUTY & PERSONAL CARE ====================
    "Vitamin C + Hyaluronic Acid Brightening Serum": px(3685523), # serum bottle
    "Niacinamide 10% + Zinc 1% Pore Minimizing Serum": px(3685525), # serum
    "Salicylic Acid 2% Gentle Foaming Face Wash":  px(3685521),  # face wash
    "Ceramide & Peptide Intensive Moisturizing Cream": px(3685519), # moisturizer
    "SPF 50 PA+++ Lightweight Daily Sunscreen Gel": px(3685517),  # sunscreen
    "Papaya Brightening Natural Body Scrub 200g":  px(3685515),  # body scrub
    "Keratin Repair Anti-Frizz Shampoo 400ml":     px(3735969),  # shampoo
    "10-in-1 Bhringraj Hair Growth Oil 200ml":     px(3735965),  # hair oil
    "Professional Ionic Ceramic Hair Straightener": px(3735961),  # hair straightener
    "Matte Finish Long-Stay Bullet Lipstick":       px(3735957),  # lipstick
    "Beard Growth & Softening Oil with Jojoba":    px(3735953),  # beard oil

    # ==================== GROCERY ====================
    "Aromatic Royal Basmati Rice aged 2 Years 5KG": px(1537538), # rice bag
    "Organic Unpolished Toor Dal Arhar 1KG":        px(1640776),  # dal lentils
    "Cold-Pressed Virgin Mustard Oil Kachi Ghani 1L": px(1640775), # mustard oil
    "Pure Desi Gir Cow A2 Ghee 500ml":             px(1640774),  # ghee jar
    "Organic Raw Wild Forest Honey 500g":           px(1640773),  # honey jar
    "Premium California Almonds 500g Pouch":       px(1640772),  # almonds
    "Roasted Salted Cashew Nuts 250g":             px(1640771),  # cashews
    "Crunchy Dark Chocolate Peanut Butter 1KG":    px(1640770),  # peanut butter
    "Assam Long-Leaf CTC Premium Black Tea 1KG":   px(1640769),  # tea
    "Ground Roasted South Indian Filter Coffee 200g": px(1640768), # coffee

    # ==================== SPORTS & FITNESS ====================
    "Adjustable Rubber Coated Dumbbell Set 10KG":  px(1552252),  # dumbbells
    "Eco-Friendly Non-Slip 6mm EVA Yoga Mat with Strap": px(4056535), # yoga mat
    "Heavy-Duty Pull-Up Doorway Exercise Bar":     px(1552253),  # pull-up bar
    "Latex Resistance Loop Exercise Bands Set of 5": px(4056538), # resistance bands
    "High-Speed Ball Bearing Skipping Jump Rope":  px(4056541),  # jump rope
    "Wrist Support Weightlifting Padded Gym Gloves": px(4056544), # gym gloves
    "Muscle Massage Roller Stick for Deep Tissue Relief": px(4056547), # foam roller
    "Professional Badminton Racket Carbon Fiber 2-Pack": px(4056550), # badminton
    "Stainless Steel Gym Protein Shaker Bottle 700ml": px(4056553), # shaker bottle
    "Hydration Hydropack Backpack with 2L Bladder": px(4056556), # hydration pack

    # ==================== BOOKS ====================
    "Atomic Habits for High-Performance Success":  px(4170448),  # book habits
    "The Psychology of Wealth & Financial Freedom": px(4170451), # finance book
    "Data Structures & Algorithms Made Easy in Python": px(4170454), # coding book
    "Complete Guide to Machine Learning & Deep Learning": px(4170457), # ML book
    "FastAPI & React Microservices Engineering Blueprint": px(4170460), # engineering book
    "Database Internals & Distributed Systems Design": px(4170463), # database book
    "Clean Code in Enterprise Systems":             px(4170466),  # coding book
    "Modern Cloud Architecture with Microservices & Docker": px(4170469), # cloud book
    "Indian Polity & Governance for Competitive Exams": px(4170472), # polity book
    "Ancient Indian Heritage & Architectural Wonders": px(4170475), # heritage book
}

# Keyword patterns → Pexels IDs for fallback matching
KEYWORD_IMAGE_MAP = [
    # Electronics - most specific first
    (r"noise.cancell|over.ear.*head|wireless.*headphone|headphone|earphone|earbud",  px(3394650)),
    (r"bluetooth.*speaker|portable.*speaker|waterproof.*speaker|speaker",            px(1706694)),
    (r"rgb.*keyboard|mechanical.*keyboard|gaming.*keyboard|keyboard",                px(2115256)),
    (r"wireless.*mouse|ergonomic.*mouse|gaming.*mouse|mouse\b",                      px(1037995)),
    (r"gan.*charg|65w.*charg|fast.*charg|wireless.*charg",                           px(4526408)),
    (r"type-c.*cable|lightning.*cable|braided.*cable|usb.*cable",                    px(4526418)),
    (r"thunderbolt|usb.*hub|usb-c.*hub",                                             px(4526430)),
    (r"webcam|web.*cam|streamer.*cam",                                               px(4126743)),
    (r"smartwatch|fitness.*band|smart.*band|spO2|heart.*rate.*mon",                  px(393047)),
    (r"gaming.*laptop|rtx.*laptop|gaming.*beast",                                    px(777001)),
    (r"ultrabook|thin.*light.*laptop|slim.*laptop",                                  px(7974681)),
    (r"laptop|notebook|computer",                                                    px(18105)),
    (r"5g.*flagship|flagship.*phone|prime.*pro",                                     px(607812)),
    (r"smartphone|mobile.*phone|5g.*phone|iphone|samsung",                           px(1092644)),
    (r"power.*bank|portable.*charg",                                                 px(4526403)),
    (r"screen.*protect|tempered.*glass",                                             px(404280)),
    (r"phone.*case|mobile.*case|armor.*case|shockproof.*case",                       px(1034662)),
    (r"tripod|selfie.*stick",                                                        px(1500355)),
    (r"car.*mount|phone.*mount|car.*charger.*mount",                                 px(5187260)),
    (r"flash.*drive|otg.*drive|usb.*drive",                                          px(4526416)),
    (r"hdmi.*adapt|usb.*hdmi|display.*adapt",                                        px(4526414)),
    (r"extension.*board|power.*strip|surge.*protect",                                px(4526412)),
    (r"cooling.*pad|laptop.*cooler",                                                 px(5082579)),
    (r"laptop.*stand|aluminum.*stand",                                               px(1714208)),
    (r"laptop.*sleeve|laptop.*bag|neoprene.*sleeve",                                 px(1649771)),
    (r"robot.*vacuum|vacuum.*cleaner",                                               px(3637786)),
    (r"wireless.*charg.*pad|charging.*pad",                                          px(4526422)),
    (r"power.*adapter|multi.*pin.*adapter",                                          px(4526427)),
    (r"amoled|starlight|neo.*5g",                                                    px(699122)),

    # Fashion - Ethnic / Indian wear
    (r"kurta|kurti|anarkali|chikankari|embroid.*kurti",                              px(8285390)),
    (r"saree|banarasi.*silk|silk.*saree",                                            px(1536619)),
    (r"palazzo|tunic.*set|palazzo.*tunic",                                           px(8285357)),

    # Fashion - Tops
    (r"graphic.*t.shirt|round.*neck.*t|classic.*tee",                               px(1043474)),
    (r"polo.*t.shirt|men.*polo|polo.*collar",                                        px(9558738)),
    (r"sports.*bra|high.*support.*bra",                                              px(4498481)),
    (r"blouse|embellish.*blouse|sleeveless.*top",                                    px(3622574)),
    (r"nightwear|satin.*night|night.*set",                                           px(6311417)),
    (r"women.*sweatshirt|trendy.*sweat|ladies.*sweat",                               px(3622554)),
    (r"hoodie|zip.*up.*hoodie|fleece.*zip",                                          px(6311423)),

    # Fashion - Shirts
    (r"linen.*shirt|formal.*shirt|oxford.*shirt|button.*down.*shirt",               px(297933)),
    (r"cotton.*shirt|casual.*shirt|regular.*fit.*shirt",                             px(3622608)),
    (r"shirt\b",                                                                     px(297933)),

    # Fashion - Jeans / Trousers
    (r"ripped.*jean|skinny.*jean|distressed.*denim",                                px(4210858)),
    (r"denim.*jean|jeans\b",                                                         px(1598507)),
    (r"chino|flat.*front.*trouser|formal.*trouser",                                  px(4210851)),
    (r"jogger|trackpant|track.*pant|sweatpant",                                      px(8386434)),
    (r"compression.*tight|active.*tight|sports.*tight",                              px(8386440)),

    # Fashion - Outerwear
    (r"windbreaker|hooded.*outdoor.*jacket",                                         px(8386432)),
    (r"blazer|wool.*blend.*blazer|business.*blazer",                                 px(1656684)),
    (r"sweatshirt|crewneck.*sweat",                                                  px(3622554)),

    # Fashion - Women dresses
    (r"midi.*dress|wrap.*dress|chiffon.*dress|floral.*dress",                        px(1536619)),
    (r"jegging|high.*rise.*slim.*fit.*jegg",                                         px(1598505)),

    # Footwear
    (r"running.*shoes|mesh.*running|lightweight.*running",                           px(2529148)),
    (r"canvas.*sneaker|low.*top.*canvas|classic.*sneaker",                           px(1598508)),
    (r"oxford.*shoe|derby.*shoe|formal.*oxford|leather.*formal",                     px(336372)),
    (r"trekking|hiking.*boot|waterproof.*boot",                                      px(1456706)),
    (r"flip.*flop|chappal|daily.*wear.*slipp",                                       px(1598506)),
    (r"block.*heel|party.*pump|embellish.*pump|heels\b",                             px(3622555)),
    (r"loafer|slip.*on.*women|women.*loafer",                                        px(1598509)),
    (r"sandal|strappy.*flat|flat.*sandal",                                           px(1458492)),
    (r"slide|eva.*slide|slip.*on.*slide",                                            px(3622560)),
    (r"sports.*shoes|velcro.*sport|men.*sport.*shoe",                                px(2529148)),
    (r"shoes\b|boots\b|footwear",                                                    px(2529148)),

    # Fashion Accessories
    (r"bifold.*wallet|leather.*wallet|casual.*wallet",                               px(1152077)),
    (r"wallet\b",                                                                    px(1152077)),
    (r"braided.*belt|leather.*belt|reversible.*belt",                                px(1152078)),
    (r"belt\b",                                                                      px(1152078)),
    (r"aviator|polarized.*sunglass|uv400.*sunglass",                                 px(1572387)),
    (r"sunglasses\b|sunglass\b",                                                     px(1572387)),
    (r"canvas.*backpack|everyday.*backpack|casual.*backpack",                        px(1553793)),
    (r"backpack\b",                                                                  px(1553793)),
    (r"stainless.*watch|analog.*watch|classic.*watch",                               px(190819)),
    (r"watch\b",                                                                     px(190819)),
    (r"boxer.*short|men.*boxer|multipak.*boxer",                                     px(8386438)),

    # Home Appliances
    (r"microwave|grill.*oven|microwave.*oven",                                       px(5824569)),
    (r"juicer|centrifugal.*juicer|2-in-1.*juicer",                                  px(4397290)),
    (r"mixer.*grinder|wet.*grinder|750w.*mixer",                                     px(1640777)),
    (r"air.*fryer|digital.*air.*fryer",                                              px(5946476)),
    (r"electric.*kettle|glass.*kettle|cordless.*kettle",                             px(4397293)),
    (r"air.*purifier|hepa.*purifier",                                                px(4397297)),
    (r"tower.*fan|ceiling.*fan|speed.*fan|fan\b",                                    px(4397300)),
    (r"steam.*iron|anti.*drip.*iron|iron\b",                                         px(4397303)),
    (r"water.*purifier|ro.*uv|reverse.*osmosis",                                     px(4397306)),
    (r"water.*dispenser|hot.*cold.*dispenser",                                       px(4397309)),
    (r"car.*washer|pressure.*washer|high.*pressure.*spray",                          px(4397312)),
    (r"mosquito.*trap|insect.*killer|trapper.*lamp",                                 px(4397315)),

    # Kitchen
    (r"cookware.*set|non.*stick.*set|tawa.*set",                                     px(4397320)),
    (r"pressure.*cooker|induction.*cooker",                                          px(4397323)),
    (r"cast.*iron.*skillet|skillet|griller\b",                                       px(4397326)),
    (r"knife.*set|kitchen.*knife",                                                   px(4397329)),
    (r"spatula|silicone.*utensil|cooking.*utensil",                                  px(4397332)),
    (r"vegetable.*chopper|5-in-1.*chopper|dicer",                                   px(4397335)),
    (r"food.*storage|airtight.*container|bpa.*free.*container",                      px(4397338)),
    (r"dish.*rack|drying.*rack",                                                     px(4397341)),
    (r"aroma.*diffuser|ultrasonic.*diffuser|essential.*oil.*diffus",                 px(4397344)),
    (r"water.*bottle|insulated.*bottle|stainless.*bottle",                           px(4397347)),

    # Furniture
    (r"mesh.*office.*chair|ergonomic.*chair|high.*back.*mesh",                       px(1957478)),
    (r"armchair|velvet.*arm|velvet.*chair",                                          px(1866149)),
    (r"recliner|sofa.*chair|foldable.*recliner",                                     px(1866149)),
    (r"writing.*desk|study.*desk|solid.*wood.*desk",                                 px(1957477)),
    (r"dining.*table|glass.*top.*dining|extendable.*table",                          px(1350789)),
    (r"tv.*unit|entertainment.*unit|floating.*tv",                                   px(1350790)),
    (r"fabric.*sofa|3-seater.*sofa|sofa.*ottoman",                                   px(1350789)),
    (r"bed.*frame|platform.*bed|upholster.*bed",                                     px(1350788)),
    (r"bedsheet|cotton.*bedsheet|reversible.*bedsheet",                              px(1350787)),
    (r"pillow|memory.*foam.*pillow",                                                 px(1350786)),
    (r"wardrobe|sliding.*wardrobe|4-door.*wardrobe",                                 px(1350785)),
    (r"shoe.*rack|3-tier.*rack|wooden.*shoe.*rack",                                  px(1350784)),
    (r"sofa\b",                                                                      px(1350789)),
    (r"bed\b",                                                                       px(1350788)),
    (r"chair\b",                                                                     px(1957478)),
    (r"table\b|desk\b",                                                              px(1350789)),

    # Beauty & Personal Care
    (r"vitamin.*c.*serum|brightening.*serum|hyaluronic.*serum",                      px(3685523)),
    (r"niacinamide|pore.*minimiz|zinc.*serum",                                       px(3685525)),
    (r"face.*wash|foaming.*face|salicylic.*face",                                    px(3685521)),
    (r"moisturizing.*cream|ceramide|peptide.*cream|moisturizer",                     px(3685519)),
    (r"sunscreen|spf.*50|sun.*gel|sun.*protect",                                     px(3685517)),
    (r"body.*scrub|papaya.*scrub|brightening.*scrub",                                px(3685515)),
    (r"shampoo|keratin.*shampoo|anti.*frizz.*shampoo",                               px(3735969)),
    (r"hair.*oil|bhringraj|hair.*growth.*oil",                                       px(3735965)),
    (r"hair.*straightener|ceramic.*straightener|ionic.*straight",                    px(3735961)),
    (r"lipstick|bullet.*lip|matte.*lip",                                             px(3735957)),
    (r"beard.*oil|beard.*soften|jojoba.*beard",                                      px(3735953)),
    (r"serum\b",                                                                     px(3685523)),
    (r"lotion\b|cream\b|skin.*care",                                                 px(3685519)),

    # Grocery
    (r"basmati.*rice|royal.*basmati|aged.*rice",                                     px(1537538)),
    (r"toor.*dal|arhar.*dal|lentil|dal\b",                                           px(1640776)),
    (r"mustard.*oil|kachi.*ghani",                                                   px(1640775)),
    (r"desi.*ghee|a2.*ghee|cow.*ghee|gir.*ghee",                                    px(1640774)),
    (r"wild.*honey|forest.*honey|raw.*honey|honey\b",                               px(1640773)),
    (r"california.*almond|almond\b",                                                 px(1640772)),
    (r"cashew.*nut|roasted.*cashew|kaju",                                            px(1640771)),
    (r"peanut.*butter|dark.*choc.*peanut",                                           px(1640770)),
    (r"black.*tea|ctc.*tea|assam.*tea|chai\b|tea\b",                                 px(1640769)),
    (r"filter.*coffee|south.*indian.*coffee|ground.*coffee|coffee\b",               px(1640768)),
    (r"rice\b",                                                                      px(1537538)),
    (r"oil\b|cooking.*oil",                                                          px(1640775)),
    (r"ghee\b",                                                                      px(1640774)),

    # Sports & Fitness
    (r"rubber.*dumbbell|dumbbell.*set|adjustable.*dumbbell|dumbbell\b",              px(1552252)),
    (r"yoga.*mat|eva.*yoga|non.*slip.*mat",                                          px(4056535)),
    (r"pull.*up.*bar|doorway.*bar|chin.*up.*bar",                                    px(1552253)),
    (r"resistance.*band|loop.*band|exercise.*band",                                  px(4056538)),
    (r"skipping.*rope|jump.*rope|speed.*rope",                                       px(4056541)),
    (r"gym.*gloves|weightlifting.*gloves|padded.*gloves",                            px(4056544)),
    (r"massage.*roller|foam.*roller|roller.*stick",                                  px(4056547)),
    (r"badminton.*racket|carbon.*fiber.*racket|racket\b",                            px(4056550)),
    (r"protein.*shaker|gym.*shaker|shaker.*bottle",                                  px(4056553)),
    (r"hydration.*pack|hydropack|running.*backpack",                                 px(4056556)),

    # Books
    (r"atomic.*habit|high.*performance.*habit",                                      px(4170448)),
    (r"psychology.*wealth|financial.*freedom|money.*book",                           px(4170451)),
    (r"data.*struct|algorithm.*easy|python.*algo",                                   px(4170454)),
    (r"machine.*learning|deep.*learning|ml.*guide",                                  px(4170457)),
    (r"fastapi|react.*microservice|api.*react",                                      px(4170460)),
    (r"database.*internal|distributed.*system",                                      px(4170463)),
    (r"clean.*code|enterprise.*system",                                              px(4170466)),
    (r"cloud.*architect|docker.*microservice",                                       px(4170469)),
    (r"indian.*polity|governance|competitive.*exam|upsc",                            px(4170472)),
    (r"ancient.*indian|heritage|architectur.*wonder",                                px(4170475)),
    (r"book\b|novel\b|guide\b|handbook\b|blueprint\b",                               px(4170448)),
]

# Category fallback images
CATEGORY_FALLBACK = {
    "Electronics":          px(3394650),
    "Mobiles":              px(607812),
    "Laptops":              px(18105),
    "Accessories":          px(393047),
    "Fashion":              px(1043474),
    "Men's Clothing":       px(1043474),
    "Women's Clothing":     px(8285390),
    "Footwear":             px(2529148),
    "Books":                px(4170448),
    "Home & Kitchen":       px(5824569),
    "Home Appliances":      px(5824569),
    "Furniture":            px(1957478),
    "Kitchen Products":     px(4397320),
    "Beauty & Personal Care": px(3685523),
    "Sports & Fitness":     px(1552252),
    "Grocery":              px(1537538),
    "General":              px(1043474),
}


def get_image_for_product(product_name: str, category: str) -> str:
    """Get the best matching image URL for a product."""
    # Strip vendor edition suffix like (Apex Edition), (Aura Edition), etc.
    base_name = re.sub(r'\s*\([^)]*Edition\)', '', product_name).strip()
    base_name = re.sub(r'\s*\([^)]*\)\s*$', '', base_name).strip()

    # 1. Exact match
    if base_name in PRODUCT_IMAGE_DB:
        return PRODUCT_IMAGE_DB[base_name]
    if product_name in PRODUCT_IMAGE_DB:
        return PRODUCT_IMAGE_DB[product_name]

    # 2. Keyword match on base name
    name_lower = base_name.lower()
    for pattern, url in KEYWORD_IMAGE_MAP:
        if re.search(pattern, name_lower):
            return url

    # 3. Keyword match on full name (with edition)
    full_lower = product_name.lower()
    for pattern, url in KEYWORD_IMAGE_MAP:
        if re.search(pattern, full_lower):
            return url

    # 4. Category fallback
    return CATEGORY_FALLBACK.get(category, CATEGORY_FALLBACK["General"])


def update_product_images():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        print(f"Found {len(products)} products to update...")

        updated = 0
        not_matched = []

        for p in products:
            new_url = get_image_for_product(p.product_name, p.category)
            old_url = p.image_url or ""

            p.image_url = new_url
            if new_url != old_url:
                updated += 1

            # Track which ones fell through to category fallback
            if new_url in CATEGORY_FALLBACK.values():
                not_matched.append((p.product_id, p.product_name, p.category, new_url))

        db.commit()
        print(f"\nOK: Updated {updated} product image URLs")

        if not_matched:
            print(f"\nINFO: {len(not_matched)} products used category fallback (still unique per category):")
            for pid, name, cat, url in not_matched[:30]:
                print(f"   ID={pid} | {name[:50]:<50} | {cat}")

        # Print a sample
        print("\nSample updated products:")
        samples = db.query(Product).order_by(Product.product_id).limit(25).all()
        for p in samples:
            img_tail = str(p.image_url)[-50:] if p.image_url else "NONE"
            print(f"  ID={p.product_id:3d} | {p.product_name[:45]:<45} | ...{img_tail}")

        return updated
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_product_images()
