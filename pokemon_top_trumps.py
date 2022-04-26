import requests
import random

# Global constants
basic_stats = ['height', 'weight']
max_pokemon_id = 151


# Function to allow User to choose the size of the pack
def choose_size_of_pack(max_size=10):
    # User chooses size of pack to play with
    print("**********************************")
    print("* Welcome to Pokemon Top Trumps!! *")
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


# Function to perform a round of the game
def game_round(player, user_pokemon_dic, computer_pokemon_dic):
    print("You can choose one of the following pokemon's :")
    name_list = []
    for user_pokemon_dics in user_pokemon_dic:
        random.randint(0, int(len(user_pokemon_dic)))
        name_list.append(user_pokemon_dics["name"])
        print(user_pokemon_dics["name"])

    user_pokemon_name = input("Which pokemon do you want to use?\n")

    user_pokemon = user_pokemon_dic[name_list.index(user_pokemon_name)]
    
    computer_pokemon = computer_pokemon_dic[0]

    # Display whose turn it is
    if player == 'User':
        print(f"\n**************")
        print(f"* YOUR TURN! *")
        print(f"**************")
    else:
        print(f"\n********************")
        print(f"* COMPUTER'S TURN! *")
        print(f"********************")

    # Display User Pokemon statistics
    allowed_stats = display_pokemon_stats(user_pokemon, 'User')

    # Determine which statistic to compare
    if player == 'User':
        # If it's the User's turn, prompt User for choice
        stat_choice = input(f"Which statistic would you like to play? Choose from {allowed_stats} ")
        while stat_choice not in allowed_stats:
            stat_choice = input(f"Which statistic would you like to play? Choose from {allowed_stats} ")

        # Display Computer Pokemon statistics
        display_pokemon_stats(computer_pokemon, '\nComputer')
    else:
        # Display Computer Pokemon statistics
        allowed_stats = display_pokemon_stats(computer_pokemon, 'Computer')

        # If it's the Computer's turn, select choice randomly
        stat_choice = allowed_stats[random.randint(0, len(allowed_stats))]

        # Report to the User what the Computer's choice was
        input(f"The Computer has chosen the statistic {stat_choice}. Press <Enter> to continue...\n")

    winner = 'User'
    if stat_choice == 'height' or stat_choice == 'weight':
        if user_pokemon[stat_choice] > computer_pokemon[stat_choice]:
            winner = 'User'
            print(f"\nUser's {user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]} "
                  f"beat Computer's {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]}")
        elif user_pokemon[stat_choice] < computer_pokemon[stat_choice]:
            winner = 'Computer'
            print(f"\nComputer's {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]} "
                  f"beat User's {user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]}")
        else:
            winner = 'Draw'
            print(f"\n{user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]} "
                  f"matches {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]}")
    else:
        winner = type_comparison(user_pokemon, computer_pokemon, stat_choice, player)

    # If User wins
    if winner == 'User':
        print(f"*** User wins this round! ***")
        computer_pokemon_dic.remove(computer_pokemon)

        # User wins the Computer's Pokemon
        user_pokemon_dic.append(computer_pokemon)

        # Computer wins the contents of the draw_list
        user_pokemon_dic.extend(draw_list)
        draw_list.clear()

        player = 'User'

    # If Computer wins
    elif winner == 'Computer':
        print(f"*** Computer wins this round! ***")
        user_pokemon_dic.remove(user_pokemon)

        # Computer wins the User's Pokemon
        computer_pokemon_dic.append(user_pokemon)

        # Computer wins the contents of the draw_list
        computer_pokemon_dic.extend(draw_list)
        draw_list.clear()

        player = 'Computer'

    # If it's a draw
    else:
        print(f"*** Draw! ***")

        # Add both cards of this round to the draw_list to be won in a subsequent round
        user_pokemon_dic.remove(user_pokemon)
        draw_list.append(user_pokemon)
        computer_pokemon_dic.remove(computer_pokemon)
        draw_list.append(computer_pokemon)

    # Move the first Pokemon to the end of the list in both lists
    move_to_end(user_pokemon_dic, user_pokemon)
    move_to_end(computer_pokemon_dic, computer_pokemon)

    return player


# Function to display Pokemon statistics and return a list of types
def display_pokemon_stats(pokemon, owner):
    print(f"{owner} Pokemon is {pokemon['name'].upper()}, it has the statistics:")
    print(f"Height: {pokemon['height']}")
    print(f"Weight: {pokemon['weight']}")

    display_stats = []
    display_stats.extend(basic_stats)

    types_list = "Type: "
    for pokemon_type in pokemon['types']:
        types_list += pokemon_type['name'] + ' '
        display_stats.append(pokemon_type['name'])
    print(types_list)

    return display_stats


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


#
# Main application starts here
#

# Prompt the User to choose the pack size
pack_size = choose_size_of_pack(max_pokemon_id)

# Randomly generate a list of Pokemon IDs and for the User and the Computer
hand_size = int(pack_size / 2)
user_pokemon_ids = generate_pokemon_ids(hand_size, max_pokemon_id)
computer_pokemon_ids = generate_pokemon_ids(hand_size, max_pokemon_id, user_pokemon_ids)

# Generate list of Pokemon data for given IDs
user_pokemon_list = generate_pokemon_list(user_pokemon_ids)
computer_pokemon_list = generate_pokemon_list(computer_pokemon_ids)

# Whenever a round result in a draw, the Pokemon for that round are added to a draw_list
# the draw_list is won by the next winner
draw_list = []

# The first player is always the User
player_turn = 'User'

# Carry on playing until one of the lists is empty,
# i.e. either the User or the Computer has won all the Pokemon
while len(user_pokemon_list) != 0 and len(computer_pokemon_list) != 0:
    player_turn = game_round(player_turn, user_pokemon_list, computer_pokemon_list)
    print(f"The Computer now has {len(computer_pokemon_list)} Pokemon, you have {len(user_pokemon_list)} Pokemon "
          f"({len(draw_list)} Pokemon are in the draw list)")

# Report who won!
if len(computer_pokemon_list) == 0:
    if len(user_pokemon_list) == 0:
        print("\n**************************************************************************")
        print("* Nobody has any more cards (they're all in the draw list!) - STALEMATE! *")
        print("**************************************************************************")
    else:
        print("\n*****************************************")
        print("* Computer has no more cards - YOU WIN! *")
        print("*****************************************")
elif len(user_pokemon_list) == 0:
    print("\n*******************************************")
    print("* User has no more cards - COMPUTER WINS! *")
    print("*******************************************")
