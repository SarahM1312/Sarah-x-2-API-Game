import sys
import winsound

from PyQt5.QtCore import QSize, Qt
from os.path import exists

from PyQt5.QtGui import QIcon

import pokemon_top_trumps
import random
from pygame import mixer

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, \
    QInputDialog, QMessageBox

# Table Cell Items
user_table_cell_items = []
computer_table_cell_items = []

# The first player is always the User
player_turn = 'User'

# Initialise basic statistics which never change
basic_stats = ['height', 'weight']

# The maximum Pokemon ID allowed for the game (Kanto Region)
max_pokemon_id = 151


# This class is required to disable editing in both tables
class MyDelegate(QtWidgets.QItemDelegate):

    def createEditor(self, *args):
        return None


# This function is called when the 'Play' button is pressed
def play():
    # Reinitialise the Data (but only if not midway through a game)
    if len(computer_pokemon_list) == 0 or len(user_pokemon_list) == 0:
        # First hide the play button, it should not be activated while initialising data
        play_button.show()

        # Allow user to reset deck size before new game
        choose_size()

        # Default user for the new game is 'User'
        global player_turn
        player_turn = 'User'

        # Re-initialise Pokemon data
        initialise_pokemon_data()

    # Clear the GUI
    reset_gui()

    # Initiate new game round
    game_round()


# This function is called when the 'help' button is pressed and invokes the Help Dialog
def help_button_clicked():
    help_text = "1. The User chooses the size of pack for the game" \
                "\n2. Pokemon cards are dealt to the User and the Computer" \
                "\n3. Th User leads the first round by choosing which stat to play on their first card" \
                "\n4. The stat is compared with the Computer's top card" \
                "\n5. For numeric stats the winner of this round is whoever has the highest" \
                "\n6. When comparing types the winner is whoever chooses the stronger type according to the Pokemon API" \
                "\n7. The winner of the highest stat wins both top cards and adds to the base of their pile" \
                "\n6. The winner of the round chooses the stat for the next round" \
                "\n7. The first player to get all of the cards wins!"
    QMessageBox.information(dialog, "How to Play Pokemon Top Trumps",
                            help_text,
                            QMessageBox.Ok)


# This function clears the contents of the tables
def reset_gui():
    # Reset table contents
    for table_cell in user_table_cell_items:
        table_cell.setText('')
    for table_cell in computer_table_cell_items:
        table_cell.setText('')

    # Update the card count on the GUI
    count_label.setText(f"User: {len(user_pokemon_list)}  Computer: {len(computer_pokemon_list)}  "
                        f"Draw Pile: {len(draw_list)}")

    # Re-enable both tables
    user_table.setEnabled(True)
    computer_table.setEnabled(True)

    # Set the text for the Play button and hide it
    play_button.setText('Next Round')
    play_button.hide()


# This function is called when a selection is made to the User table
def user_table_type_select():
    try:
        # Find what statistic has been selected
        selected_stats = user_table.selectedItems()

        # Only continue if a valid selection has been made
        if len(selected_stats) > 0:
            selected_type_row = selected_stats[0].row()
            stat_choice = selected_stats[0].text()
            if selected_type_row == 1:
                stat_choice = 'height'
            elif selected_type_row == 2:
                stat_choice = 'weight'

            # Perform statistic comparison
            type_select(stat_choice)
    except:
        print("Exception has occurred in user_table_type_select")


# Function to perform comparison of current User and Computer Pokemon
# based on the selected Pokemon statistical type
def type_select(stat_choice):
    # Define global player_turn variable which we need to keep track of
    global player_turn

    # Assume User Pokemon is the first in the list
    user_pokemon = user_pokemon_list[0]

    # Now that the User selection has been made, display the Computer Pokemon data
    computer_pokemon = computer_pokemon_list[0]
    display_pokemon_stats(computer_pokemon, 'Computer')

    winner = 'User'
    if stat_choice == 'height' or stat_choice == 'weight':
        if user_pokemon[stat_choice] > computer_pokemon[stat_choice]:
            winner = 'User'
            populate_text_box(f"<p style='color:blue'>User's {user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]} "
                              f"beat Computer's {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]}</p>")
            # Play victory sound
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        elif user_pokemon[stat_choice] < computer_pokemon[stat_choice]:
            winner = 'Computer'
            populate_text_box(
                f"<p style='color:red'>Computer's {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]} "
                f"beat User's {user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]}</p>")
            # Play sad beep
            winsound.Beep(300, 500)
        else:
            winner = 'Draw'
            populate_text_box(f"{user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]} "
                              f"matches {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]}")
    else:
        winner = type_comparison(user_pokemon, computer_pokemon, stat_choice, player_turn)

    # If User wins
    if winner == 'User':
        populate_text_box(f"<i><p style='color:blue'>~~~~~~~~~ User wins this round! ~~~~~~~~~</p></i>")
        computer_pokemon_list.remove(computer_pokemon)

        # User wins the Computer's Pokemon
        user_pokemon_list.append(computer_pokemon)

        # Computer wins the contents of the draw_list
        user_pokemon_list.extend(draw_list)
        draw_list.clear()

        # Set the next round to be for the User
        player_turn = 'User'

    # If Computer wins
    elif winner == 'Computer':
        populate_text_box(f"<i><p style='color:red'>~~~~~~~ Computer wins this round! ~~~~~~~</p></i>")
        user_pokemon_list.remove(user_pokemon)

        # Computer wins the User's Pokemon
        computer_pokemon_list.append(user_pokemon)

        # Computer wins the contents of the draw_list
        computer_pokemon_list.extend(draw_list)
        draw_list.clear()

        # Set the next round to be the Computer
        player_turn = 'Computer'

    # If it's a draw
    else:
        populate_text_box(f"<i>~~~~~~~~ This round was a Draw! ~~~~~~~~~</i>")

        # Add both cards of this round to the draw_list to be won in a subsequent round
        user_pokemon_list.remove(user_pokemon)
        draw_list.append(user_pokemon)
        computer_pokemon_list.remove(computer_pokemon)
        draw_list.append(computer_pokemon)

    # Move the first Pokemon to the end of the list in both lists
    pokemon_top_trumps.move_to_end(user_pokemon_list, user_pokemon)
    pokemon_top_trumps.move_to_end(computer_pokemon_list, computer_pokemon)

    # Display current card tally (display draw pile tally if not empty)
    populate_text_box(f"You have {len(user_pokemon_list)} Pokemon, the Computer has {len(computer_pokemon_list)}")
    if len(draw_list) != 0:
        populate_text_box(f"({len(draw_list)} Pokemon are in the draw pile)")

    # Update the card count on the GUI
    count_label.setText(f"User: {len(user_pokemon_list)}  Computer: {len(computer_pokemon_list)}  "
                        f"Draw Pile: {len(draw_list)}")

    # Disable GUI until next round
    round_over()

    # Check if, at the end of this round, the game is now over
    report_game_over()


# Function to compare the type data in the given Pokemon
def type_comparison(user_pokemon, computer_pokemon, stat_choice, player):
    winner = player

    if player == 'User':
        source_pokemon = user_pokemon
        comparison_pokemon = computer_pokemon
    elif player == 'Computer':
        source_pokemon = computer_pokemon
        comparison_pokemon = user_pokemon

    source_types = source_pokemon['types']
    source_type_strong_against = []
    source_type_weak_against = []
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
            populate_text_box(f"{stat_choice} is strong against {type_data['name']}")
            play_victory_sound(stat_choice)
            break
        elif type_data['name'] in source_type_weak_against:
            if player == 'User':
                winner = 'Computer'
            else:
                winner = 'User'
            populate_text_box(f"{stat_choice} is weak against {type_data['name']}")
            play_victory_sound(type_data['name'])
            break
        else:
            populate_text_box(f"{stat_choice} has no effect on {type_data['name']}")
            winner = 'Draw'
    return winner


# Play victory music for a type win
def play_victory_sound(winning_type):
    file_path = 'sound/' + winning_type + '.mp3'

    # Check a file exists for the winning type
    if exists(file_path):
        mixer.music.load(file_path)
        mixer.music.play()
    else:
        winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)
        print(f"Could not play victory tune: the file {file_path} does not exist")

    # Files exist for fire, water, poison, ghost, ice, electric, fighting, flying, rock, dark
    # No files for normal, grass, ground, psychic, bug, dragon, steel, fairy


# Function to report is the game is over
# i.e. if either the User or Computer ave won all the cards
def report_game_over():
    # Report who won!
    if len(computer_pokemon_list) == 0:
        if len(user_pokemon_list) == 0:
            populate_text_box("<b>**** No-one has any more cards - STALEMATE! ****</b>")
            play_button.setText('New Game')
        else:
            populate_text_box("<b><p style='color:blue'>***** Computer has no more cards - YOU WIN *****</p></b>")
            play_button.setText('New Game')
            play_victory_sound('winner')
    elif len(user_pokemon_list) == 0:
        populate_text_box("<b><p style='color:red'>**** User has no more cards - COMPUTER WINS ****</p></b>")
        play_button.setText('New Game')
        play_victory_sound('winner')

    # Re-enable the 'Play button'
    play_button.show()


# Function to populate the information text box
def populate_text_box(message):
    text_browser.append(message)
    print(message)


# Function to display Pokemon statistics and return a list of types
def display_pokemon_stats(pokemon, owner):
    # Populate text box with User instructions
    # populate_text_box(f"{owner} Pokemon is {pokemon['name'].upper()}, it has the above statistics")
    if owner == 'User':
        table_cells_to_populate = user_table_cell_items
    else:
        table_cells_to_populate = computer_table_cell_items

    table_cells_to_populate[0].setText(pokemon['name'].upper())
    table_cells_to_populate[1].setText(str(pokemon['height']))
    table_cells_to_populate[2].setText(str(pokemon['weight']))

    # Add all types to table (there may be 1 or 2)
    display_stats = []
    display_stats.extend(basic_stats)

    row = 3
    for pokemon_type in pokemon['types']:
        display_stats.append(pokemon_type['name'])
        table_cells_to_populate[row].setText(pokemon_type['name'])
        table_cells_to_populate[row].setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        row = row + 1

    # If there is an empty row, disable selection
    if row == 4:
        table_cells_to_populate[row].setFlags(QtCore.Qt.ItemIsSelectable)
    return display_stats


# Function to display a dialog allowing the User to select pack size
def choose_size():
    # User chooses size of pack to play with
    error = True
    while error:
        input_size_of_pack, ok = \
            QInputDialog.getInt(dialog,  # parent
                                "Pokemon Top Trumps",  # title
                                f"How many Pokemon cards do you want to play with?\nChoose an even "
                                f"number between 2 and {max_pokemon_id}",  # label
                                2,  # default value
                                2,  # min value
                                150,  # max value
                                2,  # step
                                Qt.WindowCloseButtonHint)  # WindowsFlags - defines the window setup
        error_message = ""
        # Error check input (must be even)
        if ok:
            if 2 <= input_size_of_pack <= max_pokemon_id:
                if (input_size_of_pack / 2).is_integer():
                    error = False
                else:
                    error_message = f"{input_size_of_pack} is not an even number"
            else:
                error_message = f"{input_size_of_pack} does not fall within 1 and {max_pokemon_id}"

            # Remind the user of the valid input criteria
            if error:
                QMessageBox.warning(dialog, error_message,
                                    f"Input of size of pack must be an even number between 1 and {max_pokemon_id}",
                                    QMessageBox.Ok)
                print(f"Input of size of pack must be an even number between 1 and {max_pokemon_id}")
        else:
            exit_dialog = QMessageBox
            answer = exit_dialog.question(dialog, "Exit?",
                                          "Are you sure you want to exit Pokemon Top Trumps?",
                                          QMessageBox.Yes | QMessageBox.No)
            # Exit the application
            if answer == QMessageBox.Yes:
                exit()

    # Set the global variable
    global pack_size
    pack_size = input_size_of_pack


# Function to update the GUI following the end of the game, i.e. to disallow further selections etc.
def round_over():
    # Disable both tables
    user_table.setEnabled(False)
    computer_table.setEnabled(False)

    # Deselect all table items
    user_table.clearSelection()

    # Prompt user to press button for new round
    play_button.setText('Next Round')
    play_button.show()


# This function generates the table items
def generate_table_items(table, owner):
    table_cell_items = [QTableWidgetItem(),  # name
                        QTableWidgetItem(),  # height
                        QTableWidgetItem(),  # weight
                        QTableWidgetItem(),  # type1
                        QTableWidgetItem()]  # type2
    table.setItem(0, 0, table_cell_items[0])
    table.setItem(1, 0, table_cell_items[1])
    table.setItem(2, 0, table_cell_items[2])
    table.setItem(3, 0, table_cell_items[3])
    table.setItem(4, 0, table_cell_items[4])

    # Only allow selection of the types in the User table
    table_cell_items[0].setFlags(QtCore.Qt.ItemIsSelectable)
    if owner == 'Computer':
        table_cell_items[1].setFlags(QtCore.Qt.ItemIsSelectable)
        table_cell_items[2].setFlags(QtCore.Qt.ItemIsSelectable)
        table_cell_items[3].setFlags(QtCore.Qt.ItemIsSelectable)
        table_cell_items[4].setFlags(QtCore.Qt.ItemIsSelectable)

    return table_cell_items


# Function to perform a round of the game
def game_round():
    # Disable the 'Play button' until the round is over
    play_button.hide()

    # Carry on playing until one of the lists is empty,
    # i.e. either the User or the Computer has won all the Pokemon
    if len(user_pokemon_list) != 0 and len(computer_pokemon_list) != 0:
        user_pokemon = user_pokemon_list[0]
        computer_pokemon = computer_pokemon_list[0]

        # Display whose turn it is
        if player_turn == 'User':
            populate_text_box(f"<p style='color:blue'>^^ YOUR TURN! ^^</p>")
        else:
            populate_text_box(f"<p style='color:red'>^^ COMPUTER'S TURN! ^^</p>")

        # Display User Pokemon statistics
        display_pokemon_stats(user_pokemon, 'User')

        # Determine which statistic to compare
        if player_turn == 'User':
            # If it's the User's turn, prompt User for choice
            populate_text_box(f"<p style='color:blue'>Select the Pokemon statistic would you like to play!</p>")
        else:
            # Display Computer Pokemon statistics
            allowed_stats = display_pokemon_stats(computer_pokemon, 'Computer')

            # If it's the Computer's turn, select choice randomly
            stat_choice = allowed_stats[random.randint(0, (len(allowed_stats)) - 1)]

            # Report to the User what the Computer's choice was
            populate_text_box(f"<p style='color:red'>The Computer has chosen to compare {stat_choice}</p>")

            # Directly initiate statistic comparison for Computer
            type_select(stat_choice)
    else:
        report_game_over()

    # Show the GUI if it has not already been shown
    if dialog.isHidden():
        dialog.show()
        sys.exit(app.exec_())


# Function to generate a random list of Pokemon for the User and Computer of size pack_size
# and to generate an empty draw_list
def initialise_pokemon_data():
    # Report that the data is being loaded
    populate_text_box("Loading Pokemon data...")

    # Randomly generate a list of Pokemon IDs for the User and the Computer
    hand_size = int(pack_size / 2)
    user_pokemon_ids = pokemon_top_trumps.generate_pokemon_ids(hand_size, max_pokemon_id)
    computer_pokemon_ids = pokemon_top_trumps.generate_pokemon_ids(hand_size, max_pokemon_id,
                                                                   user_pokemon_ids)

    # Generate list of Pokemon data for given IDs
    global user_pokemon_list
    user_pokemon_list = pokemon_top_trumps.generate_pokemon_list(user_pokemon_ids)
    global computer_pokemon_list
    computer_pokemon_list = pokemon_top_trumps.generate_pokemon_list(computer_pokemon_ids)

    # Whenever a round results in a draw, the Pokemon for that round are added to a draw_list
    # the draw_list is won by the next winner
    global draw_list
    draw_list = []

    # Report to the User that a new game has been initialised
    populate_text_box("\n<b>============ NEW GAME =============</b>")


# Create Game GUI
app = QApplication(sys.argv)
print(QtWidgets.QStyleFactory.keys())
app.setStyle('Windows')
dialog = QWidget()
dialog.setWindowTitle("Pokemon Top Trumps")
dialog.setFixedSize(QSize(620, 800))
dialog.setWindowIcon(QIcon("pokemon.jpg"))
dialog.setStyleSheet("Background:'white';""font-size: 20px;""colour:'black';")
horizontal_layout_widget = QtWidgets.QWidget(dialog)
horizontal_layout_widget.setGeometry(QtCore.QRect(10, 10, 600, 300))
horizontal_layout_widget.setObjectName("horizontal_layout_widget")
horizontal_layout = QtWidgets.QHBoxLayout(horizontal_layout_widget)
horizontal_layout.setContentsMargins(0, 0, 0, 0)
horizontal_layout.setObjectName("horizontal_layout")

# Define User Pokemon Table
user_table = QTableWidget(5, 1)
user_table.setStyleSheet("QtableWidget:: item {border:5px; padding:5px;}""Background-color:'pink'")
user_table.setItemDelegateForColumn(0, MyDelegate())  # set column 1 to be non-editable
user_table.clicked.connect(user_table_type_select)  # connect Pokemon Type selection to function
user_table.setHorizontalHeaderLabels(['User'])
user_table.horizontalHeader().setSectionsClickable(False)
user_table.setVerticalHeaderLabels(['Name', 'Height', 'Weight', 'Type', ''])
user_table.verticalHeader().setSectionsClickable(False)
user_table.setWindowTitle("User Title")
horizontal_layout.addWidget(user_table)

# Generate User table contents
user_table_cell_items = generate_table_items(user_table, 'User')

# Define cosmetic spacer
spacer_item = QtWidgets.QSpacerItem(20, 198, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
horizontal_layout.addItem(spacer_item)

# Define Computer Pokemon Table
computer_table = QTableWidget(5, 1)
computer_table.setItemDelegateForColumn(0, MyDelegate())  # set column 1 to be non-editable
computer_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
computer_table.setHorizontalHeaderLabels(['Computer'])
computer_table.horizontalHeader().setSectionsClickable(False)
computer_table.setVerticalHeaderLabels(['Name', 'Height', 'Weight', 'Type', ''])
computer_table.verticalHeader().setSectionsClickable(False)
horizontal_layout.addWidget(computer_table)

# Generate User table contents
computer_table_cell_items = generate_table_items(computer_table, 'Computer')

vertical_layout_widget = QtWidgets.QWidget(dialog)
vertical_layout_widget.setGeometry(QtCore.QRect(10, 320, 600, 470))
vertical_layout_widget.setStyleSheet("Background:'white';""font-size: 20px;""colour:'white';")
vertical_layout_widget.setObjectName("vertical_layout_widget")
vertical_layout = QtWidgets.QVBoxLayout(vertical_layout_widget)
vertical_layout.setContentsMargins(0, 0, 0, 0)
vertical_layout.setObjectName("vertical_layout")

# Define label for displaying card count
count_label = QtWidgets.QLabel(vertical_layout_widget)
count_label.setObjectName("count_label")
vertical_layout.addWidget(count_label)

# Define Text Box for displaying instructions
text_browser = QtWidgets.QTextBrowser(vertical_layout_widget)
text_browser.setObjectName("text_browser")
vertical_layout.addWidget(text_browser)

# Define buttons
play_button = QPushButton('Play')
play_button.setStyleSheet(
    "Border: 4px solid '#BC006C';""Background-color: 'pink';""Border-radius: 15px;" "font-size:35px;""color:'black';")
play_button.clicked.connect(play)  # Connect clicked action to play function
vertical_layout.addWidget(play_button)
play_button.hide()

help_button = QPushButton('Help')
help_button.setStyleSheet(
    "Border: 4px solid '#BC006C';""Background-color: 'pink';""Border-radius: 15px;" "font-size:35px;""color:'black';")
help_button.clicked.connect(help_button_clicked)  # Connect clicked action to play function
vertical_layout.addWidget(help_button)

# Initialise music player
mixer.init()

# Prompt the User to choose the pack size - only do this once
choose_size()

# Initialise Pokemon Data
initialise_pokemon_data()

# Update the card count on the GUI
count_label.setText(f"User: {len(user_pokemon_list)}  Computer: {len(computer_pokemon_list)}  "
                    f"Draw Pile: {len(draw_list)}")

# Start the first round
game_round()
