
def parse_html_cards(soup, fields):
	'''
	Uses Field objects to extract data of interest from beautiful soup
	'''
	cards = []
	for card in soup.find_all("div", {"class":"card-list-item__card__img"}):
		card_data = dict()
		for field in fields:
			field.get(card, card_data)
		cards.append(card_data)
	return cards


def parse_text_cards(text, fields):
	'''
	Uses field object to extract data of interest from a text file
	Assumes it will receive at least one ReFields 
	'''
	#print(body)
	i = 0
	cards = []
	while i < len(text):
		card_data = dict()
		for field in fields:
			i = field.get(text, card_data, i) or i
		if card_data:
			print("{}...".format(card_data["tl-title"]))
			cards.append(card_data)
	return cards

