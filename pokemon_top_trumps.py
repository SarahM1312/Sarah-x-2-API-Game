import requests
import random

# Global constants
from PyQt5.QtWidgets import QInputDialog

max_pokemon_id = 151


# Generate a list of unique Pokemon IDs
def generate_pokemon_ids(ids_number, max_id, check_list=[]):
    pokemon_ids = []
    for pack_number in range(ids_number):
        random_id = random.randint(1, max_id)
        while (random_id in pokemon_ids) or (random_id in check_list):
            random_id = random.randint(1, max_id)
        pokemon_ids.append(random_id)
    return pokemon_ids


# Function to return a randomly generated list of Pokemon containing no duplicates
def generate_pokemon_list(pokemon_ids):
    # For each chosen Pokemon, retrieve data
    pokemon_list = []
    for pokemon_id in pokemon_ids:
        url = 'https://pokeapi.co/api/v2/pokemon/{}/'.format(pokemon_id)
        response = requests.get(url)
        pokemon = response.json()

        pokemon_types_list = retrieve_types_data(pokemon['types'])
        pokemon_list.append({'id': pokemon_id,
                             'name': pokemon['name'],
                             'height': pokemon['height'],
                             'weight': pokemon['weight'],
                             'types': pokemon_types_list})
    return pokemon_list


# Function to retrieve the types data
def retrieve_types_data(pokemon_types_list):
    # Retrieve types
    types_list = []
    for list_entry in pokemon_types_list:
        response = requests.get(list_entry['type']['url'])
        type_data = response.json()

        weak_against = []
        for sub_type in type_data['damage_relations']['double_damage_from']:
            weak_against.append(sub_type['name'])

        strong_against = []
        for sub_type in type_data['damage_relations']['double_damage_to']:
            strong_against.append(sub_type['name'])

        types_list.append({'name': list_entry['type']['name'],
                           'weak against': weak_against,
                           'strong against': strong_against})
    return types_list


# Function to move the given Pokemon to the list of the given list
def move_to_end(pokemon_dic, pokemon):
    if len(pokemon_dic) != 0 and pokemon in pokemon_dic:
        pokemon_dic.remove(pokemon)
        pokemon_dic.append(pokemon)

