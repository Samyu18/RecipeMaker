from flask import Flask, send_from_directory, request, jsonify
import requests
import os

app = Flask(__name__, static_folder='.', static_url_path='')

MEALDB_FILTER_URL = 'https://www.themealdb.com/api/json/v1/1/filter.php?i='
MEALDB_LOOKUP_URL = 'https://www.themealdb.com/api/json/v1/1/lookup.php?i='

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/recipes')
def get_recipes():
    ingredients = request.args.get('ingredients', '')
    if not ingredients:
        return jsonify({'meals': []})
    first_ingredient = ingredients.split(',')[0].strip()
    res = requests.get(MEALDB_FILTER_URL + first_ingredient)
    data = res.json()
    if not data.get('meals'):
        return jsonify({'meals': []})
    all_ingredients = [i.strip().lower() for i in ingredients.split(',')]
    detailed_meals = []
    for meal in data['meals'][:30]:  # Increase to 30
        detail_res = requests.get(MEALDB_LOOKUP_URL + meal['idMeal'])
        detail_data = detail_res.json()
        meal_detail = detail_data['meals'][0]
        meal_ingredients = []
        for i in range(1, 21):
            ing = meal_detail.get(f'strIngredient{i}', None)
            if ing is not None:
                ing = ing.strip().lower()
                if ing:
                    meal_ingredients.append(ing)
        if all(ing in meal_ingredients for ing in all_ingredients):
            detailed_meals.append(meal_detail)
    return jsonify({'meals': detailed_meals})

@app.route('/api/recipe/<id>')
def get_recipe(id):
    res = requests.get(MEALDB_LOOKUP_URL + id)
    data = res.json()
    if not data.get('meals'):
        return jsonify({'meal': None})
    return jsonify({'meal': data['meals'][0]})

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True) 