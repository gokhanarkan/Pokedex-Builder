from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import Request
import csv, re

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
	if pokemon == "Nidoran♀": pokemon = "nidoran-f"
	if pokemon == "Nidoran♂": pokemon = "nidoran-m"
	if pokemon == "Flabébé": pokemon = "flabebe"
		
	# Extra caution for bloody farfetch'd and his mates
	namelist = list(pokemon)
	if "'" in namelist:
		oldname = pokemon.split("'")
		pokemon = ""
		for chars in oldname:
			pokemon += chars

	if pokemon == "Mime Jr.": pokemon = "mime-jr"
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
	headers={'User-Agent':user_agent,}
	url = Request("https://pokemondb.net/pokedex/{}".format(pokemon), None, headers)
	
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
	for span in soup.findAll('span', attrs={'class':'infocard-lg-data'}):
		for name in span.findAll('a', attrs={'class':'ent-name'}):
			# Pokemon Name
			name_dict.append(name.text)

	return name_dict

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
		for span in soup.findAll('span', attrs={'class':'infocard-lg-data'}):
			for name in span.findAll('a', attrs={'class':'ent-name'}):
				evolution.append(name.get_text())

		# IMAGES OF THE POKEMON
		img = []
		for span in soup.findAll('span', attrs={'class':'infocard-lg-img'}):
			for image in span.findAll('a'):
				src = str(image).split('"')[7]
				img.append(src)

		# MATCHING IMAGE AND EVOLUTION
		evo_and_image = []
		for i in range(0, len(evolution)):
			evo_and_image.append([evolution[i], img[i]])

		# MAIN IMAGE OF THE POKEMON
		try:
			for artwork in soup.find('a', attrs={'rel':'lightbox'}):
				main_image = artwork['src']
		except:
			artwork = soup.find('img')
			main_image = artwork['src']

		arrange_data(pokemon, definition, evo_and_image, main_image, counter)
		counter += 1

# THIS METHOD MODIFIES THE DATA FOR FINAL ENTRY
def arrange_data(pokemon, definition, evo_and_image, main_image, counter):

	if len(evo_and_image) < 1:
		evo_and_image = "No Evolution"

	arranged_data = [counter, pokemon, definition, main_image, evo_and_image]
	poke_dict.append(arranged_data)
	# pokemon = Pokemon(counter, pokemon, definition, main_image, evo_and_image)

if __name__ == '__main__':
	try:
		get_pokemon_details(get_pokemon_names())
		export_csv(poke_dict)
	except Exception as e:
		print(e)