import bs4

from fields import AttrField, TranslatedAttrField, TranslatedReField
from coalation import coalate

#cards_page = requests.get('https://tcg.build-divide.com/official/cards/search')
cards_path = "Cards.html"
extra_cards_path = "Translations.txt"

fields = [
	TranslatedAttrField({"ユニット" : "Unit", "コマンド" : "Command", "テリトリー":"Territory"}, "data-card-type"),
	AttrField("data-rarity"),
	AttrField("data-product-name"),
	AttrField("data-title"),
	AttrField("data-illustrator"),
	TranslatedAttrField({"不死" : "Undead", "魔族" : "Demon tribe", "呪術" : "Curse"}, "data-attribute"),
	AttrField("data-power"),
	AttrField("data-hit"),
	AttrField("data-cost-color1"),
	TranslatedAttrField({"赤" : "Red", "白" : "White", "青" : "Blue", "黒" : "Black"}, "data-color-name1"),
	AttrField("data-cost-colorless"),
	AttrField("data-description"),
	TranslatedAttrField({"バスター" : "Buster"}, "data-trigger-name"),
	AttrField("data-flavor-text"),
	AttrField("data-is-ace-name"),
	AttrField("data-image-url")
]

def parse_html_cards(soup, fields):
	cards = []
	for card in soup.find_all("div", {"class":"card-list-item__card__img"}):
		card_data = dict()
		for field in fields:
			field.get(card, card_data)
		cards.append(card_data)
	return cards

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
pattern += r"(?P<value6>[^(]([^=/]|[kles]/|" + sp + r"|" + br + r")*)\." # Description

print(pattern)

re_fields = [
	#ReField(r"<[br/]+>(?P<value>[\w ]+)<[br/]+>(<div>)?[^<]*<[br/]+>", "tl-title"),
	TranslatedReField(
		{"Zombie" : "Undead"},
		pattern,
		"tl-title", "data-color-name1", "data-cost-color1", "data-cost-colorless", "data-power", "data-attribute", "tl-description"
	)
	#ReField(r"(/ Hit: (?P<value>\d+))? *<[br/]", "data-hit"),
]

def parse_text_cards(text, fields):
	#print(body)
	i = 0
	cards = []
	while i < len(text):
		card_data = dict()
		for field in fields:
			i = field.get(text, card_data, i)
		if card_data:
			print(card_data["tl-title"])
			cards.append(card_data)
	return cards


def add_extras(raw_text, cards):
	for card in cards:
		pass


if __name__=="__main__":
	cards = None
	with open(cards_path) as cards_file:
		cards = parse_html_cards(bs4.BeautifulSoup(cards_file, 'html.parser'), fields)
	print("{} cards parsed!".format(len(cards)))
	extra_cards = None
	with open(extra_cards_path) as cards_file:
		extra_cards = parse_text_cards(cards_file.read(), re_fields)
	print("External data for {} cards parsed!".format(len(extra_cards)))
	#for card in extra_cards:
	#	print(card)
	coalated_cards = coalate(cards, lambda x : len(x['data-description']), extra_cards, lambda x : len(x['tl-description']))
	print("{} cards successfully coalated!".format(len(coalated_cards)))