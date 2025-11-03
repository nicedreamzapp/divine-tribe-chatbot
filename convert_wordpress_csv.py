#!/usr/bin/env python3
"""
Convert WordPress/WooCommerce CSV export to products_organized.json
FIXED: Proper price parsing, better categorization, V5 XL prioritization
"""

import csv
import json
from datetime import datetime
import re

class WordPressToJSON:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.products = []
        
        # Category mapping with priorities - IMPROVED
        self.category_mapping = {
            # Main products (Priority 1) - MUST contain these exact phrases
            'divine crossing xl v5': {'name': 'main_products', 'priority': 1, 'boost': 500},
            'xl v5': {'name': 'main_products', 'priority': 1, 'boost': 400},
            'core deluxe': {'name': 'main_products', 'priority': 1, 'boost': 400},
            'core 2.0': {'name': 'main_products', 'priority': 1, 'boost': 300},
            'ruby twist': {'name': 'main_products', 'priority': 1, 'boost': 400},
            'nice dreamz fogger': {'name': 'main_products', 'priority': 1, 'boost': 400},
            'lightning pen': {'name': 'main_products', 'priority': 1, 'boost': 400},
            'quest': {'name': 'main_products', 'priority': 1, 'boost': 300},
            
            # Bundles (Priority 1.5)
            'bundle': {'name': 'bundles', 'priority': 1.5, 'boost': 0},
            'kit': {'name': 'bundles', 'priority': 1.5, 'boost': 0},
            
            # Accessories (Priority 2)
            'glass': {'name': 'accessories', 'priority': 2, 'boost': 0},
            'hydratube': {'name': 'accessories', 'priority': 2, 'boost': 0},
            'carb cap': {'name': 'accessories', 'priority': 2, 'boost': 0},
            'pico': {'name': 'accessories', 'priority': 2, 'boost': 0},
            'battery': {'name': 'accessories', 'priority': 2, 'boost': 0},
            'mod': {'name': 'accessories', 'priority': 2, 'boost': 0},
            'jar': {'name': 'accessories', 'priority': 2, 'boost': 0},
            'adapter': {'name': 'accessories', 'priority': 2, 'boost': 0},
            'cub': {'name': 'accessories', 'priority': 2, 'boost': 0},
            
            # Replacement parts (Priority 3)
            'replacement': {'name': 'replacement_parts', 'priority': 3, 'boost': 0},
            'coil': {'name': 'replacement_parts', 'priority': 3, 'boost': 0},
            'heater': {'name': 'replacement_parts', 'priority': 3, 'boost': 0},
            'cup': {'name': 'replacement_parts', 'priority': 3, 'boost': 0},
        }
    
    def parse_csv(self):
        """Parse WordPress CSV export"""
        print(f"📖 Reading CSV: {self.csv_file}")
        
        with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Only process published simple and variable products
                if row.get('Published') == '1' and row.get('Type') in ['simple', 'variable']:
                    product = self.convert_product(row)
                    if product:
                        self.products.append(product)
        
        print(f"✅ Parsed {len(self.products)} products")
        return self.products
    
    def convert_product(self, row):
        """Convert CSV row to product dict"""
        try:
            # Extract basic info
            product_id = row.get('ID', '')
            name = row.get('Name', '').strip()
            
            if not name:
                return None
            
            # Build product URL from name (WordPress permalink structure)
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            url = f"https://ineedhemp.com/product/{slug}/"
            
            # Get price - FIXED PARSING
            price = row.get('Regular price', '').strip()
            sale_price = row.get('Sale price', '').strip()
            
            # For variable products, use min/max prices
            min_price = row.get('Meta: _min_variation_price', '').strip()
            max_price = row.get('Meta: _max_variation_price', '').strip()
            
            price_value = None
            price_display = None
            
            # Try to parse prices
            if sale_price and sale_price not in ['taxable', '']:
                try:
                    price_value = float(sale_price)
                    price_display = f"${price_value:.2f}"
                except:
                    pass
            
            if not price_value and price and price not in ['taxable', '']:
                try:
                    price_value = float(price)
                    price_display = f"${price_value:.2f}"
                except:
                    pass
            
            # For variable products with price range
            if not price_value and min_price and max_price:
                try:
                    min_val = float(min_price)
                    max_val = float(max_price)
                    if min_val == max_val:
                        price_value = min_val
                        price_display = f"${min_val:.2f}"
                    else:
                        price_value = min_val  # Use minimum for sorting
                        price_display = f"${min_val:.2f}–${max_val:.2f}"
                except:
                    pass
            
            # Get categories
            categories = row.get('Categories', '').strip()
            category_info = self.determine_category(name, categories)
            
            # Get images
            images_str = row.get('Images', '').strip()
            images = [img.strip() for img in images_str.split(',') if img.strip()] if images_str else []
            
            # In stock?
            in_stock = row.get('In stock?', '').strip() == '1'
            
            # Short description
            short_desc = row.get('Short description', '').strip()
            if short_desc:
                # Remove HTML tags
                short_desc = re.sub(r'<[^>]+>', '', short_desc)
                short_desc = short_desc[:200]  # Limit length
            
            product = {
                'id': f"prod_{product_id}",
                'name': name,
                'url': url,
                'price': price_value,
                'price_display': price_display if price_display else "Check website",
                'category': category_info['name'],
                'priority': category_info['priority'],
                'search_boost': category_info.get('boost', 0),  # For search ranking
                'in_stock': in_stock,
                'short_description': short_desc,
                'images': images[:3],  # Limit to 3 images
                'sku': row.get('SKU', '').strip()
            }
            
            return product
            
        except Exception as e:
            print(f"⚠️  Error parsing product {name}: {e}")
            return None
    
    def determine_category(self, name, categories):
        """Determine which category a product belongs to - IMPROVED"""
        name_lower = name.lower()
        categories_lower = categories.lower()
        
        # Check for exact main product matches FIRST (highest priority)
        main_products = {
            'divine crossing xl v5': {'name': 'main_products', 'priority': 1, 'boost': 500},
            'xl v5 rebuildable': {'name': 'main_products', 'priority': 1, 'boost': 450},
            'core deluxe': {'name': 'main_products', 'priority': 1, 'boost': 400},
            'ruby twist ball vape': {'name': 'main_products', 'priority': 1, 'boost': 400},
            'nice dreamz fogger': {'name': 'main_products', 'priority': 1, 'boost': 400},
        }
        
        for keyword, cat_info in main_products.items():
            if keyword in name_lower:
                return cat_info
        
        # Check against general mapping
        for keyword, cat_info in self.category_mapping.items():
            if keyword in name_lower or keyword in categories_lower:
                return cat_info
        
        # Default to accessories
        return {'name': 'accessories', 'priority': 2, 'boost': 0}
    
    def organize_products(self):
        """Organize products into category structure"""
        organized = {
            'metadata': {
                'total_products': len(self.products),
                'last_updated': datetime.now().isoformat(),
                'version': '2.1',
                'source': 'WordPress Export - FIXED',
                'business_rules': {
                    'core_always_deluxe': 'Core ALWAYS means Core Deluxe (Core 2.0 is obsolete)',
                    'cub_with_core': 'Cub recommended WITH Core/Nice Dreamz for cleaning',
                    'v5_top_flavor': 'V5 XL is #1 for flavor (pure ceramic)',
                    'core_for_beginners': 'Core Deluxe for beginners',
                    'no_push_parts': 'Never push replacement parts unless asked',
                    'ruby_needs_controller': 'Ruby Twist needs controllers',
                    'nice_dreamz_compatible': 'Nice Dreamz coils work with Core'
                }
            },
            'categories': {
                'main_products': {
                    'display_name': 'Main Products',
                    'priority': 1,
                    'description': 'Featured vaporizers and devices',
                    'products': []
                },
                'bundles': {
                    'display_name': 'Bundles & Kits',
                    'priority': 1.5,
                    'description': 'Complete bundles with Cub',
                    'products': []
                },
                'accessories': {
                    'display_name': 'Accessories',
                    'priority': 2,
                    'description': 'Glass, mods, and accessories',
                    'products': []
                },
                'replacement_parts': {
                    'display_name': 'Replacement Parts',
                    'priority': 3,
                    'description': 'Coils, heaters, and replacement components',
                    'products': []
                }
            },
            'product_index': {},
            'search_index': {}
        }
        
        # Sort products into categories
        for product in self.products:
            cat_name = product['category']
            if cat_name in organized['categories']:
                organized['categories'][cat_name]['products'].append(product)
                
                # Add to product index
                product_id = product['id']
                organized['product_index'][product_id] = product
                
                # Add to search index
                name_lower = product['name'].lower()
                for word in name_lower.split():
                    if len(word) > 2:  # Skip short words
                        if word not in organized['search_index']:
                            organized['search_index'][word] = []
                        organized['search_index'][word].append(product_id)
        
        # Update statistics
        organized['metadata']['statistics'] = {
            'main_products': len(organized['categories']['main_products']['products']),
            'bundles': len(organized['categories']['bundles']['products']),
            'accessories': len(organized['categories']['accessories']['products']),
            'replacement_parts': len(organized['categories']['replacement_parts']['products'])
        }
        
        return organized
    
    def save_json(self, output_file='products_organized_FIXED.json'):
        """Save to JSON file"""
        organized = self.organize_products()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(organized, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved to: {output_file}")
        
        # Print summary
        stats = organized['metadata']['statistics']
        print(f"\n📊 SUMMARY:")
        print(f"  Total products: {organized['metadata']['total_products']}")
        print(f"  Main products: {stats['main_products']}")
        print(f"  Bundles: {stats['bundles']}")
        print(f"  Accessories: {stats['accessories']}")
        print(f"  Replacement parts: {stats['replacement_parts']}")
        
        #

 Show sample products with prices
        print(f"\n💰 Sample Prices:")
        for cat_name, cat_data in organized['categories'].items():
            if cat_data['products']:
                sample = cat_data['products'][0]
                print(f"  {sample['name'][:50]}: {sample['price_display']}")
        
        return output_file


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   WORDPRESS CSV → products_organized.json CONVERTER      ║
    ║   FIXED: Prices, V5 XL Priority, Better Categorization   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Find CSV file
    import glob
    csv_files = glob.glob('wc-product-export-*.csv')
    
    if not csv_files:
        print("❌ No WordPress export CSV found!")
        print("   Please save your exported CSV in this directory")
        print("   File should be named: wc-product-export-*.csv")
        return
    
    csv_file = csv_files[0]
    print(f"📁 Found: {csv_file}\n")
    
    # Convert
    converter = WordPressToJSON(csv_file)
    converter.parse_csv()
    output = converter.save_json()
    
    print(f"\n{'='*70}")
    print("NEXT STEPS:")
    print(f"{'='*70}")
    print(f"1. Review the new file: {output}")
    print(f"2. Test that prices show correctly")
    print(f"3. Replace old file:")
    print(f"   mv products_organized.json products_organized_OLD2.json")
    print(f"   mv {output} products_organized.json")
    print(f"4. Restart chatbot!")
    print(f"\n✨ Prices fixed! V5 XL prioritized! Better categorization!")


if __name__ == "__main__":
    main()
