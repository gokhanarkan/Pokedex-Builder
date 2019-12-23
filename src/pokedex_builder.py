from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import Request
import csv
import re

# I am currently not using the Pokemon object. Reference purposes only


class Pokemon:
	def __init__(self, pokeid, name, definition, image, evolution):
		self.pokeid = pokeid
		self.name = name
		self.definition = definition
		self.image = image
		self.evolution = evolution


poke_dict = []

# THIS METHOD EXPORTS INFORMATION AS CSV FILE


def export_csv(poke_dict):
	with open("poke_dict.csv", "w") as file:
		pokemon_writer = csv.writer(file)
		pokemon_writer.writerows(poke_dict)

# THIS METHOD CREATES A HTML PAGE FOR SCRAPING


def make_html(pokemon):

	# Extra caution for nidoran genders and flabebe
	if pokemon == "Nidoran♀":
		pokemon = "nidoran-f"
	if pokemon == "Nidoran♂":
		pokemon = "nidoran-m"
	if pokemon == "Flabébé":
		pokemon = "flabebe"

	# Extra caution for bloody farfetch'd and his mates
	namelist = list(pokemon)
	if "'" in namelist:
		oldname = pokemon.split("'")
		pokemon = ""
		for chars in oldname:
			pokemon += chars

	if pokemon == "Mime Jr.":
		pokemon = "mime-jr"
	# Extra caution for Sir Mr. Mime and his bros
	elif "." in namelist:
		oldname = pokemon.split(". ")
		pokemon = oldname[0] + "-" + oldname[1]
	# For the Pokemon Type: Null
	elif ":" in namelist:
		oldname = pokemon.split(": ")
		pokemon = oldname[0] + "-" + oldname[1]
	# Tapu Pokemon
	elif " " in namelist:
		oldname = pokemon.split(" ")
		pokemon = oldname[0] + "-" + oldname[1]

	# Reaching the page and getting HTML entities
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers = {'User-Agent': user_agent, }
	url = Request(
		"https://pokemondb.net/pokedex/{}".format(pokemon), None, headers)

	return urlopen(url)

# THIS METHOD GETS STRING WITH HTML CODE AND CLEANS WITH REGULAR EXPRESSION


def clean_tags(raw_html):

	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

# THIS METHOD SCRAPES ALL THE POKEMONS CREATED FROM THE DIRECTORY


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

# THIS METHOD CREATES TABLE OUT OF MESSY LIST OF INFORMATION


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

# THIS METHOD LIMITS THE LENGTH OF THE TABLE
# ALTHOUGH THE FURTHER INFORMATION IS NOT NECESSARY FOR ME AT THE MOMENT, YOU CAN COMMENT THE BREAK AND ACCESS ALL THE DATA


def limit_table(cleaned_table):

	true_table = []
	for array in cleaned_table:
		for product in array:
			if len(true_table) == 56:
				break
			if product != '':
				true_table.append(product)

	return true_table

# THIS METHOD SCRAPES THE IMPORTANT INFORMATION FROM POKEDEX PAGE


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

		# EVOLUTION STYLE LIKE WHEN OR HOW ETC.
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

		# VARIOUS TABLE DATA TABLE
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

		arrange_data(pokemon, definition, evo_list, main_image,
		             counter, pokedex_data, training, breeding, base_stats)
		counter += 1

# THIS METHOD MODIFIES THE DATA FOR FINAL ENTRY


def arrange_data(pokemon, definition, evo_list, main_image, counter, pokedex_data, training, breeding, base_stats):

	if len(evo_list) < 1:
		evo_list = "No Evolution"

	arranged_data = [counter, pokemon, definition, main_image,
                  evo_list, pokedex_data, training, breeding, base_stats]
	poke_dict.append(arranged_data)
	# pokemon = Pokemon(counter, pokemon, definition, main_image, evo_list)


if __name__ == '__main__':
	get_pokemon_details(get_pokemon_names())
	export_csv(poke_dict)
