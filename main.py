import requests
import bs4

from fields import AttrField, TranslatedAttrField, ReField

#cards_page = requests.get('https://tcg.build-divide.com/official/cards/search')
cards_path = "Cards.html"
extra_page_urls = ["http://freedomduo-hobby.blog.jp/archives/11357884.html"]

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

div = r"</?div>"
br = r"<br/?>" 
sp = r"( |"+div+r")*"
br = r"("+div+r"|"+br+r")( |"+br+r"|"+div+r")*" #sp + r"(<[br/]+>)" + sp

pattern = r"((img|src|a)[^<>]*>)" + br
pattern += r"(?P<value>[\w #\"',]+)" + br # Title
pattern += r"[^<]*" + br # Card type
pattern += r"(Total cost:" + sp + r"\d/" + sp + r"(?P<value1>\w*):" + sp # cost
pattern += r"(?P<value2>\d)/" + sp # Color cost
pattern += r"(Colorless: (?P<value3>\d))?" + br + r")?" # Colorless cost
pattern += r"(POWER: (?P<value4>\d+)[\w /:]*\d)?" + br # Power and hit
pattern += r"(\((?P<value5>[\w/ ]+)\)" + br + r")?" # Attribute
#pattern += r"(?P<value6>([^=/(]|" + sp + r"|" + br + r")([^=/]|" + sp + r"|" + br + r")*)(<img|<a|$)" # Description
pattern += r"(?P<value6>([^=/(]|\w\(|" + sp + r"|" + br + r")*)(<img|<a)" # Description

print(pattern)

re_fields = [
	#ReField(r"<[br/]+>(?P<value>[\w ]+)<[br/]+>(<div>)?[^<]*<[br/]+>", "tl-title"),
	ReField(pattern, "tl-title", "data-color-name1", "data-cost-color1", "data-cost-colorless", "data-power", "data-attribute", "tl-description")
	#ReField(r"(/ Hit: (?P<value>\d+))? *<[br/]", "data-hit"),
]

def parse_text_cards(soup, fields):
	body = soup.find("div", {"class":"article-body-inner"}).decode_contents() # this might not actually be an efficiency gain :(
	#print(body)
	i = 0
	cards = []
	while i < len(body):
		card_data = dict()
		for field in fields:
			i = field.get(body, card_data, i)
		if card_data:
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
	for url in extra_page_urls:
		extra_page = requests.get(url).content
		extra_cards = parse_text_cards(bs4.BeautifulSoup(extra_page, 'html.parser'), re_fields)
		for card in extra_cards:
			print(card['tl-title'] if 'tl-title' in card else card)
			#print(card)