# In order to run this code you will need to:
# run it on Python 3.9;
# save Pokemon-top_trumps in the same file; and
# import the following into your terminal
# ~ pip install requests; and
# ~ pip install pyqt5 pyqt5-tools

import sys

from PyQt5.QtCore import QSize

import pokemon_top_trumps
import random

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, \
    QInputDialog, QMessageBox, QVBoxLayout, QGridLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QCursor

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
    # Reinitialise the Data (but only if not mid-way through a game)
    if len(computer_pokemon_list) == 0 or len(user_pokemon_list) == 0:
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


# This function clears contents of text box

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


# This function is called when a selection is made to the User table
def user_table_type_select():
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
            populate_text_box(f"\nUser's {user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]} "
                              f"beat Computer's {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]}\n")
        elif user_pokemon[stat_choice] < computer_pokemon[stat_choice]:
            winner = 'Computer'
            populate_text_box(
                f"\nComputer's {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]} "
                f"beat User's {user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]}\n")
        else:
            winner = 'Draw'
            populate_text_box(f"{user_pokemon['name'].upper()} {stat_choice} {user_pokemon[stat_choice]} "
                              f"matches {computer_pokemon['name'].upper()} {stat_choice} {computer_pokemon[stat_choice]}")
    else:
        winner = type_comparison(user_pokemon, computer_pokemon, stat_choice, player_turn)

    # If User wins
    if winner == 'User':
        populate_text_box(f"~~~~~~~~~ User wins this round! ~~~~~~~~~")
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
        populate_text_box(f"~~~~~~~ Computer wins this round! ~~~~~~~")
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
        populate_text_box(f"~~~~~~~~ This round was a Draw! ~~~~~~~~~")

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
            populate_text_box(f"\n{stat_choice} is strong against {type_data['name']}\n")
            break
        elif type_data['name'] in source_type_weak_against:
            if player == 'User':
                winner = 'Computer'
            else:
                winner = 'User'
            populate_text_box(f"\n{stat_choice} is weak against {type_data['name']}\n")
            break
        else:
            populate_text_box(f"\n{stat_choice} has no effect on {type_data['name']}\n")
            winner = 'Draw'
    return winner


# Function to report is the game is over
# i.e. if either the User or Computer ave won all the cards
def report_game_over():
    # Report who won!
    if len(computer_pokemon_list) == 0:
        if len(user_pokemon_list) == 0:
            populate_text_box("****** No-one has any more cards - STALEMATE! ******")
            play_button.setText('New Game')
        else:
            populate_text_box("******* Computer has no more cards - YOU WIN *******")
            play_button.setText('New Game')
    elif len(user_pokemon_list) == 0:
        populate_text_box("****** User has no more cards - COMPUTER WINS ******")
        play_button.setText('New Game')

    # Re-enable the 'Play button'
    play_button.setDisabled(False)


# Function to populate the information text box
def populate_text_box(message):
    text_browser.append(message)
    print(message)


# Function to clear the information in text box
def clear_text_box():
    clear(text_browser)


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
        input_size_of_pack, ok = QInputDialog.getInt(dialog, "Pokemon Top Trumps",
                                                     f"How many Pokemon cards do you want to play with?\nChoose an even "
                                                     f"number between 2 and {max_pokemon_id}")
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

    # Set the global variable
    global pack_size
    pack_size = input_size_of_pack


# Function for user to choose your Pokemon

# Function to update the GUI following the end of the game, i.e. to disallow further selections etc.
def round_over():
    # Disable both tables
    user_table.setEnabled(False)
    computer_table.setEnabled(False)

    # Deselect all table items
    user_table.clearSelection()

    # Prompt user to press button for new round
    play_button.setText('Next Round')
    play_button.setDisabled(True)


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
    play_button.setDisabled(True)

    # Carry on playing until one of the lists is empty,
    # i.e. either the User or the Computer has won all the Pokemon
    if len(user_pokemon_list) != 0 and len(computer_pokemon_list) != 0:
        user_pokemon = user_pokemon_list[0]
        computer_pokemon = computer_pokemon_list[0]

        # Display whose turn it is
        if player_turn == 'User':
            populate_text_box(f"^^^^^^^^^\nYOUR TURN!\n^^^^^^^^^")
        else:
            populate_text_box(f"^^^^^^^^^^\nCOMPUTER'S TURN!\n^^^^^^^^^^")

        # Display User Pokemon statistics
        display_pokemon_stats(user_pokemon, 'User')

        # Determine which statistic to compare
        if player_turn == 'User':
            # If it's the User's turn, prompt User for choice
            populate_text_box(f"\nSelect the Pokemon statistic would you like to play!")
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

    # Show the GUI if it has not already been shown
    if dialog.isHidden():
        dialog.show()
        sys.exit(app.exec_())


# Function to generate a random list of Pokemon for the User and Computer of size pack_size
# and to generate an empty draw_list
def initialise_pokemon_data():
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
    populate_text_box("\n==================\nNEW GAME\n ===================")


# create welcome message
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Welcome to Pokemon Top Trumps")
window.setFixedWidth(1000)
window.setStyleSheet("background: #161219;")

grid = QGridLayout()

image = QPixmap("Pokemon-Transparent-Images.png")
logo = QLabel()
logo.setPixmap(image)
logo.setAligment(QtCore.Qt.AlignCenter)
grid.addimage(logo,0,0)

sys.exit(app.exec())

# Create Game GUI
app = QApplication(sys.argv)
dialog = QWidget()
dialog.setWindowTitle("Pokemon Top Trumps")
dialog.setFixedSize(QSize(620, 800))
dialog.setStyleSheet("Background:'white';""font-size: 20px;""colour:'black';")
horizontal_layout_widget = QtWidgets.QWidget(dialog)
horizontal_layout_widget.setGeometry(QtCore.QRect(10, 10, 600, 300))
horizontal_layout_widget.setObjectName("horizontal_layout_widget")
horizontal_layout = QtWidgets.QHBoxLayout(horizontal_layout_widget)
horizontal_layout.setContentsMargins(0, 0, 0, 0)
horizontal_layout.setObjectName("horizontal_layout")

# Create table to allow user to choose Pokemon
# user_table_pokemon = QTableWidget(random.randint(0, int(len(user_pokemon_dic))))
# user_table.setItemDelegateForColumn(0, MyDelegate())  # set column 1 to be non-editable
# user_table.clicked.connect(user_pokemon_select)  # connect Pokemon Type selection to function
# user_table.setHorizontalHeaderLabels(['User Pokemon Choice'])
# user_table.horizontalHeader().setSectionsClickable(False)
# user_table.setWindowTitle("Pick Pokemon you would like to select")
# horizontal_layout.addWidget(user_table)

# Define User Pokemon Table
user_table = QTableWidget(5, 1)
user_table.setStyleSheet("QtableWidget:: item {border:0px; padding:5px;}""Background-color:'pink'")
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
    "Border: 4px solid 'bue';""Background-color: 'yellow';""Border-radius: 15px;" "font-size:35px;""color:'blue';")
play_button.clicked.connect(play)  # Connect clicked action to play function
vertical_layout.addWidget(play_button)

# Prompt the User to choose the pack size - only do this once
choose_size()

# Initialise Pokemon Data
initialise_pokemon_data()

# Update the card count on the GUI
count_label.setText(f"User: {len(user_pokemon_list)}  Computer: {len(computer_pokemon_list)}  "
                    f"Draw Pile: {len(draw_list)}")

# Start the first round
game_round()
