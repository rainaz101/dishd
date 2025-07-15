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
    """Generate practical fallback recipes that use ALL selected ingredients, with comprehensive, non-repeating instructions"""
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
    
    recipes = []
    
    # Helper to add extra ingredients only if not already present
    def add_unique_ingredients(base, extras):
        base_lower = set(i.lower() for i in base)
        return base + [e for e in extras if e.lower() not in base_lower]

    # Helper to build comprehensive steps without repeating ingredients
    def build_comprehensive_steps(steps_data):
        used_ingredients = set()
        result = []
        
        for step_info in steps_data:
            desc, ings, step_num = step_info
            # Only include ingredients that haven't been used yet
            unused_ings = [i for i in ings if i.lower() not in used_ingredients]
            
            if unused_ings:
                used_ingredients.update(i.lower() for i in unused_ings)
                # Format the description with the unused ingredients
                formatted_desc = desc.format(ingredients=', '.join(unused_ings))
                result.append(f"{step_num}. {formatted_desc}")
            elif not ings:  # Step with no specific ingredients
                result.append(f"{step_num}. {desc}")
        
        return result

    # Recipe 1: Stir Fry (uses all ingredients)
    if len(ingredients) >= 2:
        stirfry_extras = ['soy sauce', 'sesame oil', 'garlic', 'ginger', 'vegetable oil', 'salt', 'black pepper']
        all_ings = add_unique_ingredients(ingredients, stirfry_extras)
        
        steps_data = [
            ("Heat 2 tablespoons vegetable oil in a large wok or deep skillet over high heat until oil is shimmering.", ['vegetable oil'], 1),
            ("Add minced garlic and ginger, stir-fry for 30 seconds until fragrant and golden.", ['garlic', 'ginger'], 2),
            ("Add {ingredients} and stir-fry for 3-4 minutes, tossing constantly until vegetables are bright in color and slightly tender.", ingredients, 3),
            ("Pour in 2 tablespoons soy sauce and 1 tablespoon sesame oil, tossing to coat all ingredients evenly.", ['soy sauce', 'sesame oil'], 4),
            ("Season with salt and black pepper to taste, continuing to stir-fry for 1-2 minutes.", ['salt', 'black pepper'], 5),
            ("Remove from heat when vegetables are tender-crisp and serve immediately over steamed rice or noodles.", [], 6),
        ]
        
        instructions = [
            "COOKING STEPS:",
        ]
        instructions += build_comprehensive_steps(steps_data)
        instructions += [
            "",
            "COOKING TIPS:",
            "• Keep the heat high throughout cooking for authentic stir-fry texture",
            "• Don't overcrowd the pan - cook in batches if needed",
            "• Stir constantly to prevent burning and ensure even cooking",
            "• Vegetables should be tender-crisp, not mushy",
            "• Serve immediately for best texture and flavor",
            "",
            "TIMING:",
            "• Preparation time: 15 minutes",
            "• Cooking time: 8-10 minutes",
            "• Total time: 25 minutes",
            "• Servings: 4 people"
        ]
        
        recipes.append({
            'name': f"Wok-Tossed {', '.join(ingredients[:2]).title()} Delight",
            'ingredients': all_ings,
            'instructions': '\n'.join(instructions),
            'image': '🥘',
            'source': 'Practical Recipe',
            'cuisine': 'Asian',
            'difficulty': 'Easy',
            'prep_time': '15 min',
            'cook_time': '10 min'
        })
    
    # Recipe 2: Roasted Vegetables (uses all ingredients)
    if len(ingredients) >= 2:
        roast_extras = ['olive oil', 'garlic', 'rosemary', 'thyme', 'salt', 'black pepper']
        all_ings = add_unique_ingredients(ingredients, roast_extras)
        
        steps_data = [
            ("Preheat oven to 425°F (220°C) and position rack in the middle of the oven.", [], 1),
            ("Wash and cut {ingredients} into similar-sized pieces, approximately 1-inch cubes or wedges.", ingredients, 2),
            ("Place {ingredients} on a large rimmed baking sheet, ensuring pieces are in a single layer with space between them.", ingredients, 3),
            ("Drizzle with 3 tablespoons olive oil and toss thoroughly to coat all pieces evenly.", ['olive oil'], 4),
            ("Sprinkle minced garlic, chopped fresh rosemary, and thyme over the vegetables.", ['garlic', 'rosemary', 'thyme'], 5),
            ("Season generously with salt and black pepper, tossing again to distribute seasonings.", ['salt', 'black pepper'], 6),
            ("Roast in preheated oven for 25-30 minutes, stirring and flipping pieces halfway through cooking time.", [], 7),
            ("Remove from oven when vegetables are tender, slightly caramelized, and edges are golden brown.", [], 8),
            ("Let rest for 5 minutes before serving to allow flavors to meld.", [], 9),
        ]
        
        instructions = [
            "COOKING STEPS:",
        ]
        instructions += build_comprehensive_steps(steps_data)
        instructions += [
            "",
            "COOKING TIPS:",
            "• Cut vegetables to similar sizes for even cooking",
            "• Don't overcrowd the baking sheet - use two sheets if needed",
            "• Stir halfway through for even browning and cooking",
            "• Adjust cooking time based on vegetable types and sizes",
            "• Vegetables should be tender but not mushy",
            "",
            "TIMING:",
            "• Preparation time: 20 minutes",
            "• Cooking time: 30 minutes",
            "• Total time: 50 minutes",
            "• Servings: 6 people"
        ]
        
        recipes.append({
            'name': f"Golden Roasted {', '.join(ingredients[:2]).title()} Medley",
            'ingredients': all_ings,
            'instructions': '\n'.join(instructions),
            'image': '🥕',
            'source': 'Practical Recipe',
            'cuisine': 'Mediterranean',
            'difficulty': 'Easy',
            'prep_time': '20 min',
            'cook_time': '30 min'
        })
    
    # Recipe 3: Hearty Soup (uses all ingredients)
    if len(ingredients) >= 2:
        soup_extras = ['chicken broth', 'onion', 'garlic', 'olive oil', 'bay leaves', 'salt', 'black pepper']
        all_ings = add_unique_ingredients(ingredients, soup_extras)
        
        steps_data = [
            ("Wash and cut {ingredients} into uniform, bite-sized pieces. Dice 1 large onion and mince 4 cloves garlic.", ingredients + ['onion', 'garlic'], 1),
            ("Heat 2 tablespoons olive oil in a large, heavy-bottomed pot over medium heat until oil is shimmering.", ['olive oil'], 2),
            ("Add diced onion and sauté for 5-6 minutes, stirring occasionally, until onions are translucent and softened.", ['onion'], 3),
            ("Add minced garlic and cook for 1 minute, stirring constantly, until fragrant but not browned.", ['garlic'], 4),
            ("Add {ingredients} to the pot and stir to combine with onions and garlic.", ingredients, 5),
            ("Pour in 8 cups of chicken broth and add 2 bay leaves. Bring mixture to a gentle boil.", ['chicken broth', 'bay leaves'], 6),
            ("Reduce heat to low and simmer uncovered for 25-30 minutes, stirring occasionally.", [], 7),
            ("Season with salt and black pepper to taste, starting with 1 teaspoon salt and 1/2 teaspoon black pepper.", ['salt', 'black pepper'], 8),
            ("Remove bay leaves before serving. Taste and adjust seasoning if needed.", ['bay leaves'], 9),
        ]
        
        instructions = [
            "COOKING STEPS:",
        ]
        instructions += build_comprehensive_steps(steps_data)
        instructions += [
            "",
            "COOKING TIPS:",
            "• Use homemade or high-quality chicken broth for better flavor",
            "• Simmer gently to develop flavors without overcooking vegetables",
            "• Taste and adjust seasoning throughout cooking process",
            "• Let soup rest for 10 minutes before serving to allow flavors to meld",
            "• Soup can be made ahead and reheated gently",
            "",
            "TIMING:",
            "• Preparation time: 25 minutes",
            "• Cooking time: 35 minutes",
            "• Total time: 60 minutes",
            "• Servings: 6 people"
        ]
        
        recipes.append({
            'name': f"Savory {', '.join(ingredients[:2]).title()} Comfort Soup",
            'ingredients': all_ings,
            'instructions': '\n'.join(instructions),
            'image': '🍲',
            'source': 'Practical Recipe',
            'cuisine': 'International',
            'difficulty': 'Easy',
            'prep_time': '25 min',
            'cook_time': '35 min'
        })
    
    # Recipe 4: Pasta Dish (uses all ingredients)
    if len(ingredients) >= 2:
        pasta_extras = ['spaghetti', 'olive oil', 'garlic', 'basil', 'parmesan cheese', 'salt', 'black pepper']
        all_ings = add_unique_ingredients(ingredients, pasta_extras)
        
        steps_data = [
            ("Bring a large pot of water to a rolling boil and add 2 tablespoons salt to season the pasta water.", ['salt'], 1),
            ("Wash and cut {ingredients} into small, uniform pieces suitable for pasta.", ingredients, 2),
            ("Cook 1 pound of spaghetti in the boiling water according to package directions until al dente (usually 8-10 minutes).", ['spaghetti'], 3),
            ("While pasta cooks, heat 3 tablespoons olive oil in a large skillet over medium heat until oil is shimmering.", ['olive oil'], 4),
            ("Add minced garlic and cook for 1 minute, stirring constantly, until fragrant but not browned.", ['garlic'], 5),
            ("Add {ingredients} and sauté for 6-7 minutes, stirring occasionally, until vegetables are tender and slightly caramelized.", ingredients, 6),
            ("Drain pasta, reserving 1 cup of the starchy cooking water for sauce consistency.", ['spaghetti'], 7),
            ("Add cooked pasta to the skillet with vegetables and toss to combine thoroughly.", ['spaghetti'], 8),
            ("Add reserved pasta water gradually, tossing constantly, until sauce coats pasta evenly (use 1/2 to 1 cup).", [], 9),
            ("Season with salt and black pepper to taste, then serve immediately with grated parmesan cheese and fresh basil.", ['salt', 'black pepper', 'parmesan cheese', 'basil'], 10),
        ]
        
        instructions = [
            "COOKING STEPS:",
        ]
        instructions += build_comprehensive_steps(steps_data)
        instructions += [
            "",
            "COOKING TIPS:",
            "• Salt the pasta water well - it should taste like seawater",
            "• Cook pasta until al dente (firm to the bite)",
            "• Reserve pasta water for sauce consistency",
            "• Don't rinse the pasta after draining",
            "• Toss pasta with sauce immediately while hot",
            "",
            "TIMING:",
            "• Preparation time: 20 minutes",
            "• Cooking time: 15 minutes",
            "• Total time: 35 minutes",
            "• Servings: 4 people"
        ]
        
        recipes.append({
            'name': f"Garden Fresh {', '.join(ingredients[:2]).title()} Pasta",
            'ingredients': all_ings,
            'instructions': '\n'.join(instructions),
            'image': '🍝',
            'source': 'Practical Recipe',
            'cuisine': 'Italian',
            'difficulty': 'Easy',
            'prep_time': '20 min',
            'cook_time': '15 min'
        })
    
    # Recipe 5: Fresh Salad (uses all ingredients)
    if len(ingredients) >= 2:
        salad_extras = ['olive oil', 'lemon juice', 'garlic', 'honey', 'salt', 'black pepper']
        all_ings = add_unique_ingredients(ingredients, salad_extras)
        
        steps_data = [
            ("Wash and thoroughly dry all {ingredients}. Cut into uniform, bite-sized pieces suitable for salad.", ingredients, 1),
            ("In a small bowl, whisk together 3 tablespoons olive oil, 2 tablespoons fresh lemon juice, and 1 teaspoon honey until emulsified.", ['olive oil', 'lemon juice', 'honey'], 2),
            ("Add minced garlic, 1/2 teaspoon salt, and 1/4 teaspoon black pepper to the dressing and whisk to combine.", ['garlic', 'salt', 'black pepper'], 3),
            ("Place {ingredients} in a large salad bowl and drizzle with half of the prepared dressing.", ingredients, 4),
            ("Toss salad gently to coat ingredients evenly with dressing, being careful not to bruise delicate ingredients.", [], 5),
            ("Let salad rest for 5 minutes to allow flavors to meld, then serve with remaining dressing on the side.", [], 6),
        ]
        
        instructions = [
            "COOKING STEPS:",
        ]
        instructions += build_comprehensive_steps(steps_data)
        instructions += [
            "",
            "COOKING TIPS:",
            "• Use fresh, crisp ingredients for best texture",
            "• Don't overdress the salad - start with less dressing",
            "• Toss gently to avoid bruising delicate ingredients",
            "• Serve immediately to maintain crispness and freshness",
            "• You can add protein like grilled chicken or nuts for extra nutrition",
            "",
            "TIMING:",
            "• Preparation time: 20 minutes",
            "• Resting time: 5 minutes",
            "• Total time: 25 minutes",
            "• Servings: 4 people"
        ]
        
        recipes.append({
            'name': f"Sun-Kissed {', '.join(ingredients[:2]).title()} Garden Salad",
            'ingredients': all_ings,
            'instructions': '\n'.join(instructions),
            'image': '🥗',
            'source': 'Practical Recipe',
            'cuisine': 'Mediterranean',
            'difficulty': 'Easy',
            'prep_time': '20 min',
            'cook_time': '0 min'
        })
    
    # Recipe 6: Skillet Dish (uses all ingredients)
    if len(ingredients) >= 2:
        skillet_extras = ['olive oil', 'garlic', 'herbs', 'butter', 'salt', 'black pepper']
        all_ings = add_unique_ingredients(ingredients, skillet_extras)
        
        steps_data = [
            ("Wash and cut {ingredients} into uniform pieces. Mince 3 cloves garlic and chop 2 tablespoons fresh herbs.", ingredients + ['garlic', 'herbs'], 1),
            ("Heat 2 tablespoons olive oil and 1 tablespoon butter in a large skillet over medium heat until butter is melted and oil is shimmering.", ['olive oil', 'butter'], 2),
            ("Add minced garlic and cook for 1 minute, stirring constantly, until fragrant but not browned.", ['garlic'], 3),
            ("Add {ingredients} and cook for 4-5 minutes, stirring occasionally, until vegetables are bright in color and slightly tender.", ingredients, 4),
            ("Add chopped fresh herbs and season with 1/2 teaspoon salt and 1/4 teaspoon black pepper.", ['herbs', 'salt', 'black pepper'], 5),
            ("Continue cooking for 3-4 minutes, stirring occasionally, until all ingredients are tender and flavors are well combined.", [], 6),
            ("Remove from heat and let rest for 2 minutes before serving to allow flavors to meld.", [], 7),
        ]
        
        instructions = [
            "COOKING STEPS:",
        ]
        instructions += build_comprehensive_steps(steps_data)
        instructions += [
            "",
            "COOKING TIPS:",
            "• Don't overcrowd the skillet - cook in batches if needed",
            "• Cook ingredients in order of cooking time needed",
            "• Season gradually and taste as you go",
            "• Use fresh herbs for best flavor and aroma",
            "• Vegetables should be tender but still have some texture",
            "",
            "TIMING:",
            "• Preparation time: 20 minutes",
            "• Cooking time: 12 minutes",
            "• Total time: 32 minutes",
            "• Servings: 4 people"
        ]
        
        recipes.append({
            'name': f"Cast-Iron {', '.join(ingredients[:2]).title()} Skillet",
            'ingredients': all_ings,
            'instructions': '\n'.join(instructions),
            'image': '🍳',
            'source': 'Practical Recipe',
            'cuisine': 'International',
            'difficulty': 'Easy',
            'prep_time': '20 min',
            'cook_time': '12 min'
        })

    return recipes[:6]  # Return maximum 6 recipes

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
        # If instructions is an array of steps, format them without numbering
        formatted_instructions = []
        for step in instructions:
            if isinstance(step, dict) and 'step' in step:
                formatted_instructions.append(step['step'])
            elif isinstance(step, str):
                formatted_instructions.append(step)
        cleaned_recipe['instructions'] = '\n'.join(formatted_instructions)
    elif isinstance(instructions, str):
        # If instructions is a string, clean it up and remove any existing numbers
        # The frontend will handle the numbering
        lines = instructions.split('\n')
        cleaned_lines = []
        seen_lines = set()  # Track seen lines to avoid duplicates
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove leading numbers and dots from instruction lines (Python regex)
                line = re.sub(r'^\d+\.\s*', '', line)
                # Only add if we haven't seen this line before (case-insensitive)
                line_lower = line.lower()
                if line_lower not in seen_lines:
                    cleaned_lines.append(line)
                    seen_lines.add(line_lower)
        
        cleaned_recipe['instructions'] = '\n'.join(cleaned_lines)
    
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
    spoonacular_recipes = search_spoonacular_recipes(selected_ingredients, 10)
    
    if spoonacular_recipes:
        print("✅ Found recipes from Spoonacular API")
        # Process Spoonacular recipes
        processed_recipes = []
        for recipe in spoonacular_recipes[:10]:
            # Get detailed recipe information
            recipe_detail = get_recipe_instructions(recipe['id'])
            
            if recipe_detail:
                cleaned_recipe = clean_recipe_data(recipe_detail)
                if cleaned_recipe:
                    processed_recipes.append(cleaned_recipe)
            else:
                # Fallback if detailed info not available
                cleaned_recipe = clean_recipe_data(recipe)
                if cleaned_recipe:
                    processed_recipes.append(cleaned_recipe)
        
        if processed_recipes:
            return jsonify(processed_recipes)
    
    # Use enhanced fallback recipe generation
    print("🎨 Using creative fallback recipe generation")
    fallback_recipes = generate_fallback_recipes(selected_ingredients)
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
    """Get scheduled meals for the current month"""
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1)
        
        # Calculate end of month
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        month_schedule = {}
        current = start_of_month
        while current <= end_of_month:
            date_str = current.strftime('%Y-%m-%d')
            if date_str in scheduled_meals:
                month_schedule[date_str] = scheduled_meals[date_str]
            current += timedelta(days=1)
        
        return jsonify({
            'month_schedule': month_schedule,
            'month_range': {
                'start_date': start_of_month.strftime('%Y-%m-%d'),
                'end_date': end_of_month.strftime('%Y-%m-%d')
            }
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
    app.run(debug=True, host='0.0.0.0', port=5000) 