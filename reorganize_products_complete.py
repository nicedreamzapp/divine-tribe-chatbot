#!/usr/bin/env python3
"""
Product Reorganization Script for Tribe Chatbot
Restructures products JSON with proper hierarchy and priorities
Based on Matt's business rules and product categories
"""

import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ProductReorganizer:
    """Reorganizes products into hierarchical structure with priorities"""
    
    def __init__(self):
        # Main product keywords for identification (Priority 1)
        self.MAIN_PRODUCTS = {
            "V5 XL": {
                "keywords": ["XL v5", "V5 XL", "v5 Rebuildable", "XL V5", "v5 Heater", "V5 side"],
                "category": "main_vaporizer",
                "priority": 1,
                "display_name": "V5 XL Rebuildable Heater",
                "description": "#1 for flavor - pure ceramic technology"
            },
            "Core Deluxe": {
                "keywords": ["XL Deluxe Core", "Core eRig", "Deluxe Core", "Core XL"],
                "category": "main_vaporizer", 
                "priority": 1,
                "display_name": "Core Deluxe eRig",
                "description": "Best for beginners - complete eRig kit"
            },
            "Nice Dreamz": {
                "keywords": ["Nice Dreamz", "Dreamz Fogger", "Fogger", "Nice Dreams"],
                "category": "main_vaporizer",
                "priority": 1,
                "display_name": "Nice Dreamz Fogger",
                "description": "Premium concentrate fogger with adjustable airflow"
            },
            "Ruby Twist": {
                "keywords": ["Ruby Twist", "Ruby 510"],
                "category": "cartridge_battery",
                "priority": 1,
                "display_name": "Ruby Twist Battery",
                "description": "510 thread battery for cartridges"
            },
            "Lightning Pen": {
                "keywords": ["Lightning Pen", "Thunder Cap"],
                "category": "portable_vaporizer",
                "priority": 1,
                "display_name": "Lightning Pen",
                "description": "Portable pen vaporizer"
            },
            "Cub": {
                "keywords": ["Cub", "cleaning adapter", "The Cub"],
                "category": "cleaning_accessory",
                "priority": 1.5,  # Important accessory
                "display_name": "The Cub",
                "description": "Recommended cleaning adapter for Core/Nice Dreamz"
            }
        }
        
        # Accessory categories (Priority 2)
        self.ACCESSORIES = {
            "glass": {
                "keywords": ["glass", "bubbler", "hydratube", "matrix perc", "grenade", "recycler"],
                "category": "glass_attachment",
                "priority": 2
            },
            "controller": {
                "keywords": ["controller", "ruby twist controller", "controller for ruby"],
                "category": "controller",
                "priority": 2,
                "parent_product": "Ruby Twist"
            },
            "hubble_bubble": {
                "keywords": ["hubble bubble", "water attachment", "water cooled"],
                "category": "water_attachment",
                "priority": 2
            },
            "carb_cap": {
                "keywords": ["carb cap", "spinner cap", "titanium cap", "glass cap"],
                "category": "carb_cap",
                "priority": 2
            },
            "mod": {
                "keywords": ["pico", "rim c", "mod", "battery mod"],
                "category": "battery_mod",
                "priority": 2
            }
        }
        
        # Replacement parts (Priority 3 - only show when specifically asked)
        self.REPLACEMENT_PARTS = {
            "heater": {
                "keywords": ["replacement heater", "spare heater", "heater cup", "ceramic heater", 
                           "rebuildable coil", "coil assembly", "heater coil"],
                "category": "replacement_part",
                "priority": 3
            },
            "o_ring": {
                "keywords": ["o-ring", "o ring", "gasket", "seal", "rubber ring"],
                "category": "replacement_part",
                "priority": 3
            },
            "screw": {
                "keywords": ["screw", "bolt", "fastener"],
                "category": "replacement_part", 
                "priority": 3
            },
            "wire": {
                "keywords": ["wire", "coil wire", "heating wire", "resistance wire"],
                "category": "replacement_part",
                "priority": 3
            }
        }
        
        # Business rules from Matt
        self.BUSINESS_RULES = {
            "core_always_deluxe": "Core ALWAYS means Core Deluxe (Core 2.0 is obsolete)",
            "cub_with_core": "Cub recommended WITH Core/Nice Dreamz for cleaning",
            "v5_top_flavor": "V5 XL is #1 for flavor (pure ceramic)",
            "core_for_beginners": "Core Deluxe for beginners",
            "no_push_parts": "Never push replacement parts unless asked",
            "ruby_needs_controller": "Ruby Twist needs controllers",
            "nice_dreamz_compatible": "Nice Dreamz coils work with Core"
        }

    def categorize_product(self, product: Dict) -> Tuple[str, int, str]:
        """
        Categorize a product and assign priority
        Returns: (category, priority, matched_keyword)
        """
        name = product.get("name", "").lower()
        description = product.get("full_description", "").lower()
        combined_text = f"{name} {description}"
        
        # Check for main products first
        for main_name, config in self.MAIN_PRODUCTS.items():
            for keyword in config["keywords"]:
                if keyword.lower() in combined_text:
                    return config["category"], config["priority"], main_name
        
        # Check for replacement parts (these get lowest priority)
        for part_type, config in self.REPLACEMENT_PARTS.items():
            for keyword in config["keywords"]:
                if keyword.lower() in combined_text:
                    # Double check it's actually a replacement part
                    if any(term in name for term in ["replacement", "spare", "extra", "rebuild"]):
                        return config["category"], config["priority"], f"replacement_{part_type}"
        
        # Check for accessories
        for acc_type, config in self.ACCESSORIES.items():
            for keyword in config["keywords"]:
                if keyword.lower() in combined_text:
                    return config["category"], config["priority"], f"accessory_{acc_type}"
        
        # Default category for uncategorized items
        return "uncategorized", 4, "unknown"

    def extract_price(self, price_str: str) -> float:
        """Extract numeric price from string"""
        if not price_str:
            return 0.0
        
        # Handle price ranges
        prices = re.findall(r'\$?([\d,]+\.?\d*)', price_str)
        if prices:
            # Return the lowest price for ranges
            return float(prices[0].replace(',', ''))
        return 0.0

    def clean_description(self, description: str) -> str:
        """Clean up description for better readability"""
        # Remove excessive emojis and special characters
        description = re.sub(r'[🔥✨💨🌿🔧💎🚀🌬️]+', '', description)
        # Remove multiple spaces
        description = re.sub(r'\s+', ' ', description)
        # Truncate to reasonable length
        if len(description) > 500:
            description = description[:497] + "..."
        return description.strip()

    def reorganize_products(self, products_file: str) -> Dict:
        """
        Main reorganization function
        Returns hierarchical product structure
        """
        print("🔄 Loading products from JSON...")
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"📦 Processing {len(products)} products...")
        
        # Initialize structure
        organized = {
            "metadata": {
                "total_products": len(products),
                "last_updated": datetime.now().isoformat(),
                "version": "2.0",
                "business_rules": self.BUSINESS_RULES
            },
            "categories": {
                "main_products": {
                    "display_name": "Main Products",
                    "priority": 1,
                    "description": "Featured vaporizers and devices",
                    "products": []
                },
                "accessories": {
                    "display_name": "Accessories", 
                    "priority": 2,
                    "description": "Glass, controllers, and add-ons",
                    "products": []
                },
                "replacement_parts": {
                    "display_name": "Replacement Parts",
                    "priority": 3,
                    "description": "Spare parts and rebuild kits (shown only when requested)",
                    "products": []
                },
                "bundles": {
                    "display_name": "Bundles & Kits",
                    "priority": 1.5,
                    "description": "Complete packages and combo deals",
                    "products": []
                }
            },
            "product_index": {},  # Quick lookup by ID
            "search_index": {}    # Search keywords to product IDs
        }
        
        # Process each product
        for idx, product in enumerate(products):
            category, priority, matched = self.categorize_product(product)
            
            # Create enhanced product entry
            enhanced_product = {
                "id": f"prod_{idx:04d}",
                "name": product["name"],
                "url": product["url"],
                "price": self.extract_price(product.get("price", "")),
                "price_display": product.get("price", "Contact for pricing"),
                "category": category,
                "priority": priority,
                "matched_keywords": matched,
                "in_stock": product.get("in_stock", True),
                "short_description": self.clean_description(product.get("short_description", "")),
                "images": product.get("images", [])[:3],  # Limit to 3 images
                "specifications": product.get("specifications", []),
                "sku": product.get("sku", "")
            }
            
            # Check if it's a bundle
            if "bundle" in product["name"].lower() or "kit" in product["name"].lower():
                organized["categories"]["bundles"]["products"].append(enhanced_product)
            # Sort into appropriate category
            elif priority == 1 or priority == 1.5:
                organized["categories"]["main_products"]["products"].append(enhanced_product)
            elif priority == 2:
                organized["categories"]["accessories"]["products"].append(enhanced_product)
            elif priority == 3:
                organized["categories"]["replacement_parts"]["products"].append(enhanced_product)
            else:
                # Uncategorized items go to accessories by default
                organized["categories"]["accessories"]["products"].append(enhanced_product)
            
            # Add to product index
            organized["product_index"][enhanced_product["id"]] = enhanced_product
            
            # Build search index
            search_terms = [
                product["name"].lower(),
                matched.lower(),
                category.lower()
            ]
            
            for term in search_terms:
                words = term.split()
                for word in words:
                    if len(word) > 2:  # Skip very short words
                        if word not in organized["search_index"]:
                            organized["search_index"][word] = []
                        if enhanced_product["id"] not in organized["search_index"][word]:
                            organized["search_index"][word].append(enhanced_product["id"])
        
        # Sort products within each category by priority
        for category in organized["categories"].values():
            if "products" in category:
                category["products"].sort(key=lambda x: (x["priority"], -x["price"]))
        
        # Add statistics
        organized["metadata"]["statistics"] = {
            "main_products": len(organized["categories"]["main_products"]["products"]),
            "accessories": len(organized["categories"]["accessories"]["products"]),
            "replacement_parts": len(organized["categories"]["replacement_parts"]["products"]),
            "bundles": len(organized["categories"]["bundles"]["products"])
        }
        
        print("\n✅ Reorganization complete!")
        return organized

    def save_organized_products(self, organized: Dict, output_file: str):
        """Save reorganized products to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(organized, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved reorganized products to: {output_file}")

    def print_summary(self, organized: Dict):
        """Print summary of reorganization"""
        print("\n📊 REORGANIZATION SUMMARY")
        print("=" * 50)
        
        stats = organized["metadata"]["statistics"]
        print(f"Total Products: {organized['metadata']['total_products']}")
        print(f"Main Products: {stats['main_products']}")
        print(f"Accessories: {stats['accessories']}")
        print(f"Replacement Parts: {stats['replacement_parts']}")
        print(f"Bundles: {stats['bundles']}")
        
        print("\n🌟 TOP MAIN PRODUCTS:")
        for product in organized["categories"]["main_products"]["products"][:5]:
            print(f"  • {product['name'][:50]}")
            print(f"    Price: {product['price_display']}")
            print(f"    Category: {product['category']}")
        
        print("\n📋 BUSINESS RULES APPLIED:")
        for rule, description in organized["metadata"]["business_rules"].items():
            print(f"  ✓ {description}")

def main():
    """Main execution function"""
    print("""
╔════════════════════════════════════════════╗
║   TRIBE CHATBOT PRODUCT REORGANIZER v2.0  ║
║   Restructuring products with hierarchy   ║
╚════════════════════════════════════════════╝
    """)
    
    # Initialize reorganizer
    reorganizer = ProductReorganizer()
    
    # Input and output files
    input_file = "complete_products_full.json"
    output_file = "products_organized.json"
    
    try:
        # Reorganize products
        organized = reorganizer.reorganize_products(input_file)
        
        # Save results
        reorganizer.save_organized_products(organized, output_file)
        
        # Print summary
        reorganizer.print_summary(organized)
        
        print("\n✨ SUCCESS! Your products have been reorganized.")
        print(f"📁 Output file: {output_file}")
        print("\n🚀 Next steps:")
        print("1. Copy products_organized.json to your chatbot directory")
        print("2. Update product_database.py to use the new structure")
        print("3. Test searches for 'V5', 'controllers', 'Core', etc.")
        
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find {input_file}")
        print("Make sure complete_products_full.json is in the same directory")
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in {input_file}")
        print(f"Details: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

