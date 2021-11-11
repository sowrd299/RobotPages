class ParseDidntAdvanceError(Exception):
	pass

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


def parse_text_cards(text, fields, unmatchable_field = None):
	'''
	Uses field object to extract data of interest from a text file
	Assumes it will receive at least one ReFields 
	'''
	#print(body)
	i = 0
	last_i = -1
	cards = []
	while i < len(text):

		if i != last_i:
			last_i = i
		elif unmatchable_field:
			print("Skipping invalid data...")
			i = unmatchable_field.get(text, {}, i)
		else:
			raise ParseDidntAdvanceError

		#print("Parsing card from {}...".format(i))
		card_data = dict()
		for field in fields:
			i = field.get(text, card_data, i, not unmatchable_field) or i
		if card_data:
			print("Parsed {}...".format(card_data["tl-title"] if "tl-title" in card_data else card_data))
			cards.append(card_data)
	return cards

