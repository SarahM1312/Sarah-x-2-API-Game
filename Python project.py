import requests

import random


# Welcome message

print("Welcome to Pokemon Top Trumps, your opponent is the computer \n")


# Obtain data
def random_pokemon():
    pokemon_number = random.randint(1, 151)
    url = 'https://pokeapi.co/api/v2/pokemon/{}/'.format(pokemon_number)
    response = requests.get(url)
    pokemon = response.json()

    return {
        'name': pokemon['name'],
        'id': pokemon['id'],
        'height': pokemon['height'],
        'weight': pokemon['weight'],
    }


def random_stat():
    random_number = random.randint(1, 3)
    if random_number == 1:
        stat = 'id'
    elif random_number == 2:
        stat = 'height'
    else:
        stat = 'weight'

    return stat


# Round where player chooses stat
def player_round():
    print("In this round you will choose the stat's to compare\n")

    # player picks Pokemon
    player_score = 0
    opponent_score = 0

    random_pokemon_1 = random_pokemon()
    random_pokemon_2 = random_pokemon()
    random_pokemon_3 = random_pokemon()
    random_pokemon_4 = random_pokemon()

    print("You can choose one of the following pokemon's :\n{}, {}, {} or {}\n".format(random_pokemon_1["name"],
                                                                                    random_pokemon_2["name"],
                                                                                    random_pokemon_3["name"],
                                                                                    random_pokemon_4["name"]))
    pokemon_choice = input("Which pokemon do you want to use?\n")

    # Obtaining the stats of the Pokemon

    if pokemon_choice == random_pokemon_1['name']:
        player_pokemon = random_pokemon_1
    elif pokemon_choice == random_pokemon_2['name']:
        player_pokemon = random_pokemon_2
    elif pokemon_choice == random_pokemon_3['name']:
        player_pokemon = random_pokemon_3
    elif pokemon_choice == random_pokemon_4["name"]:
        player_pokemon = random_pokemon_4

    print("\nYour pokemon has the following stats: \nid: {}, height: {}, weight: {} \n".format(player_pokemon['id'],
                                                                                               player_pokemon['height'],
                                                                                               player_pokemon[
                                                                                                   'weight']))
    stat_choice = input("Which stat do you want to use? (id, height, weight) \n")

    # opponent pokemon choice
    opponent_pokemon = random_pokemon()
    print("\nYour opponent chose {}\n".format(opponent_pokemon['name']))

    # Determine who wins the round
    player_stat = player_pokemon[stat_choice]
    opponent_stat = opponent_pokemon[stat_choice]

    if player_stat > opponent_stat:
        print("Congratulations, you have won this round\n")
        player_score = player_score + 1
    elif player_stat < opponent_stat:
        print("You have lost this round, better luck next time\n")
        opponent_score = opponent_score + 1
    else:
        print("It's a draw!\n")

    print("At the end of this round the score is \nYour score: {}, Opponent score: {} \n".format(player_score,opponent_score))

    return player_score, opponent_score


# Round where opponent chooses stat
def opponent_round():
    print("In this round your opponent will pick the stats\n")
    player_score = 0
    opponent_score = 0

    random_pokemon_1 = random_pokemon()
    random_pokemon_2 = random_pokemon()
    random_pokemon_3 = random_pokemon()
    random_pokemon_4 = random_pokemon()

    print("\nYou can choose one of the following pokemon's :\n{}, {}, {} or {}\n".format(random_pokemon_1["name"],
                                                                                    random_pokemon_2["name"],
                                                                                    random_pokemon_3["name"],
                                                                                    random_pokemon_4["name"]))
    pokemon_choice = input("Which pokemon do you want to use? \n")

    # Obtaining the stats of the Pokemon

    if pokemon_choice == random_pokemon_1['name']:
        player_pokemon = random_pokemon_1
    elif pokemon_choice == random_pokemon_2['name']:
        player_pokemon = random_pokemon_2
    elif pokemon_choice == random_pokemon_3['name']:
        player_pokemon = random_pokemon_3
    elif pokemon_choice == random_pokemon_4["name"]:
        player_pokemon = random_pokemon_4

    opponent_pokemon = random_pokemon()
    print("Your opponent chose {}\n".format(opponent_pokemon['name']))

    opponent_stat_choice = random_stat()
    print("The opponent chose {} as their stat choice\n".format(opponent_stat_choice))

    opponent_stat = opponent_pokemon[opponent_stat_choice]

    player_stat = player_pokemon[opponent_stat_choice]

    if player_stat > opponent_stat:
        print("Congratulations, you have won this round\n")
        player_score = player_score + 1
    elif player_stat < opponent_stat:
        print("You have lost this round, better luck next time\n")
        opponent_score = opponent_score + 1
    else:
        print("It's a draw!\n")

    print("At the end of this round the score is \n Your Score: {}, Opponent: {} \n".format(player_score,
                                                                                opponent_score))


def run():
    for rounds in range(4):
        player_round()
        opponent_round()



run()
