from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import Request
from helper_fuctions import export_csv, clean_tags, is_integer, arrange_data, run_precaution

poke_dict = []

# Creating HTML page for scraping
def make_html(pokemon):

	pokemon = run_precaution(pokemon)

	# Reaching the page and getting HTML entities
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers = {'User-Agent': user_agent, }
	url = Request(
		"https://pokemondb.net/pokedex/{}".format(pokemon), None, headers)

	return urlopen(url)

# Scraping all the pokemon names from the directory
def get_pokemon_names():

	name_dict = []
	html = make_html("national")
	# Converting into a BeautifulSoup object and iterating the content
	soup = BeautifulSoup(html.read(), "html5lib")
	for span in soup.findAll('span', attrs={'class': 'infocard-lg-data'}):
		for name in span.findAll('a', attrs={'class': 'ent-name'}):
			# Pokemon Name
			name_dict.append(name.text)

	return name_dict

# Cleaning the messy information
def make_table(cleaned_table):

	true_table = limit_table(cleaned_table)

	pokedex_data = []
	training = []
	breeding = []
	base_stats = []

	# Addint information to Pokedex Data table
	for p in range(0, 14):
		pokedex_data.append(true_table[p])

	# Adding information to Training table
	for t in range(14, 24):
		training.append(true_table[t])

	# Adding information to Breeding table
	for b in range(24, 30):
		breeding.append(true_table[b])

	# Adding information to Base Stats table
	# Note: I grouped them up in four; header, base stat, min and max
	for bs in range(30, 54, 4):
		if bs == len(true_table)-2:
			total = [true_table[bs], true_table[bs+1]]
			base_stats.append(total)
			break
		stat = [true_table[bs], true_table[bs+1], true_table[bs+2], true_table[bs+3]]
		base_stats.append(stat)

	return pokedex_data, training, breeding, base_stats

# Limiting length of the table
# ALTHOUGH THE FURTHER INFORMATION IS NOT NECESSARY FOR ME AT THE MOMENT, YOU CAN CHANGE THE BREAK WITH PASS AND ACCESS ALL THE DATA
def limit_table(cleaned_table):

	true_table = []
	for array in cleaned_table:
		for product in array:
			if len(true_table) == 56:
				break
			if product != '':
				true_table.append(product)

	return true_table


def get_move_table(chars):

	# The aim of this function to empty the chars list whilst getting all the relevant information
	# such as move type, move power and move accuracy

	# The data example is like this without the first digits
	# { 40Flare BlitzFire 120 100 }
	first_position = 0
	for i in range(1, len(chars)):
		if chars[i].isupper():
			first_position = i

	# This if statement is my own way of error handling, please don't ask any questions
	if first_position == 0:
		move_table = {
			"move_level" 	: "move_level",
			"move_name" 	: "SOMETHING'S WRONG",
		}
		return move_table

	move_name = ""
	for f in range(0, first_position):
		move_name += chars.pop(0)
	# Rest of the chars are type, power and accuracy. Fortunately they came in order,
	# simple string manipulation is enough here.
	rest = "".join(chars)
	rest = rest.split(' ')
	move_type = rest[0]
	move_power = rest[1]
	move_accuracy = rest[2]

	# Creating all the content for move table. Move level is stored already so it's temporary here
	move_table = {

		"move_level" 	: "move_level",
		"move_name" 	: move_name,
		"move_type" 	: move_type,
		"move_power" 	: move_power,
		"move_accuracy": move_accuracy

	}

	return move_table


def divide_words(chars):

	# Keeping the first word of the move also counting how many letters does it have
	first_word = ""
	counter = 0
	for i in chars:
		if i == ' ':
			first_word += i
			counter += 1
			break
		first_word += i
		counter += 1
	for i in range(0, counter):
		chars.pop(0)
	# After storing the first word and popping the characters from the array it's all very easy, logig is already done on get_move_table
	move_table = get_move_table(chars)
	second_word = move_table['move_name']
	move_table.update({"move_name": first_word + second_word})

	return move_table

# MAIN SCRAPING FUNCTION
def get_pokemon_details(name_dict):

	counter = 1
	for pokemon in name_dict:
		print(pokemon)

		# Create the html file to start for single pokedex entry
		html = make_html(pokemon)
		soup = BeautifulSoup(html.read(), "html5lib")

		# DEFINITION OF THE POKEMON
		definition_string = ""
		for paragraph in soup.find('p'):
			definition_string += str(paragraph)
		definition = clean_tags(definition_string)

		# EVOLUTION NAMES OF THE POKEMON
		evolution = []
		for evo in soup.findAll('span', attrs={'class': 'infocard-lg-data'}):
			evo = clean_tags(str(evo))
			evo = evo.split(' ')
			evolution.append(evo[1])

		# EVOLUTION STYLE SUCH AS HOW OR WHEN
		evolution_styles = []
		for evo in soup.findAll('span', attrs={'class': 'infocard-arrow'}):
			evo = clean_tags(str(evo))
			evolution_styles.append(evo)

		# LISTING NAME AND STYLE TOGETHER
		evo_list = []
		while evolution:
			evo_list.append(evolution.pop(0))
			if(evolution_styles):
				evo_list.append(evolution_styles.pop(0))

		# MAIN IMAGE OF THE POKEMON
		try:
			for artwork in soup.find('a', attrs={'rel': 'lightbox'}):
				main_image = artwork['src']
		except:
			artwork = soup.find('img')
			main_image = artwork['src']

		# VARIOUS DATA TABLE
		table_data = []
		# This for loop checks all the fields for table data like breeding, capture chance, type etc.
		for poketype in soup.findAll('table', attrs={'class': 'vitals-table'}):
			if poketype != "\n":
				table_data.append(clean_tags(str(poketype)))
		# There will be tuples of data and it needs some cleaning to put all of them into a single list
		cleaned_table = []
		for t in table_data:
			x = t.split('\n')
			cleaned_table.append(x)

		pokedex_data, training, breeding, base_stats = make_table(cleaned_table)

		# MOVES LEARNT BY LEVEL UP TABLE
		for move in soup.findAll('div', attrs={'class': 'span-lg-6'}):
			# Specifically storing the first table, otherwise the for loop gets other tables as well
			i = move.find('div', attrs={'class': 'resp-scroll'})
			# This is rather a complex way to get the best result from the html
			moves = i.text.split('Lv. Move Type Cat. Power Acc. ')[1]
			break
		# moves is a single string so I divide them into pieces
		moves = moves.split('\n')
		# Inspecting every single move
		moves.pop()  # The last item is empty, it's wise to pop that here
		# List of all the moves of that specific pokemon
		move_tables = []
		# BEFORE: I BELIEVE THIS FOR LOOP WILL BE A BIT COMPLEX
		for move in moves:
			chars = list(move)  # Checking every character is necessary
			counter_map = 0  # There will be two algorithms depending on the counter_map number. 2 will be straight-forward but 3, well, not too much
			# Calculating counter_map
			for char in chars:
				if char == ' ':
					counter_map += 1
			# First algorithm
			if counter_map == 2:
				# Checking if the second integer is string (higher level move)
				if is_integer(chars[1]):
					# Since the level is two digits, I get the first two character, then pop them
					move_level = chars[0] + chars[1]

					chars.pop(0)
					chars.pop(0)
					# Sending a factored function to avoid mess
					move_table = get_move_table(chars)
					move_table.update({"move_level": int(move_level)})

				else:
					# The level is one digit, I only get the first character and pop it
					move_level = chars[0]

					chars.pop(0)

					move_table = get_move_table(chars)
					# Final change because I stored the level in the first place
					move_table.update({"move_level": int(move_level)})

			else:  # This else statement is for moves that contain more than a word

				if is_integer(chars[1]):
					# Same logic, I store the level and pop these characters
					move_level = chars[0] + chars[1]

					chars.pop(0)
					chars.pop(0)

					move_table = divide_words(chars)
					move_table.update({"move_level": int(move_level)})

				else:

					move_level = chars[0]

					chars.pop(0)

					move_table = divide_words(chars)
					move_table.update({"move_level": int(move_level)})

			move_tables.append(move_table)

		poke_dict.append(arrange_data(pokemon, definition, evo_list, main_image,
                                counter, pokedex_data, training, breeding, base_stats, move_tables))
		counter += 1


if __name__ == '__main__':
	get_pokemon_details(get_pokemon_names())
	export_csv(poke_dict)
