import re


class AttrField():
	def __init__(self, attr_name):
		self.attr_name = attr_name
		self.names = [attr_name]

	def parse(self, soup):
		return soup[self.attr_name]

	def get(self, soup, out_data):
		out_data[self.attr_name] = self.parse(soup)


class ReField():
	'''
	Extracts fields based on names subgroups of the RE found in the inner HTML of the given soup
	'''
	
	value_group_name = "value"

	def __init__(self, pattern, *args):
		self.re = re.compile(pattern)
		self.names = list(args)

	def get(self, soup, out_data, start_index = 0):
		'''
		Only will search from the given start index
		Also returns the end of its search index
		'''
		inner_html = soup if isinstance(soup, str) else soup.decode_contents()
		match = self.re.search(inner_html, start_index)
		if match:
			for i, name in enumerate(self.names):
				out_data[name] = match.group(self.value_group_name + str(i))
			return match.end()
		else:
			return len(inner_html)



class TranslatedField():
	'''
	This is a mix-in
	'''
	def __init__(self, translations, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.translations = translations

	def get(self, input, output, *args, **kwargs):
		r = super().get(input, output, *args, **kwargs)
		for name in self.names:
			for k,v in self.translations.items():
				if name in output and output[name]:
					output[name] = output[name].replace(k,v)
		return r

class TranslatedAttrField(TranslatedField, AttrField):
	pass

class TranslatedReField(TranslatedField, ReField):
	pass