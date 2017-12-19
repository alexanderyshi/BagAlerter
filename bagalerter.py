from bs4 import BeautifulSoup
import urllib2
import os

### CONFIG
ysl_kate_url_CA = 'https://www.ysl.com/ca/shop-product/women/kate'
url = ysl_kate_url_CA

# Use a dummy user agent for YSL site
dummy_user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-Agent' : dummy_user_agent }

PRINT_ENDPOINTS = False
countries_file_name = 'countries.csv'

output_encoding = 'utf8'
output_file_name_base = 'bags_'
output_folder_name = 'output'

### HELPERS

class Item:
	# there are edge cases for handling currency,
	# i.e. Andorra uses "." and "," opposite from the north american way
	# France uses "," as "."
	# !!AYS take country code for edge cases?
	def __init__(self, name, price, currency, brand):
		self.name 	= name.encode(output_encoding)
		self.price 	= price.replace(',','').encode(output_encoding)
		self.currency = currency.encode(output_encoding)
		self.brand 	= brand.encode(output_encoding)

	def get_display_string(self):
		return '{},{},{},{}\n'.format(self.name, self.price, self.currency, self.brand)

def _parse_by_name(soup):
	### these are of type <class 'bs4.element.ResultSet'>
	names = soup.find_all('span', class_='inner modelName')
	prices = soup.find_all('span', class_='value')
	currencies = soup.find_all('span', class_='currency')

	if prices[0].get_text() == '':
		prices = prices[1:]
		print 'culled empty price'

	output = []
	
	# !!AYS replace the brand with some sort of site code pulled from the soup?
	for idx in range (0, len(names)):
		output.append(Item(names[idx].get_text().strip(), 	\
							prices[idx].get_text(), 		\
							currencies[idx].get_text(), 	\
							'YSL'))
	return output

# !!AYS not working
# def _parse_by_relation(soup):
	## these are of type <class 'bs4.element.ResultSet'>
	# items = soup.find_all('div', class_='infoMouseOver')

	# os.remove(output_file_name_base)
	# f = open(output_file_name_base, 'a')
	# for item in items:
	# 	for child in item.children:
	# 		print child
	# 		f.write(child.encode('utf16'))
	# f.close()

def _get_selling_countries():
	req = urllib2.Request(ysl_kate_url_CA, headers=headers)
	response = urllib2.urlopen(req)
	page = response.read()

	soup = BeautifulSoup(page, 'html.parser')
	countries = []
	urls = []

	regions = soup.find_all('div', class_='nations')
	for region in regions:
		for country in region.find_all('span', 'text'):
			country_string = country.get_text().replace(' ', '_')
			country_string.encode(output_encoding)
			countries.append(country_string)
		for url in region.find_all('a'):
			url_string = url['href']
			url_string.encode(output_encoding)
			urls.append(url_string)

	output = {}
	for idx in range(0, len(countries)):
		output[countries[idx]] = urls[idx]
	return output

### OUTPUT
# Parsing the soup for eligible countries
countries = _get_selling_countries()

if PRINT_ENDPOINTS:
	if os.path.isfile(countries_file_name):
		os.remove(countries_file_name)
	f = open(countries_file_name, 'a')
	for country in countries:
		display_string = '{}, {}\n'.format(country, countries[country])
		print(countries[country])
		f.write(display_string)
	f.close()

# Getting the web page
for country in countries:
	output_file_name = output_file_name_base + country + '.csv'
	output_file_path = os.path.join(output_folder_name, output_file_name)

	req = urllib2.Request(countries[country], headers=headers)
	response = urllib2.urlopen(req)
	page = response.read()

	# Parsing the soup for bags
	soup = BeautifulSoup(page, 'html.parser')
	database = _parse_by_name(soup)
	# Output formatting
	if not os.path.exists(output_folder_name):
		os.makedirs(output_folder_name)
	if os.path.isfile(output_file_path):
		os.remove(output_file_path)
	f = open(output_file_path, 'a')
	for item in database:
		display_string = item.get_display_string()
		f.write(display_string)
	f.close()
