import requests
import random

# Global constants
basic_stats = ['height', 'weight']
max_pokemon_id = 151


# Function to allow User to choose the size of the pack
def choose_size_of_pack(max_size=10):
    # User chooses size of pack to play with
    print("**********************************")
    print("* Welcome to Pokemon Top Trumps! *")
    print("**********************************")
    print("The aim is to win all of you opponents Pokemon!")
    print("What size of pack would you like to play Pokemon with?")

    error = True
    while error:
        input_size_of_pack = input(f"Choose an even number between 2 and {max_size}: ")

        # Error check input (must be even)
        if input_size_of_pack.isnumeric():
            size_of_pack = int(input_size_of_pack)
            if 2 <= size_of_pack <= max_size:
                if (size_of_pack / 2).is_integer():
                    error = False
                else:
                    print(f"{size_of_pack} is not an even number")
            else:
                print(f"{input_size_of_pack} does not fall within 1 and {max_pokemon_id}")
        else:
            print(f"{input_size_of_pack} is not a number")

        # Remind the user of the valid input criteria
        if error:
            print(f"Input of size of pack must be an even number between 1 and {max_size}")
    return size_of_pack


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


# Function to compare the type data in the given Pokemon
def type_comparison(source_pokemon, comparison_pokemon, stat_choice, player):
    winner = player
    source_types = source_pokemon['types']
    for source_type in source_types:
        if source_type['name'] == stat_choice:
            source_type_strong_against = source_type['strong against']
            source_type_weak_against = source_type['weak against']
            break

    for type_data in comparison_pokemon['types']:
        if type_data['name'] in source_type_strong_against:
            if player == 'User':
                winner = 'User'
            else:
                winner = 'Computer'
            print(f"Type {stat_choice} is strong against {type_data['name']}")
            break
        elif type_data['name'] in source_type_weak_against:
            if player == 'User':
                winner = 'Computer'
            else:
                winner = 'User'
            print(f"Type {stat_choice} is weak against {type_data['name']}")
            break
        else:
            print(f"Type {stat_choice} has no effect on {type_data['name']}")
            winner = 'Draw'

    return winner


# Function to move the given Pokemon to the list of the given list
def move_to_end(pokemon_dic, pokemon):
    if len(pokemon_dic) != 0 and pokemon in pokemon_dic:
        pokemon_dic.remove(pokemon)
        pokemon_dic.append(pokemon)
