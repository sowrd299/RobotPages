import bs4
import requests
import shutil
import webbrowser
from os import path

from parsing import *
from fields import AttrField, TranslatedAttrField, TranslatedReField, SetField, SetTranslatedAttrField, MappedField, ReField
from coalation import coalate, coalate_unmatched, merge_entries

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
		"魔族" : "Demonic tribe",
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
translations = {"Zombie" : "Undead", "Decoy" : "[[Decoy]]", "Blitz" : "[[Blitz]]", "[Territory]" : "<Territory>"}

#print(pattern)

re_fields = [
	#ReField(r"<[br/]+>(?P<value>[\w ]+)<[br/]+>(<div>)?[^<]*<[br/]+>", "tl-title"),
	#"tl-title", "data-color-name1", "data-cost-color1", "data-cost-colorless", "data-power", "data-attribute", "tl-description"
	ReField(r"^[\\A-Za-z\d\-]+ ?\n"),
	ReField(r"^(?P<value0>[\w #\"'\-,]+)" + br, "tl-title"),
	ReField(r"^(Unit|Command|Territory)[^\n]*" + br),
	ReField(
		r"^Total cost:" + sp + r"\d/" + sp + r"(?P<value0>\w*):" + sp + r"(?P<value1>\d)" + sp + r"(/"+sp+r"[Cc]olorless:"+sp+r"(?P<value2>\d))?" + br,
		"data-color-name1", "data-cost-color1", "data-cost-colorless"
	),
	ReField(r"^POWER: (?P<value0>\d+)[\w /:]*\d" + br, "data-power"),
	TranslatedReField(translations, r"^\((?P<value0>[\w/ ]+)\)" + br, "data-attribute"),
	TranslatedReField(translations, r"^(?P<value0>[^(]([^=/]|[kles]/|" + sp + r"|" + br + r")*([\.\])]|000))" + br, "tl-description"),

	#ReField(r"(/ Hit: (?P<value>\d+))? *<[br/]", "data-hit"),
	SetField("/", ["data-attribute"]),
	MappedField(lambda s, i : s[i] if s[i] != "\n" or s[i-1] in ".]>" or s[i+1] in ".[<" else " " if s[i-1] != " " and s[i+1] != " " else "", ["tl-description"])
]

unmatchable_field = ReField(r"^[\n]*\n")



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



def format_compare_entries(*entries, col_size = 30):
	'''
	Displays a side-by-side comparision of the given entries
	'''
	cols = set()
	for entry in entries:
		for col in entry:
			cols.add(col)
	text = " "*col_size + "".join("|{1:<{0}}".format(col_size, "Entry {}".format(i+1)) for i in range(len(entries)))
	for col in cols:
		entry_text = "".join("|{1:<{0}}".format(col_size, entry[col] if col in entry else "") for entry in entries)
		text += "\n{1:<{0}}{2}".format(col_size, col, entry_text)
	return text


if __name__=="__main__":

	# Parse the original cards
	cards = None
	with open(cards_path) as cards_file:
		cards = parse_html_cards(bs4.BeautifulSoup(cards_file, 'html.parser'), fields)
	print("{} cards parsed!".format(len(cards)))

	# Parse the extra data for the cards
	extra_cards = None
	with open(extra_cards_path) as cards_file:
		extra_cards = parse_text_cards(cards_file.read(), re_fields, unmatchable_field)
	print("\nExternal data for {} cards parsed!".format(len(extra_cards)))

	# Coalate that data
	uncoalated_buckets = dict()
	coalated_cards = coalate(cards, lambda x : len(x['data-description']), extra_cards, lambda x : len(x['tl-description']), uncoalated_buckets = uncoalated_buckets)
	print("\n{} cards successfully coalated!".format(len(coalated_cards)))
	print("{} keys uncoalated!".format(len(uncoalated_buckets)))

	# Check for typos
	potential_matchs = coalate_unmatched(uncoalated_buckets, 2)
	print("...of those, {} potential typos found!".format(len(potential_matchs)))
	for i,match in enumerate(potential_matchs):
		while True:
			print("\n{}/{}".format(i+1,len(potential_matchs)))
			choice = input("Do these match?\n\n{}\n\nIf so, input the number of the one without a typo (\".\" to inspect): ".format(format_compare_entries(*match)))
			if choice == ".":
				for entry in match:
					if "data-image-url" in entry:
						webbrowser.open(entry["data-image-url"], 2)
			elif choice:
				i = int(choice) - 1
				coalated_cards.append(merge_entries(match[i], match[(i+1) % len(match)]))
				print("Typo fixed!")
				break
			else:
				break

	print("After typo corrections, {} cards successfully coalated!".format(len(coalated_cards)))

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
