import faker
import random
from datetime import datetime
from datetime import timedelta
from random import randrange
from collections import OrderedDict
from faker.providers import misc, lorem, internet, company, file, currency, geo, job

fake = faker.Faker()
fake.add_provider(misc)
fake.add_provider(lorem)
fake.add_provider(internet)
fake.add_provider(company)
fake.add_provider(file)
fake.add_provider(currency)
fake.add_provider(geo)
fake.add_provider(job)

def get_fake_id(length):
	length = int(length)
	return fake.password(length=length, special_chars=False, digits=True, upper_case=True, lower_case=False)

def get_fake_uuid():
    return fake.uuid4()

def get_fake_text(range):
	max_chars = int(range)
	return fake.text(max_nb_chars=max_chars)

def get_fake_number(range):
	try:
		range_list = range.split(",", 1)
		range_list[0] = int(range_list[0])
		range_list[1] = int(range_list[1])
	except:
		range_list = [0, 1000]
	return random.randint(range_list[0], range_list[1])

def get_fake_float(range):
	try:
		range_list = range.split(",", 1)
		range_list[0] = float(range_list[0])
		range_list[1] = float(range_list[1])
	except:
		range_list = [0.0, 1000.0]	
	return round(random.uniform(range_list[0], range_list[1]),2)

def get_fake_name(name_type):
	if name_type == "first":
		return fake.first_name()
	else:
		if name_type == "last":
			return fake.last_name()
		else:
			return fake.first_name() + " " + fake.last_name()

def get_fake_timestamp():
	timestamp = ""
	d1 = datetime.strptime('2001-01-01T01:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
	d2 = datetime.strptime('2025-01-01T01:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
	delta = d2 - d1
	int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
	random_second = randrange(int_delta)
	timestamp = d1 + timedelta(seconds =random_second)
	return timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

def get_fake_phone():
	return fake.phone_number()

def get_fake_email():
	return fake.ascii_email()

def get_fake_job_title():
	return fake.job().title()

def get_fake_location(locationtype):
	if locationtype == "street":
		return fake.street_address()
	if locationtype == "city":
		return fake.city()
	if locationtype == "state":
		return fake.state()
	if locationtype == "zipcode":
		return fake.postcode()
	if locationtype == "country":
		return fake.country()

def get_fake_boolean():
	return fake.boolean(chance_of_getting_true=50)

def get_fake_coordinates():
	return fake.local_latlng(country_code='US', coords_only=True)

def get_fake_company():
	return fake.company()

def get_fake_url():
	return fake.url()

def get_fake_ip():
	return fake.ipv4()

def get_fake_file_path(depth):
	return fake.file_path(depth=depth)

def get_fake_list_of_strings(num_items):
	list_of_values = fake.words(nb=num_items)
	string_list = ','.join(list_of_values)
	return string_list

def get_fake_list_of_ints(range_start, range_end):
	num_items = range_end - range_start
	number_list = random.sample(range(range_start, range_end), num_items * 10)
	mydict = {}
	for i in range(0, len(number_list), 2):
		mydict[number_list[i]] = 0.01

	fake_list = fake.random_elements(elements=OrderedDict(mydict), unique=False, length=num_items)
	return fake_list

def get_fake_option(option_list):
	return random.choice(option_list)