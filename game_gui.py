import sys

from PyQt5.QtCore import QSize

import pokemon_top_trumps
import random

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, \
    QDialog

# Table Cell Items
user_table_cell_items = []
computer_table_cell_items = []

# The first player is always the User
player_turn = 'User'

# Initialise basic statistics which never change
basic_stats = ['height', 'weight']


# This class is required to disable editing in both tables
class MyDelegate(QtWidgets.QItemDelegate):

    def createEditor(self, *args):
        return None


# This function is called when the 'Play' button is pressed
def play():
    # Clear the GUI
    reset_gui()

    # Reinitialise the Data (but only if not mid-way through a game)
    if len(computer_pokemon_list) == 0 or len(user_pokemon_list) == 0:
        global player_turn
        player_turn = 'User'
        initialise_pokemon_data()

    # Initiate new game round
    game_round()


# This function clears the contents of the tables
def reset_gui():
    # Reset table contents
    for table_cell in user_table_cell_items:
        table_cell.setText('')
    for table_cell in computer_table_cell_items:
        table_cell.setText('')

    # Re-enable both tables
    user_table.setEnabled(True)
    computer_table.setEnabled(True)


# This function is called when a selection is made to the User table
def user_table_type_select():
    # Find what statistic has been selected
    selected_stats = user_table.selectedItems()
    selected_type_row = selected_stats[0].row()
    stat_choice = selected_stats[0].text()
    if selected_type_row == 1:
        stat_choice = 'height'
    elif selected_type_row == 2:
        stat_choice = 'weight'

    # Perform statistic comparison
    type_select(stat_choice)


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
            populate_text_box(f"User's {user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]} "
                              f"beat Computer's {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]}")
        elif user_pokemon[stat_choice] < computer_pokemon[stat_choice]:
            winner = 'Computer'
            populate_text_box(
                f"Computer's {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]} "
                f"beat User's {user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]}")
        else:
            winner = 'Draw'
            populate_text_box(f"{user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]} "
                              f"matches {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]}")
    else:
        winner = pokemon_top_trumps.type_comparison(user_pokemon, computer_pokemon, stat_choice, player_turn)

    # If User wins
    if winner == 'User':
        populate_text_box(f"*** User wins this round! ***")
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
        populate_text_box(f"*** Computer wins this round! ***")
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
        populate_text_box(f"*** Draw! ***")

        # Add both cards of this round to the draw_list to be won in a subsequent round
        user_pokemon_list.remove(user_pokemon)
        draw_list.append(user_pokemon)
        computer_pokemon_list.remove(computer_pokemon)
        draw_list.append(computer_pokemon)

    # Move the first Pokemon to the end of the list in both lists
    pokemon_top_trumps.move_to_end(user_pokemon_list, user_pokemon)
    pokemon_top_trumps.move_to_end(computer_pokemon_list, computer_pokemon)

    populate_text_box(
        f"The Computer now has {len(computer_pokemon_list)} Pokemon, you have {len(user_pokemon_list)} Pokemon "
        f"({len(draw_list)} Pokemon are in the draw list)")

    # Disable GUI until next round
    round_over()

    # Check if, at the end of this round, the game is now over
    report_game_over()


# Function to report is the game is over
# i.e. if either the User or Computer ave won all the cards
def report_game_over():
    # Report who won!
    if len(computer_pokemon_list) == 0:
        if len(user_pokemon_list) == 0:
            populate_text_box("* Nobody has any more cards (they're all in the draw list!) - STALEMATE! *")
            play_button.setText('New Game')
        else:
            populate_text_box("****** Computer has no more cards - YOU WIN! ******")
            play_button.setText('New Game')
    elif len(user_pokemon_list) == 0:
        populate_text_box("****** User has no more cards - COMPUTER WINS! ******")
        play_button.setText('New Game')


# Function to populate the information text box
def populate_text_box(message):
    text_browser.append(message)
    print(message)


# Function to display Pokemon statistics and return a list of types
def display_pokemon_stats(pokemon, owner):
    # Populate text box with User instructions
    populate_text_box(f"{owner} Pokemon is {pokemon['name'].upper()}, it has the above statistics")

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
        row = row + 1

    return display_stats


# Function to display a dialog
def display_dialog():
    welcome_dialog = QWidget()
    welcome_dialog.resize(1000, 500)
    welcome_dialog.setWindowTitle("Welcome")
    welcome_dialog.setFixedSize()
    welcome_dialog.show()


# Function to update the GUI following the end of the game, i.e. to disallow further selections etc.
def round_over():
    # Disable both tables
    user_table.setEnabled(False)
    computer_table.setEnabled(False)

    # Deselect all table items
    user_table.clearSelection()

    # Prompt user to press button for new round
    play_button.setText('Next Round')


# This function generates the table items
def generate_table_items(table):
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
    return table_cell_items


# Function to perform a round of the game
def game_round():
    # Carry on playing until one of the lists is empty,
    # i.e. either the User or the Computer has won all the Pokemon
    if len(user_pokemon_list) != 0 and len(computer_pokemon_list) != 0:
        user_pokemon = user_pokemon_list[0]
        computer_pokemon = computer_pokemon_list[0]

        # Display whose turn it is
        if player_turn == 'User':
            populate_text_box(f"*** YOUR TURN! ***")
        else:
            populate_text_box(f"*** COMPUTER'S TURN! ***")

        # Display User Pokemon statistics
        display_pokemon_stats(user_pokemon, 'User')

        # Show the GUI if it has not already been shown
        if dialog.isHidden():
            dialog.show()
            sys.exit(app.exec_())

        # Determine which statistic to compare
        if player_turn == 'User':
            # If it's the User's turn, prompt User for choice
            populate_text_box(f"Select the Pokemon statistic would you like to play!")
        else:
            # Display Computer Pokemon statistics
            allowed_stats = display_pokemon_stats(computer_pokemon, 'Computer')

            # If it's the Computer's turn, select choice randomly
            stat_choice = allowed_stats[random.randint(0, len(allowed_stats))]

            # Report to the User what the Computer's choice was
            populate_text_box(f"The Computer has chosen the statistic {stat_choice}")

            # Directly initiate statistic comparison for Computer
            type_select(stat_choice)
    else:
        report_game_over()


def initialise_pokemon_data():
    # Randomly generate a list of Pokemon IDs for the User and the Computer
    hand_size = int(pack_size / 2)
    user_pokemon_ids = pokemon_top_trumps.generate_pokemon_ids(hand_size, pokemon_top_trumps.max_pokemon_id)
    computer_pokemon_ids = pokemon_top_trumps.generate_pokemon_ids(hand_size, pokemon_top_trumps.max_pokemon_id,
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
    populate_text_box("\n================== NEW GAME ==================")


# Create Game GUI
app = QApplication(sys.argv)
dialog = QWidget()
dialog.setWindowTitle("Pokemon Top Trumps")
dialog.setFixedSize(QSize(620, 800))
horizontal_layout_widget = QtWidgets.QWidget(dialog)
horizontal_layout_widget.setGeometry(QtCore.QRect(10, 10, 600, 300))
horizontal_layout_widget.setObjectName("horizontal_layout_widget")
horizontal_layout = QtWidgets.QHBoxLayout(horizontal_layout_widget)
horizontal_layout.setContentsMargins(0, 0, 0, 0)
horizontal_layout.setObjectName("horizontal_layout")

# Define User Pokemon Table
user_table = QTableWidget(5, 1)
user_table.setItemDelegateForColumn(0, MyDelegate())  # set column 1 to be non-editable
user_table.clicked.connect(user_table_type_select)  # connect Pokemon Type selection to function
user_table.setHorizontalHeaderLabels(['User'])
user_table.horizontalHeader().setSectionsClickable(False)
user_table.setVerticalHeaderLabels(['Name', 'Height', 'Weight', 'Type', ''])
user_table.verticalHeader().setSectionsClickable(False)
horizontal_layout.addWidget(user_table)

# Generate User table contents
user_table_cell_items = generate_table_items(user_table)

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
computer_table_cell_items = generate_table_items(computer_table)

vertical_layout_widget = QtWidgets.QWidget(dialog)
vertical_layout_widget.setGeometry(QtCore.QRect(10, 320, 600, 470))
vertical_layout_widget.setObjectName("vertical_layout_widget")
vertical_layout = QtWidgets.QVBoxLayout(vertical_layout_widget)
vertical_layout.setContentsMargins(0, 0, 0, 0)
vertical_layout.setObjectName("vertical_layout")

# Define Text Box for displaying instructions
text_browser = QtWidgets.QTextBrowser(vertical_layout_widget)
text_browser.setObjectName("text_browser")
vertical_layout.addWidget(text_browser)

# Define buttons
play_button = QPushButton('Play')
play_button.clicked.connect(play)  # Connect clicked action to play function
vertical_layout.addWidget(play_button)

# Prompt the User to choose the pack size - only do this once
pack_size = pokemon_top_trumps.choose_size_of_pack(pokemon_top_trumps.max_pokemon_id)

# Initialise Pokemon Data
initialise_pokemon_data()

# Start the first round
game_round()
