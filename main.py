import bs4
import requests
import shutil
from os import path

from parsing import *
from fields import AttrField, TranslatedAttrField, TranslatedReField, SetField, SetTranslatedAttrField
from coalation import coalate

#cards_page = requests.get('https://tcg.build-divide.com/official/cards/search')
cards_path = "Cards.html"
extra_cards_path = "Translations.txt"
template_path = "WikiTemplate.txt"
image_dir_path = "ImageDownloads"

fields = [
	TranslatedAttrField({"ユニット" : "Unit", "コマンド" : "Command", "テリトリー":"Territory"}, "data-card-type"),
	AttrField("data-rarity"),
	AttrField("data-product-name"),
	AttrField("data-title"),
	AttrField("data-illustrator"),
	SetTranslatedAttrField("/", {
		"不死" : "Undead",
		"魔族" : "Demon tribe",
		"呪術" : "Curse",
		"人間" : "Human",
		"グラド" : "Grado",
		"兵器" : "Weapon",
		"理力" : "Force",
		"天使" : "Angel",
		"精霊" : "Spirit",
		"闘気" : "Battle aura",
		"獣" : "Beast",
		"テノス" : "Tinos",
		"天変" : "Natural calamity",
		"竜" : "Dragon",
		"異相" : "Unusual look",
		"観測者" : "Observer",
		"巨人" : "Giant"
	}, "data-attribute"),
	AttrField("data-power"),
	AttrField("data-hit"),
	AttrField("data-cost-color1"),
	TranslatedAttrField({"赤" : "Red", "白" : "White", "青" : "Blue", "黒" : "Black"}, "data-color-name1"),
	AttrField("data-cost-colorless"),
	TranslatedAttrField({"--BR--" : ""}, "data-description"),
	TranslatedAttrField({"バスター" : "Buster"}, "data-trigger-name"),
	AttrField("data-flavor-text"),
	AttrField("data-is-ace-name"),
	AttrField("data-image-url")
]

sp = r" *"
br = sp + r"\n" + sp

pattern = r"\n[A-F0-9\-]+ ?\n"
pattern += r"(?P<value0>[\w #\"',]+)" + br # Title
pattern += r"[^\n]*" + br # Card type
pattern += r"(Total cost:" + sp + r"\d/" + sp + r"(?P<value1>\w*):" + sp # cost
pattern += r"(?P<value2>\d)" + sp # Color cost
pattern += r"(/"+sp+r"Colorless:"+sp+r"(?P<value3>\d))?" + br + r")?" # Colorless cost
pattern += r"(POWER: (?P<value4>\d+)[\w /:]*\d" + br + r")?" # Power and hit
pattern += r"(\((?P<value5>[\w/ ]+)\)" + br + r")?" # Attribute
#pattern += r"(?P<value6>([^=/(]|" + sp + r"|" + br + r")([^=/]|" + sp + r"|" + br + r")*)(<img|<a|$)" # Description
pattern += r"(?P<value6>[^(]([^=/]|[kles]/|" + sp + r"|" + br + r")*\.)" # Description

#print(pattern)

re_fields = [
	#ReField(r"<[br/]+>(?P<value>[\w ]+)<[br/]+>(<div>)?[^<]*<[br/]+>", "tl-title"),
	TranslatedReField(
		{"Zombie" : "Undead"},
		pattern,
		"tl-title", "data-color-name1", "data-cost-color1", "data-cost-colorless", "data-power", "data-attribute", "tl-description"
	),
	#ReField(r"(/ Hit: (?P<value>\d+))? *<[br/]", "data-hit"),
	SetField("/", ["data-attribute"])
]



def download_image(url, file_path):
	'''
	Based on code from: https://towardsdatascience.com/how-to-download-an-image-using-python-38a75cfa21c
	'''

	extension = "." + url.split(".")[-1]
	if file_path[-len(extension):] != extension:
		file_path += extension
	
	if not path.isfile(file_path):
		r = requests.get(url, stream = True)
		r.raw.decode_conent = True

		with open(file_path, 'wb') as file:
			shutil.copyfileobj(r.raw, file)

	return file_path



if __name__=="__main__":

	# Parse the original cards
	cards = None
	with open(cards_path) as cards_file:
		cards = parse_html_cards(bs4.BeautifulSoup(cards_file, 'html.parser'), fields)
	print("{} cards parsed!".format(len(cards)))

	# Parse the extra data for the cards
	extra_cards = None
	with open(extra_cards_path) as cards_file:
		extra_cards = parse_text_cards(cards_file.read(), re_fields)
	print("External data for {} cards parsed!".format(len(extra_cards)))

	# Coalate that data
	coalated_cards = coalate(cards, lambda x : len(x['data-description']), extra_cards, lambda x : len(x['tl-description']))
	print("{} cards successfully coalated!".format(len(coalated_cards)))

	# Get the images
	print("Downloading images...")
	for card in coalated_cards:
		image_path = download_image(card["data-image-url"], path.join(image_dir_path, card["tl-title"].replace(" ","").replace(",","").replace("\"","")))
		card["image-name"] = path.basename(image_path)

	# Format the wiki pages
	with open(template_path) as template_file:
		template = template_file.read()
		for card in coalated_cards:
			print("\n")
			print(template.format(**card))
			input("\nPress to continue...")
