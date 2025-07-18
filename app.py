import os
import re
import json
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
SPOONACULAR_API_KEY = "ef894cd8d3b54a408581aba96d542406"
SPOONACULAR_BASE_URL = "https://api.spoonacular.com/recipes"

# In-memory storage for scheduled meals (in production, use a database)
scheduled_meals = {}

# Spoonacular API configuration
SPOONACULAR_API_KEY = "ef894cd8d3b54a408581aba96d542406"
SPOONACULAR_BASE_URL = "https://api.spoonacular.com/recipes"

# Enhanced recipe generation data
COOKING_METHODS = [
    "Stir Fry", "Soup", "Salad", "Casserole", "Pasta", "Skillet", "Bake", "Grill", 
    "Stew", "Sandwich", "Wrap", "Tacos", "Burrito", "Pizza", "Lasagna", "Curry",
    "Risotto", "Quiche", "Frittata", "Omelette", "Burger", "Kebab", "Skewers",
    "Roast", "Braised", "Poached", "Steamed", "Fried", "Air Fry", "Smoked"
]

CUISINES = [
    "Italian", "Mexican", "Asian", "Mediterranean", "Indian", "French", "Thai",
    "Japanese", "Chinese", "Greek", "Spanish", "American", "Middle Eastern",
    "Caribbean", "African", "Fusion", "Modern", "Classic", "Rustic", "Gourmet"
]

COOKING_TECHNIQUES = [
    "sauté", "simmer", "boil", "steam", "roast", "grill", "bake", "fry",
    "braise", "poach", "smoke", "air fry", "slow cook", "pressure cook"
]

FLAVOR_PROFILES = [
    "savory", "spicy", "sweet", "tangy", "herbaceous", "smoky", "creamy",
    "citrusy", "umami", "fresh", "rich", "light", "bold", "subtle"
]

RECIPE_ADJECTIVES = [
    "Delicious", "Amazing", "Fantastic", "Incredible", "Wonderful", "Perfect",
    "Gourmet", "Chef's", "Signature", "Classic", "Modern", "Rustic", "Elegant",
    "Comforting", "Refreshing", "Hearty", "Light", "Bold", "Subtle", "Creative"
]

# Food emojis for fallback recipes
FOOD_EMOJIS = [
    "🍽️", "🍳", "🥘", "🍲", "🥗", "🍜", "🍝", "🍛", "🍚", "🍙", "🍱", "🥪", "🌮", "🌯", "🍕", "🍔", "🥩", "🍗", "🍖", "🥓", "🍤", "🦐", "🐟", "🐠", "🥬", "🥕", "🥦", "🥒", "🍅", "🌶️", "🧅", "🧄", "🥔", "🍠", "🥜", "🌰", "🥑", "🥝", "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍒", "🍑", "🥭", "🍍", "🥥", "🥑", "🥦", "🥬", "🥒", "🌽", "🥕", "🥔", "🍠", "🥐", "🥯", "🍞", "🥖", "🥨", "🧀", "🥚", "🥛", "🍼", "☕", "🍵", "🧃", "🥤", "🧋", "🍶", "🍺", "🍷", "🥂", "🍾", "🥃", "🍸", "🍹", "🍻", "🥂", "🍷", "🍸", "🍹", "🍺", "🍻", "🥃", "🍾", "🍶", "🍵", "☕", "🥤", "🧃", "🧋", "🥛", "🍼", "🥚", "🧀", "🥨", "🥖", "🍞", "🥯", "🥐", "🍠", "🥔", "🥕", "🌽", "🥒", "🥬", "🥦", "🥑", "🥥", "🍍", "🥭", "🍑", "🍒", "🫐", "🍓", "🍇", "🍉", "🍌", "🍋", "🍊", "🍐", "🍎", "🥝", "🥑", "🌰", "🥜", "🍠", "🥔", "🥕", "🥦", "🥬", "🥒", "🍅", "🌶️", "🧄", "🧅", "🐠", "🐟", "🦐", "🍤", "🥓", "🍖", "🍗", "🥩", "🍔", "🍕", "🌯", "🌮", "🥪", "🍱", "🍙", "🍚", "🍛", "🍝", "🍜", "🥗", "🍲", "🥘", "🍳", "🍽️"
]

def search_spoonacular_recipes(ingredients, number=10):
    """Search for recipes using Spoonacular API"""
    try:
        ingredients_str = ",".join(ingredients)
        url = f"{SPOONACULAR_BASE_URL}/findByIngredients"
        params = {
            'apiKey': SPOONACULAR_API_KEY,
            'ingredients': ingredients_str,
            'number': number,
            'ranking': 1,
            'ignorePantry': False
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error calling Spoonacular API: {e}")
        return []

def get_recipe_instructions(recipe_id):
    """Get detailed recipe instructions from Spoonacular"""
    try:
        url = f"{SPOONACULAR_BASE_URL}/{recipe_id}/information"
        params = {
            'apiKey': SPOONACULAR_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"❌ Error getting recipe instructions: {e}")
        return None

def generate_creative_recipe_name(ingredients, method, cuisine):
    """Generate a creative and engaging recipe name"""
    if not ingredients:
        return "Chef's Special Creation"
    
    # Get main ingredients for naming
    main_ingredient = ingredients[0].title() if ingredients else "Delight"
    secondary_ingredient = ingredients[1].title() if len(ingredients) > 1 else ""
    
    # Creative adjectives for recipe names
    creative_adjectives = [
        "Golden", "Crispy", "Savory", "Aromatic", "Zesty", "Velvety", "Rustic", 
        "Gourmet", "Artisan", "Chef's", "Signature", "Premium", "Deluxe", "Classic",
        "Modern", "Traditional", "Fusion", "Exotic", "Homestyle", "Garden Fresh",
        "Sun-Kissed", "Herb-Infused", "Spice-Rubbed", "Citrus-Bright", "Smoky",
        "Creamy", "Tangy", "Sweet & Spicy", "Umami-Rich", "Fresh-Picked"
    ]
    
    # Cooking method variations
    method_variations = {
        'stir fry': ['Stir-Fry', 'Wok-Tossed', 'Quick-Fried', 'Asian-Style'],
        'roast': ['Roasted', 'Oven-Baked', 'Slow-Roasted', 'Herb-Roasted'],
        'grill': ['Grilled', 'Char-Grilled', 'Flame-Kissed', 'BBQ-Style'],
        'bake': ['Baked', 'Oven-Fresh', 'Golden-Baked', 'Artisan-Baked'],
        'soup': ['Soup', 'Bisque', 'Chowder', 'Broth'],
        'salad': ['Salad', 'Medley', 'Mix', 'Bowl'],
        'pasta': ['Pasta', 'Noodles', 'Primavera', 'Alfredo'],
        'skillet': ['Skillet', 'Pan-Seared', 'One-Pan', 'Cast-Iron']
    }
    
    # Get method variation
    method_key = method.lower().replace(' ', '')
    method_variation = method_variations.get(method_key, [method.title()])[0]
    
    # Creative name templates
    name_templates = [
        # Simple and elegant
        f"{random.choice(creative_adjectives)} {main_ingredient} {method_variation}",
        f"{method_variation} {main_ingredient} {random.choice(creative_adjectives)}",
        f"{cuisine} {main_ingredient} {method_variation}",
        
        # With secondary ingredients
        f"{main_ingredient} & {secondary_ingredient} {method_variation}" if secondary_ingredient else f"{main_ingredient} {method_variation}",
        f"{random.choice(creative_adjectives)} {main_ingredient} with {secondary_ingredient}" if secondary_ingredient else f"{random.choice(creative_adjectives)} {main_ingredient}",
        
        # Chef-inspired
        f"Chef's {random.choice(creative_adjectives)} {main_ingredient}",
        f"Signature {main_ingredient} {method_variation}",
        f"Artisan {method_variation} {main_ingredient}",
        
        # Descriptive and appealing
        f"{random.choice(creative_adjectives)} {cuisine} {method_variation}",
        f"{method_variation} {main_ingredient} Delight",
        f"{main_ingredient} {method_variation} Supreme",
        
        # Seasonal and fresh
        f"Garden Fresh {main_ingredient} {method_variation}",
        f"Sun-Kissed {main_ingredient} {method_variation}",
        f"Herb-Infused {main_ingredient} {method_variation}",
        
        # Fusion and modern
        f"{cuisine} Fusion {main_ingredient}",
        f"Modern {main_ingredient} {method_variation}",
        f"{random.choice(creative_adjectives)} {method_variation} Fusion"
    ]
    
    # Filter out templates that don't work with current ingredients
    valid_templates = []
    for template in name_templates:
        try:
            # Test if the template can be formatted
            test_name = template.format(
                main_ingredient=main_ingredient,
                secondary_ingredient=secondary_ingredient,
                method_variation=method_variation,
                cuisine=cuisine,
                random=random.choice(creative_adjectives)
            )
            valid_templates.append(template)
        except:
            continue
    
    if not valid_templates:
        return f"{random.choice(creative_adjectives)} {main_ingredient} {method_variation}"
    
    # Generate the final name
    chosen_template = random.choice(valid_templates)
    try:
        final_name = chosen_template.format(
            main_ingredient=main_ingredient,
            secondary_ingredient=secondary_ingredient,
            method_variation=method_variation,
            cuisine=cuisine,
            random=random.choice(creative_adjectives)
        )
        return final_name
    except:
        return f"{random.choice(creative_adjectives)} {main_ingredient} {method_variation}"

def generate_detailed_instructions(ingredients, method, cuisine, technique):
    """Generate detailed cooking instructions with comprehensive steps using specific ingredients"""
    prep_time = random.randint(15, 45)
    cook_time = random.randint(20, 90)
    servings = random.randint(2, 8)
    
    # Get main ingredients for specific instructions
    main_ingredient = ingredients[0] if ingredients else "ingredients"
    secondary_ingredients = ingredients[1:3] if len(ingredients) > 1 else []
    
    # Check which ingredients are available for more specific instructions
    has_garlic = any('garlic' in ing.lower() for ing in ingredients)
    has_onion = any('onion' in ing.lower() for ing in ingredients)
    has_vegetables = any(veg in ing.lower() for ing in ingredients for veg in ['tomato', 'pepper', 'carrot', 'broccoli', 'spinach', 'kale', 'lettuce'])
    has_meat = any(meat in ing.lower() for ing in ingredients for meat in ['chicken', 'beef', 'pork', 'lamb', 'turkey', 'fish', 'shrimp'])
    
    # Create ingredient-specific instructions without repetition
    ingredient_mentions = set()  # Track which ingredients have been mentioned
    
    instructions = f"""PREPARATION ({prep_time} minutes):
• Wash and prepare all ingredients
• Chop {', '.join(ingredients)} into uniform pieces
• Gather all necessary cooking equipment

COOKING STEPS ({cook_time} minutes):"""

    # Add ingredient-specific steps without repetition
    if has_garlic and 'garlic' not in ingredient_mentions:
        instructions += f"\n• Mince garlic and set aside"
        ingredient_mentions.add('garlic')
    
    if has_onion and 'onion' not in ingredient_mentions:
        instructions += f"\n• Dice onion finely"
        ingredient_mentions.add('onion')
    
    # Add main cooking steps
    if has_meat:
        meat_ingredient = next((ing for ing in ingredients if any(meat in ing.lower() for meat in ['chicken', 'beef', 'pork', 'lamb', 'turkey', 'fish', 'shrimp'])), ingredients[0])
        instructions += f"\n• Cook {meat_ingredient} first until properly browned"
        ingredient_mentions.add(meat_ingredient.lower())
    
    if has_vegetables:
        veg_ingredients = [ing for ing in ingredients if any(veg in ing.lower() for veg in ['tomato', 'pepper', 'carrot', 'broccoli', 'spinach', 'kale', 'lettuce'])]
        for veg in veg_ingredients:
            if veg.lower() not in ingredient_mentions:
                instructions += f"\n• Add {veg} and cook until tender"
                ingredient_mentions.add(veg.lower())
    
    # Add remaining ingredients that haven't been mentioned
    for ingredient in ingredients:
        if ingredient.lower() not in ingredient_mentions:
            instructions += f"\n• Incorporate {ingredient} and continue cooking"
            ingredient_mentions.add(ingredient.lower())
    
    instructions += f"""

SEASONING & FINISHING:
• Season with salt and black pepper to taste
• Add any additional herbs or spices as desired
• Let the dish rest for 2-3 minutes before serving

COOKING TIPS:
• Keep heat at medium-high for best results
• Don't overcrowd the pan
• Taste and adjust seasoning throughout cooking
• Serve immediately for best flavor and texture

TIMING:
• Preparation time: {prep_time} minutes
• Cooking time: {cook_time} minutes
• Total time: {prep_time + cook_time} minutes
• Servings: {servings} people

SERVING SUGGESTIONS:
• Serve hot and fresh for best texture and flavor
• Consider complementary side dishes
• Garnish with fresh herbs or a drizzle of olive oil
• Let the dish rest briefly before serving

STORAGE:
• Store leftovers in an airtight container for up to 3-4 days
• Reheat gently over low heat to preserve texture
• Most dishes freeze well for future meals"""
    
    return instructions.strip()

def generate_fallback_recipes(ingredients):
    """Generate practical fallback recipes that use ALL selected ingredients with detailed, logical instructions"""
    if not ingredients:
        return []
    
    # Deduplicate ingredients (case-insensitive)
    deduped_ingredients = []
    seen = set()
    for ing in ingredients:
        ing_lower = ing.strip().lower()
        if ing_lower not in seen:
            deduped_ingredients.append(ing)
            seen.add(ing_lower)
    ingredients = deduped_ingredients
    
    # Enhanced ingredient categorization with specific quantities
    def categorize_ingredients(ingredients):
        vegetables = []
        proteins = []
        condiments = []
        grains = []
        dairy = []
        fruits = []
        herbs_spices = []
        
        for ing in ingredients:
            ing_lower = ing.lower()
            if any(veg in ing_lower for veg in ['tomato', 'onion', 'garlic', 'carrot', 'broccoli', 'zucchini', 'pepper', 'mushroom', 'spinach', 'kale', 'lettuce', 'cucumber', 'celery', 'potato', 'sweet potato', 'cauliflower', 'brussels sprouts', 'asparagus', 'green bean', 'pea', 'corn', 'bell pepper', 'jalapeño', 'chili']):
                vegetables.append(ing)
            elif any(prot in ing_lower for prot in ['chicken', 'beef', 'pork', 'fish', 'shrimp', 'salmon', 'tuna', 'turkey', 'lamb', 'egg', 'tofu', 'tempeh', 'bean', 'lentil']):
                proteins.append(ing)
            elif any(cond in ing_lower for cond in ['ketchup', 'mustard', 'mayo', 'sauce', 'dressing', 'vinegar', 'oil', 'butter', 'honey', 'syrup', 'jam', 'jelly']):
                condiments.append(ing)
            elif any(grain in ing_lower for grain in ['rice', 'pasta', 'bread', 'quinoa', 'couscous', 'oat', 'flour', 'noodle']):
                grains.append(ing)
            elif any(dairy_item in ing_lower for dairy_item in ['milk', 'cheese', 'yogurt', 'cream', 'butter', 'sour cream']):
                dairy.append(ing)
            elif any(fruit in ing_lower for fruit in ['apple', 'banana', 'orange', 'lemon', 'lime', 'berry', 'grape', 'peach', 'pear', 'mango', 'pineapple']):
                fruits.append(ing)
            elif any(herb in ing_lower for herb in ['basil', 'oregano', 'thyme', 'rosemary', 'sage', 'parsley', 'cilantro', 'mint', 'dill', 'chive', 'ginger', 'garlic', 'onion']):
                herbs_spices.append(ing)
            else:
                # Default to vegetables for unknown ingredients
                vegetables.append(ing)
        
        return {
            'vegetables': vegetables,
            'proteins': proteins,
            'condiments': condiments,
            'grains': grains,
            'dairy': dairy,
            'fruits': fruits,
            'herbs_spices': herbs_spices
        }
    
    # Helper to add extra ingredients with quantities
    def add_unique_ingredients(base, extras):
        base_lower = set(i.lower() for i in base)
        return base + [e for e in extras if e.lower() not in base_lower]

    # Get ingredient categories
    categories = categorize_ingredients(ingredients)
    recipes = []

    # Recipe 1: Stir Fry (uses all ingredients)
    if len(ingredients) >= 2:
        stirfry_extras = ['2 tbsp soy sauce', '1 tbsp sesame oil', '2 tbsp vegetable oil', '1 tsp salt', '1/2 tsp black pepper']
        all_ings = add_unique_ingredients(ingredients, stirfry_extras)
        
        # Create detailed cooking steps
        cooking_steps = []
        
        # Preparation steps
        if categories['vegetables']:
            veg_list = ', '.join(categories['vegetables'])
            cooking_steps.append(f"• Wash and cut {veg_list} into 1-inch pieces for even cooking")
        
        if categories['proteins']:
            protein_list = ', '.join(categories['proteins'])
            cooking_steps.append(f"• Cut {protein_list} into 1/2-inch cubes or strips")
        
        if categories['herbs_spices']:
            herb_list = ', '.join(categories['herbs_spices'])
            cooking_steps.append(f"• Mince {herb_list} finely and set aside")
        
        cooking_steps.append(f"• Heat 2 tablespoons vegetable oil in a large wok or deep skillet over high heat until oil is shimmering and just starting to smoke")
        
        if categories['herbs_spices']:
            herb_list = ', '.join(categories['herbs_spices'])
            cooking_steps.append(f"• Add minced {herb_list} and stir-fry for 30 seconds until fragrant and golden brown")
        
        if categories['proteins']:
            protein_list = ', '.join(categories['proteins'])
            cooking_steps.append(f"• Add {protein_list} and stir-fry for 3-4 minutes, tossing constantly, until meat is browned on all sides and nearly cooked through")
        
        if categories['vegetables']:
            veg_list = ', '.join(categories['vegetables'])
            cooking_steps.append(f"• Add {veg_list} and stir-fry for 3-4 minutes, tossing constantly, until vegetables are bright in color and slightly tender but still crisp")
        
        if categories['condiments']:
            condiment_list = ', '.join(categories['condiments'])
            cooking_steps.append(f"• Add {condiment_list} and stir-fry for 1-2 minutes, tossing to coat all ingredients evenly")
        
        cooking_steps.append(f"• Pour in 2 tablespoons soy sauce and 1 tablespoon sesame oil, tossing to coat all ingredients evenly")
        
        cooking_steps.append(f"• Season with 1 teaspoon salt and 1/2 teaspoon black pepper to taste, continuing to stir-fry for 1-2 minutes")
        
        cooking_steps.append(f"• Remove from heat when all ingredients are cooked through and serve immediately over steamed rice or noodles")
        
        instructions = '\n'.join(cooking_steps)
        
        # Generate a better recipe name
        def generate_recipe_name(ingredients, categories, style):
            if style == 'stir_fry':
                if categories['proteins'] and categories['vegetables']:
                    protein = categories['proteins'][0].title()
                    veg = categories['vegetables'][0].title()
                    return f"{protein} and {veg} Stir Fry"
                elif categories['proteins']:
                    protein = categories['proteins'][0].title()
                    return f"{protein} Stir Fry"
                elif categories['vegetables']:
                    veg = categories['vegetables'][0].title()
                    return f"{veg} Stir Fry"
                else:
                    return f"Quick Stir Fry"
            return f"Quick Stir Fry"
        
        recipe_name = generate_recipe_name(ingredients, categories, 'stir_fry')
        
        recipes.append({
            'name': recipe_name,
            'ingredients': all_ings,
            'instructions': instructions,
            'image': '🥘',
            'source': 'Generated',
            'cuisine': 'Asian',
            'difficulty': 'Easy',
            'prep_time': '15 min',
            'cook_time': '10 min'
        })

    # Recipe 2: Roasted Medley (uses all ingredients)
    if len(ingredients) >= 2:
        roast_extras = ['3 tbsp olive oil', '1 tsp salt', '1/2 tsp black pepper']
        all_ings = add_unique_ingredients(ingredients, roast_extras)
        
        # Create detailed cooking steps
        cooking_steps = []
        
        # Preparation steps
        if categories['vegetables']:
            veg_list = ', '.join(categories['vegetables'])
            cooking_steps.append(f"• Wash and cut {veg_list} into 1-inch pieces for even roasting")
        
        if categories['proteins']:
            protein_list = ', '.join(categories['proteins'])
            cooking_steps.append(f"• Cut {protein_list} into 1-inch cubes or strips")
        
        if categories['herbs_spices']:
            herb_list = ', '.join(categories['herbs_spices'])
            cooking_steps.append(f"• Mince {herb_list} finely and set aside")
        
        cooking_steps.append(f"• Preheat oven to 425°F (220°C) and position rack in the middle of the oven")
        
        # Combine all ingredients for roasting
        all_ingredient_list = []
        for category in ['vegetables', 'proteins']:
            if categories[category]:
                all_ingredient_list.extend(categories[category])
        
        if all_ingredient_list:
            ingredient_list = ', '.join(all_ingredient_list)
            cooking_steps.append(f"• Place {ingredient_list} on a large rimmed baking sheet, ensuring pieces are in a single layer with space between them for even cooking")
        
        cooking_steps.append(f"• Drizzle with 3 tablespoons olive oil and toss thoroughly to coat all pieces evenly")
        
        if categories['herbs_spices']:
            herb_list = ', '.join(categories['herbs_spices'])
            cooking_steps.append(f"• Sprinkle minced {herb_list} over the ingredients")
        
        if categories['condiments']:
            condiment_list = ', '.join(categories['condiments'])
            cooking_steps.append(f"• Drizzle {condiment_list} over the ingredients and toss to coat evenly")
        
        cooking_steps.append(f"• Season generously with 1 teaspoon salt and 1/2 teaspoon black pepper, tossing again to distribute seasonings")
        
        cooking_steps.append(f"• Roast in preheated oven for 25-30 minutes, stirring and flipping pieces halfway through cooking time for even browning")
        
        cooking_steps.append(f"• Remove from oven when all ingredients are tender, slightly caramelized, and edges are golden brown")
        
        cooking_steps.append(f"• Let rest for 5 minutes before serving to allow flavors to meld")
        
        instructions = '\n'.join(cooking_steps)
        
        # Generate a better recipe name for roasted dish
        def generate_roasted_name(ingredients, categories):
            if categories['vegetables'] and categories['proteins']:
                veg = categories['vegetables'][0].title()
                protein = categories['proteins'][0].title()
                return f"Roasted {veg} and {protein}"
            elif categories['vegetables']:
                veg = categories['vegetables'][0].title()
                return f"Roasted {veg} Medley"
            elif categories['proteins']:
                protein = categories['proteins'][0].title()
                return f"Roasted {protein}"
            else:
                return f"Roasted Vegetable Medley"
        
        roasted_name = generate_roasted_name(ingredients, categories)
        
        recipes.append({
            'name': roasted_name,
            'ingredients': all_ings,
            'instructions': instructions,
            'image': '🥕',
            'source': 'Generated',
            'cuisine': 'Mediterranean',
            'difficulty': 'Easy',
            'prep_time': '20 min',
            'cook_time': '30 min'
        })

    # Recipe 3: Hearty Soup (uses all ingredients)
    if len(ingredients) >= 2:
        soup_extras = ['8 cups chicken broth', '2 tbsp olive oil', '1 tsp salt', '1/2 tsp black pepper']
        all_ings = add_unique_ingredients(ingredients, soup_extras)
        
        # Create detailed cooking steps
        cooking_steps = []
        
        # Preparation steps
        if categories['vegetables']:
            veg_list = ', '.join(categories['vegetables'])
            cooking_steps.append(f"• Wash and cut {veg_list} into uniform, bite-sized pieces")
        
        if categories['proteins']:
            protein_list = ', '.join(categories['proteins'])
            cooking_steps.append(f"• Cut {protein_list} into bite-sized pieces")
        
        if categories['herbs_spices']:
            herb_list = ', '.join(categories['herbs_spices'])
            cooking_steps.append(f"• Mince {herb_list} finely")
        
        cooking_steps.append(f"• Heat 2 tablespoons olive oil in a large, heavy-bottomed pot over medium heat until oil is shimmering")
        
        if categories['herbs_spices']:
            herb_list = ', '.join(categories['herbs_spices'])
            cooking_steps.append(f"• Add minced {herb_list} and cook for 1 minute, stirring constantly, until fragrant but not browned")
        
        if categories['proteins']:
            protein_list = ', '.join(categories['proteins'])
            cooking_steps.append(f"• Add {protein_list} and cook for 3-4 minutes, stirring occasionally, until lightly browned")
        
        if categories['vegetables']:
            veg_list = ', '.join(categories['vegetables'])
            cooking_steps.append(f"• Add {veg_list} to the pot and stir to combine with other ingredients")
        
        if categories['condiments']:
            condiment_list = ', '.join(categories['condiments'])
            cooking_steps.append(f"• Add {condiment_list} to the pot and stir to combine")
        
        cooking_steps.append(f"• Pour in 8 cups of chicken broth and bring mixture to a gentle boil")
        
        cooking_steps.append(f"• Reduce heat to low and simmer uncovered for 25-30 minutes, stirring occasionally")
        
        cooking_steps.append(f"• Season with 1 teaspoon salt and 1/2 teaspoon black pepper to taste, starting with these amounts and adjusting as needed")
        
        cooking_steps.append(f"• Taste and adjust seasoning if needed, then serve hot")
        
        instructions = '\n'.join(cooking_steps)
        
        # Generate a better recipe name for soup
        def generate_soup_name(ingredients, categories):
            if categories['proteins'] and categories['vegetables']:
                protein = categories['proteins'][0].title()
                veg = categories['vegetables'][0].title()
                return f"{protein} and {veg} Soup"
            elif categories['proteins']:
                protein = categories['proteins'][0].title()
                return f"{protein} Soup"
            elif categories['vegetables']:
                veg = categories['vegetables'][0].title()
                return f"{veg} Soup"
            else:
                return f"Comfort Soup"
        
        soup_name = generate_soup_name(ingredients, categories)
        
        recipes.append({
            'name': soup_name,
            'ingredients': all_ings,
            'instructions': instructions,
            'image': '🍲',
            'source': 'Generated',
            'cuisine': 'International',
            'difficulty': 'Easy',
            'prep_time': '25 min',
            'cook_time': '35 min'
        })

    # Recipe 4: Pasta Dish (uses all ingredients)
    if len(ingredients) >= 2:
        pasta_extras = ['1 lb spaghetti', '3 tbsp olive oil', '1/2 cup parmesan cheese', '1 tsp salt', '1/2 tsp black pepper']
        all_ings = add_unique_ingredients(ingredients, pasta_extras)
        
        # Create detailed cooking steps
        cooking_steps = []
        
        # Preparation steps
        if categories['vegetables']:
            veg_list = ', '.join(categories['vegetables'])
            cooking_steps.append(f"• Wash and cut {veg_list} into small, uniform pieces")
        
        if categories['proteins']:
            protein_list = ', '.join(categories['proteins'])
            cooking_steps.append(f"• Cut {protein_list} into bite-sized pieces")
        
        if categories['herbs_spices']:
            herb_list = ', '.join(categories['herbs_spices'])
            cooking_steps.append(f"• Mince {herb_list} finely")
        
        cooking_steps.append(f"• Bring a large pot of water to a rolling boil and add 2 tablespoons salt to season the pasta water")
        
        cooking_steps.append(f"• Cook 1 pound of spaghetti in the boiling water according to package directions until al dente (usually 8-10 minutes)")
        
        cooking_steps.append(f"• While pasta cooks, heat 3 tablespoons olive oil in a large skillet over medium heat until oil is shimmering")
        
        if categories['herbs_spices']:
            herb_list = ', '.join(categories['herbs_spices'])
            cooking_steps.append(f"• Add minced {herb_list} and cook for 1 minute, stirring constantly, until fragrant but not browned")
        
        if categories['proteins']:
            protein_list = ', '.join(categories['proteins'])
            cooking_steps.append(f"• Add {protein_list} and cook for 3-4 minutes, stirring occasionally, until nearly cooked through")
        
        if categories['vegetables']:
            veg_list = ', '.join(categories['vegetables'])
            cooking_steps.append(f"• Add {veg_list} and sauté for 4-5 minutes, stirring occasionally, until tender and slightly caramelized")
        
        if categories['condiments']:
            condiment_list = ', '.join(categories['condiments'])
            cooking_steps.append(f"• Add {condiment_list} and stir to combine")
        
        cooking_steps.append(f"• Drain pasta, reserving 1 cup of pasta water")
        
        cooking_steps.append(f"• Add cooked pasta to the skillet with ingredients and toss to combine")
        
        cooking_steps.append(f"• Add 1/2 cup parmesan cheese and toss until cheese melts and coats pasta")
        
        cooking_steps.append(f"• Season with 1 teaspoon salt and 1/2 teaspoon black pepper to taste")
        
        cooking_steps.append(f"• If needed, add reserved pasta water 1/4 cup at a time to create a creamy sauce")
        
        cooking_steps.append(f"• Serve immediately with extra parmesan cheese on top")
        
        instructions = '\n'.join(cooking_steps)
        
        # Generate a better recipe name for pasta
        def generate_pasta_name(ingredients, categories):
            if categories['proteins'] and categories['vegetables']:
                protein = categories['proteins'][0].title()
                veg = categories['vegetables'][0].title()
                return f"Pasta with {protein} and {veg}"
            elif categories['proteins']:
                protein = categories['proteins'][0].title()
                return f"Pasta with {protein}"
            elif categories['vegetables']:
                veg = categories['vegetables'][0].title()
                return f"Pasta with {veg}"
            else:
                return f"Simple Pasta"
        
        pasta_name = generate_pasta_name(ingredients, categories)
        
        recipes.append({
            'name': pasta_name,
            'ingredients': all_ings,
            'instructions': instructions,
            'image': '🍝',
            'source': 'Generated',
            'cuisine': 'Italian',
            'difficulty': 'Easy',
            'prep_time': '20 min',
            'cook_time': '15 min'
        })

    return recipes

def clean_recipe_data(recipe_data):
    """Clean and validate recipe data"""
    if not recipe_data:
        return None
    
    # Ensure all required fields exist
    cleaned_recipe = {
        'name': recipe_data.get('title', recipe_data.get('name', 'Delicious Recipe')),
        'ingredients': [],
        'instructions': recipe_data.get('instructions', 'Follow the recipe instructions.'),
        'image': recipe_data.get('image', random.choice(FOOD_EMOJIS)),
        'source': recipe_data.get('source', 'Spoonacular'),
        'cuisine': recipe_data.get('cuisines', ['International'])[0] if recipe_data.get('cuisines') else 'International',
        'difficulty': 'Medium',
        'prep_time': f"{recipe_data.get('preparationMinutes', 20)} min" if recipe_data.get('preparationMinutes') else '20 min',
        'cook_time': f"{recipe_data.get('cookingMinutes', 30)} min" if recipe_data.get('cookingMinutes') else '30 min'
    }
    
    # Handle ingredients properly
    if 'extendedIngredients' in recipe_data:
        cleaned_recipe['ingredients'] = [ingredient.get('name', 'Unknown ingredient') for ingredient in recipe_data['extendedIngredients']]
    elif 'usedIngredients' in recipe_data:
        cleaned_recipe['ingredients'] = [ingredient.get('name', 'Unknown ingredient') for ingredient in recipe_data['usedIngredients']]
    else:
        cleaned_recipe['ingredients'] = ['Ingredient list not available']
    
    # Ensure ingredients list is not empty
    if not cleaned_recipe['ingredients']:
        cleaned_recipe['ingredients'] = ['Ingredient list not available']
    
    # Format instructions properly - handle both string and array formats
    instructions = cleaned_recipe['instructions']
    if isinstance(instructions, list):
        # If instructions is an array of steps, format them properly
        formatted_instructions = []
        for step in instructions:
            if isinstance(step, dict) and 'step' in step:
                formatted_instructions.append(step['step'])
            elif isinstance(step, str):
                formatted_instructions.append(step)
        cleaned_recipe['instructions'] = '\n'.join(formatted_instructions)
    elif isinstance(instructions, str):
        # If instructions is a string, clean it up and ensure proper formatting
        lines = instructions.split('\n')
        cleaned_lines = []
        seen_lines = set()  # Track seen lines to avoid duplicates
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove leading numbers and dots from instruction lines
                line = re.sub(r'^\d+\.\s*', '', line)
                # Only add if we haven't seen this line before (case-insensitive)
                line_lower = line.lower()
                if line_lower not in seen_lines:
                    cleaned_lines.append(line)
                    seen_lines.add(line_lower)
        
        cleaned_recipe['instructions'] = '\n'.join(cleaned_lines)
    
    # Ensure instructions are not empty or too short
    if not cleaned_recipe['instructions'] or len(cleaned_recipe['instructions'].strip()) < 10:
        # Generate basic instructions if none provided
        ingredients_text = ', '.join(cleaned_recipe['ingredients'][:3])
        cleaned_recipe['instructions'] = f"""• Gather all ingredients: {ingredients_text}
• Prepare your cooking equipment
• Follow the recipe method for best results
• Cook ingredients according to their requirements
• Season to taste with salt and pepper
• Serve hot and fresh
• Enjoy your delicious meal!"""
    
    # Limit instructions to maximum 10 steps
    if cleaned_recipe['instructions']:
        lines = cleaned_recipe['instructions'].split('\n')
        step_lines = []
        for line in lines:
            line = line.strip()
            if line and line.startswith('•'):
                step_lines.append(line)
                if len(step_lines) >= 10:  # Limit to 10 steps
                    break
        
        if step_lines:
            cleaned_recipe['instructions'] = '\n'.join(step_lines)
    
    # Add cooking time and serving size
    cleaned_recipe['cooking_time'] = recipe_data.get('readyInMinutes', 30)
    cleaned_recipe['servings'] = recipe_data.get('servings', 4)
    
    # Ensure image URL is valid
    if not cleaned_recipe['image'] or cleaned_recipe['image'].startswith('http'):
        cleaned_recipe['image'] = random.choice(FOOD_EMOJIS)
    
    return cleaned_recipe

@app.route('/api/recipes', methods=['POST'])
def generate_recipes():
    data = request.get_json()
    selected_ingredients = data.get('ingredients', [])
    
    if not selected_ingredients or not isinstance(selected_ingredients, list):
        return jsonify({'error': 'No ingredients provided'}), 400

    print(f"🎯 Looking for recipes using: {selected_ingredients}")

    # Try to get recipes from Spoonacular first
    spoonacular_recipes = search_spoonacular_recipes(selected_ingredients, 15)  # Get more recipes to filter from
    
    if spoonacular_recipes:
        print("✅ Found recipes from Spoonacular API")
        # Process and filter Spoonacular recipes to prioritize those using more ingredients
        processed_recipes = []
        
        for recipe in spoonacular_recipes:
            # Get detailed recipe information
            recipe_detail = get_recipe_instructions(recipe['id'])
            
            if recipe_detail:
                cleaned_recipe = clean_recipe_data(recipe_detail)
                if cleaned_recipe:
                    # Calculate how many of our ingredients are used in this recipe
                    recipe_ingredients = []
                    if 'extendedIngredients' in recipe_detail:
                        recipe_ingredients = [ing['name'].lower() for ing in recipe_detail['extendedIngredients']]
                    elif 'ingredients' in cleaned_recipe:
                        recipe_ingredients = [ing.lower() for ing in cleaned_recipe['ingredients']]
                    
                    # Count how many of our selected ingredients are used
                    selected_lower = [ing.lower() for ing in selected_ingredients]
                    used_count = sum(1 for ing in selected_lower if any(ing in recipe_ing for recipe_ing in recipe_ingredients))
                    
                    # Add usage percentage to recipe data
                    cleaned_recipe['ingredient_usage'] = {
                        'used': used_count,
                        'total': len(selected_ingredients),
                        'percentage': round((used_count / len(selected_ingredients)) * 100, 1)
                    }
                    
                    processed_recipes.append(cleaned_recipe)
            else:
                # Fallback if detailed info not available
                cleaned_recipe = clean_recipe_data(recipe)
                if cleaned_recipe:
                    # Estimate usage from the basic recipe data
                    used_count = recipe.get('usedIngredientCount', 0)
                    cleaned_recipe['ingredient_usage'] = {
                        'used': used_count,
                        'total': len(selected_ingredients),
                        'percentage': round((used_count / len(selected_ingredients)) * 100, 1)
                    }
                    processed_recipes.append(cleaned_recipe)
        
        # Sort recipes by ingredient usage percentage (highest first)
        processed_recipes.sort(key=lambda x: x.get('ingredient_usage', {}).get('percentage', 0), reverse=True)
        
        # Count how many recipes use all ingredients
        full_usage_recipes = [r for r in processed_recipes if r.get('ingredient_usage', {}).get('percentage', 0) == 100.0]
        partial_usage_recipes = [r for r in processed_recipes if r.get('ingredient_usage', {}).get('percentage', 0) < 100.0]
        
        print(f"📊 Found {len(full_usage_recipes)} recipes using all ingredients, {len(partial_usage_recipes)} partial usage")
        
        # If we don't have enough recipes using all ingredients, add fallback recipes
        if len(full_usage_recipes) < 3:
            print("🎨 Adding fallback recipes to ensure at least 3 recipes use all ingredients")
            fallback_recipes = generate_fallback_recipes(selected_ingredients)
            # Add usage information to fallback recipes
            for recipe in fallback_recipes:
                recipe['ingredient_usage'] = {
                    'used': len(selected_ingredients),
                    'total': len(selected_ingredients),
                    'percentage': 100.0
                }
            # Combine API recipes with fallback recipes, prioritizing full usage
            combined_recipes = full_usage_recipes + fallback_recipes + partial_usage_recipes
            # Take the top 10 recipes total
            final_recipes = combined_recipes[:10]
            print(f"📊 Final recipe count: {len([r for r in final_recipes if r.get('ingredient_usage', {}).get('percentage', 0) == 100.0])} full usage, {len([r for r in final_recipes if r.get('ingredient_usage', {}).get('percentage', 0) < 100.0])} partial usage")
            return jsonify(final_recipes)
        else:
            # We have enough full usage recipes, just return the top 10
            final_recipes = processed_recipes[:10]
            print(f"📊 Recipe usage stats: {[f'{r.get('ingredient_usage', {}).get('percentage', 0)}%' for r in final_recipes[:3]]}")
            return jsonify(final_recipes)
    
    # Use enhanced fallback recipe generation (guarantees using ALL ingredients)
    print("🎨 Using creative fallback recipe generation (100% ingredient usage)")
    fallback_recipes = generate_fallback_recipes(selected_ingredients)
    
    # Add usage information to fallback recipes
    for recipe in fallback_recipes:
        recipe['ingredient_usage'] = {
            'used': len(selected_ingredients),
            'total': len(selected_ingredients),
            'percentage': 100.0
        }
    
    return jsonify(fallback_recipes)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Dish Discovery API is running',
        'timestamp': datetime.now().isoformat()
    })

# Calendar Scheduling Routes
@app.route('/api/calendar/schedule', methods=['POST'])
def schedule_meal():
    """Schedule a meal for a specific date"""
    try:
        data = request.get_json()
        date = data.get('date')
        meal_type = data.get('meal_type', 'dinner')  # breakfast, lunch, dinner
        recipe = data.get('recipe')
        
        if not date or not recipe:
            return jsonify({'error': 'Date and recipe are required'}), 400
        
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Store the scheduled meal
        if date not in scheduled_meals:
            scheduled_meals[date] = {}
        
        scheduled_meals[date][meal_type] = {
            'recipe': recipe,
            'scheduled_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'message': f'Meal scheduled for {date} ({meal_type})',
            'scheduled_meal': scheduled_meals[date][meal_type]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/schedule', methods=['GET'])
def get_scheduled_meals():
    """Get scheduled meals for a date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400
        
        # Validate date formats
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get meals in the date range
        meals_in_range = {}
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            if date_str in scheduled_meals:
                meals_in_range[date_str] = scheduled_meals[date_str]
            current += timedelta(days=1)
        
        return jsonify({
            'scheduled_meals': meals_in_range,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/schedule/<date>/<meal_type>', methods=['DELETE'])
def remove_scheduled_meal(date, meal_type):
    """Remove a scheduled meal"""
    try:
        if date in scheduled_meals and meal_type in scheduled_meals[date]:
            removed_meal = scheduled_meals[date].pop(meal_type)
            
            # Clean up empty date entries
            if not scheduled_meals[date]:
                del scheduled_meals[date]
            
            return jsonify({
                'message': f'Meal removed from {date} ({meal_type})',
                'removed_meal': removed_meal
            })
        else:
            return jsonify({'error': 'Meal not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/week', methods=['GET'])
def get_week_schedule():
    """Get scheduled meals for the current week"""
    try:
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        week_schedule = {}
        current = start_of_week
        while current <= end_of_week:
            date_str = current.strftime('%Y-%m-%d')
            if date_str in scheduled_meals:
                week_schedule[date_str] = scheduled_meals[date_str]
            current += timedelta(days=1)
        
        return jsonify({
            'week_schedule': week_schedule,
            'week_range': {
                'start_date': start_of_week.strftime('%Y-%m-%d'),
                'end_date': end_of_week.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/month', methods=['GET'])
def get_month_schedule():
    """Get all scheduled meals for the current month"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # Get all dates in the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        month_schedule = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str in scheduled_meals:
                month_schedule[date_str] = scheduled_meals[date_str]
            current_date += timedelta(days=1)
        
        return jsonify(month_schedule)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/expiring', methods=['GET'])
def get_expiring_ingredients():
    """Get ingredients that are expiring soon and suggest recipes for them"""
    try:
        # This endpoint will be called by the frontend to get expiring ingredients
        # The frontend will send the ingredients data from localStorage
        return jsonify({'message': 'Reminder endpoint ready'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/recipes-for-expiring', methods=['POST'])
def get_recipes_for_expiring_ingredients():
    """Get recipe suggestions for ingredients that are expiring soon"""
    try:
        data = request.get_json()
        expiring_ingredients = data.get('ingredients', [])
        
        if not expiring_ingredients:
            return jsonify({'recipes': [], 'message': 'No expiring ingredients provided'})
        
        # Get recipe names for the expiring ingredients
        ingredient_names = [ing['name'] for ing in expiring_ingredients]
        
        # Search for recipes using these ingredients
        recipes = search_spoonacular_recipes(ingredient_names, number=5)
        
        # If no API recipes found, generate fallback recipes
        if not recipes:
            recipes = generate_fallback_recipes(ingredient_names)
        
        # Add expiration info to each recipe
        for recipe in recipes:
            recipe['expiring_ingredients'] = ingredient_names
            recipe['urgency'] = 'high' if any(ing.get('days_until_expiry', 0) <= 1 for ing in expiring_ingredients) else 'medium'
        
        return jsonify({
            'recipes': recipes,
            'expiring_ingredients': expiring_ingredients,
            'message': f'Found {len(recipes)} recipes for your expiring ingredients'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🍽️ Dish Discovery API Server Starting...")
    print("🌐 API Provider: Spoonacular")
    print("🔑 API Key: Configured")
    print("🎨 Creative Fallback: Enabled")
    print("📅 Calendar Scheduling: Enabled")
    print("🌐 API Endpoints:")
    print("   - POST /api/recipes - Generate recipes")
    print("   - GET /api/health - Health check")
    print("   - POST /api/calendar/schedule - Schedule a meal")
    print("   - GET /api/calendar/schedule - Get scheduled meals")
    print("   - DELETE /api/calendar/schedule/<date>/<meal> - Remove meal")
    print("   - GET /api/calendar/week - Get week schedule")
    print("   - GET /api/calendar/month - Get month schedule")
    print("📁 Open dishdiscovery.html in your browser")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001) 