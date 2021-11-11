import re



class Field():

	empty_field = ""

	def __init__(self, names):
		self.names = names

	def fix_empty_fields(self, output):
		# TODO: Make this harder to forget to call
		for name in self.names:
			if not name in output or not output[name]:
				output[name] = self.empty_field

	def get(self, input, output, *args, **kwargs):
		pass



class AttrField(Field):
	def __init__(self, attr_name):
		super().__init__([attr_name])
		self.attr_name = attr_name

	def parse(self, soup):
		try:
			return soup[self.attr_name]
		except KeyError as e:
			pass

	def get(self, soup, out_data):
		out_data[self.attr_name] = self.parse(soup)
		self.fix_empty_fields(out_data)


class ReField(Field):
	'''
	Extracts fields based on names subgroups of the RE found in the inner HTML of the given soup
	'''
	
	value_group_name = "value"
	max_len = 500

	def __init__(self, pattern, *args):
		super().__init__(list(args))
		self.re = re.compile(pattern)

	def get(self, soup, out_data, start_index = 0, skip_unmatched = True):
		'''
		Only will search from the given start index
		Also returns the end of its search index
		'''
		inner_html = soup if isinstance(soup, str) else soup.decode_contents()
		#inner_html = inner_html[:start_index + self.max_len]
		match = self.re.search(inner_html[start_index:])
		if match:
			for i, name in enumerate(self.names):
				out_data[name] = match.group(self.value_group_name + str(i))
			self.fix_empty_fields(out_data)
			return start_index + match.end()
		else:
			self.fix_empty_fields(out_data)
			return len(inner_html) if skip_unmatched else start_index



class TranslatedField(Field):
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



class SetField(Field):
	'''
	This is a mix-in to handle a field that contains data best understood as a set
	Still returns the data a (newly sorted) string for consistency
	'''
	def __init__(self, delimeter, *args, sort_by = lambda x : x, **kwargs):
		super().__init__(*args, **kwargs)
		self.delimeter = delimeter
		self.sort_by = sort_by

	def get(self, input, output, *args, **kwargs):
		r = super().get(input, output, *args, **kwargs)
		for name in self.names:
			if name in output and output[name]:
				fs = set(map(str.strip, output[name].split(self.delimeter)))
				output[name] = self.delimeter.join(sorted(fs, key=self.sort_by))
		return r



class MappedField(Field):
	'''
	Alters the string by applying the function to all character
	Gives the function the arguments (string, index)
	'''
	def __init__(self, func, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.func = func 

	def get(self, input, output, *args, **kwargs):
		r = super().get(input, output, *args, **kwargs)
		for name in self.names:
			if name in output and output[name]:
				s = ""
				for i in range(len(output[name])):
					s += self.func(output[name], i)
				output[name] = s
		return r



class TranslatedAttrField(TranslatedField, AttrField):
	pass

class SetTranslatedAttrField(SetField, TranslatedAttrField):
	pass

class TranslatedReField(TranslatedField, ReField):
	pass