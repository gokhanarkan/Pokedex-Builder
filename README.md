# Pokedex-Builder

---

Install packages: ```pip install -r requirements.txt```
Run: ```python src/pokedex_builder.py```

---

I decided to write my own minimalistic Pokédex. You never know you need until you need it.

A day ago, I published [this repo](https://github.com/gokhj/get_pokemon_names), and it gave me the idea to scrape the necessary information from different resources to create my own database.

Although the pokedex app is currently private since it's in development, I am sharing the scraping algorithm and current data publicly for everyone to use.

Note that this is an ongoing project and the current data set is expanding regularly.

I will add a client file to create objects, access generic data soon.

Huge thanks to https://pokemondb.net for providing the information.

---

# UPDATES

##### 21/12/2019
I now added a lot of useful information from tables. The csv file contains more than enough data for my app but I will try to scrape more in the future. At this time, I will create a client file to access the information easily for other people.

##### 23/12/2019
I had a chance to update evolution levels. I will also add a table concerning moves learnt by leveling up. I have a plan to create a file, moves.csv, and add all the moves details later.

---

# TODO

- Some data in tables missing for gen8. Pokemondb didn't provide these details yet, I'll try to find external source for similar information.
- moves.csv