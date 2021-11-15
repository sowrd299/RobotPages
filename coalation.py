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
	Favores earlier entries if any columns conflict
	'''
	new_entry = dict()
	for entry in reversed(entries):
		new_entry.update(entry)
	return new_entry


def coalate_matched_buckets(merge_func, buckets):
	'''
	Coalate entries from all the given bucks (lists),
	assuming the buckets have been found to match
	an are already sorted by their hurisitic
	'''
	coalated_entries = []
	num_entries = min([len(bucket) for bucket in buckets])
	for i in range(num_entries):
		coalated_entry = merge_func(*(key_bucket[i] for key_bucket in buckets))
		if coalated_entry:
			coalated_entries.append(coalated_entry)
	return coalated_entries


def coalate(*args, uncoalated_buckets = dict()):
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
	for key in keys:
		key_buckets = [set_buckets[key] for set_buckets in buckets if key in set_buckets]
		if len(key_buckets) == len(data_sets):
			coalated_entries.extend(coalate_matched_buckets(merge_entries, key_buckets))
		else:
			uncoalated_buckets[key] = key_buckets

	return coalated_entries


def distinct_cols_to_tuple(*entries):
	'''
	If the elements have distinct columns, it will 
		return them as a tuple
	'''
	col_sets = set()
	for entry in entries:
		col_set = frozenset(entry.keys())
		if col_set in col_sets:
			return None
		else:
			col_sets.add(col_set)	
	return tuple(entries)


def coalate_unmatched(uncoalated_buckets, num_data_sets):
	'''
	Attempts to coalate unmatched buckets as output by the coalate unfunction
	Uses a relaxes version of the coaltion requirements
	'''
	key_size = len(next(iter(uncoalated_buckets)))
	potential_matches = []
	for i in range(key_size):
		key_mask = tuple(j != i for j in range(key_size))
		relaxed_buckets = DefaultDict(list)

		for old_key, buckets in uncoalated_buckets.items():
			relaxed_key = tuple(item for j, item in enumerate(old_key) if key_mask[j])
			relaxed_buckets[relaxed_key].extend(buckets)

		for relaxed_key, buckets in relaxed_buckets.items():
			if len(buckets) == num_data_sets:
				potential_matches.extend(coalate_matched_buckets(distinct_cols_to_tuple, buckets))

	return potential_matches