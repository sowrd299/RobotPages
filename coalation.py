# A file for coaliting different sets of data into repeated objects

from typing import DefaultDict


def get_cols(data_set):
	'''
	Returns the collumns of a data set
		as represented by the keys of its entries
	'''
	cols = set()
	for entry in data_set:
		for col in entry:
			cols.add(col)
	return cols	


def merge_entries(*entries):
	'''
	Returns an entry with all data from both given entries
	'''
	new_entry = dict()
	for entry in entries:
		new_entry.update(entry)
	return new_entry


def coalate(*args):
	'''
	Takes each data set as lists of dictionaries (entries)
	Takes (data set, sort function, data set, sort function)
	'''
	data_sets = [args[i] for i in range(0, len(args), 2)]
	sort_funcs = [args[i] for i in range(1, len(args), 2)]

	cols = tuple(get_cols(data_sets[0]).intersection(*(get_cols(s) for s in data_sets[1:])))

	# put entries into buckets for fast coalation
	keys = set()
	buckets = []
	for data_set, sort_func in zip(data_sets, sort_funcs):
		set_buckets = DefaultDict(list)
		for entry in data_set:
			key = tuple((entry[col] if col in entry else None) for col in cols)
			keys.add(key)
			set_buckets[key].append(entry)
		for key, bucket in set_buckets.items():
			bucket.sort(key = sort_func)
		buckets.append(set_buckets)
	
	# Ascociate data!
	coalated_entries = []
	uncoalated_keys = []
	for key in keys:
		key_buckets = [set_buckets[key] for set_buckets in buckets if key in set_buckets]
		if len(key_buckets) == len(data_sets):
			num_entries = min([len(bucket) for bucket in key_buckets])
			for i in range(num_entries):
				coalated_entry = merge_entries(*(key_bucket[i] for key_bucket in key_buckets))
				coalated_entries.append(coalated_entry)
		else:
			uncoalated_keys.append(key)

	print("{} keys uncoalated!".format(len(uncoalated_keys)))
	
	return coalated_entries