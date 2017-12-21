from bs4 import BeautifulSoup

import urllib2
import os
import json
import re
import CurrencyConverter

### CONFIG
ysl_kate_url_CA = 'https://www.ysl.com/ca/shop-product/women/kate'

# Use a dummy user agent for YSL site
dummy_user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-Agent' : dummy_user_agent }

PRINT_ENDPOINTS = False
countries_file_name = 'countries.csv'

whitelist_file_name = 'whitelist.json'

output_encoding = 'utf8'
output_file_name_base = 'bags_'
output_folder_name = 'output'

sanitized_currencies = {}
sanitized_currencies_file_name = 'sanitized_currencies.json'

standardized_currency = 'CAD'

### HELPERS

class Item:
	def __init__(self, name, price, currency, brand):
		name = name.strip().replace(',','')
		self.name 	= name.encode(output_encoding)
		self.price 	= price
		self.currency = currency.encode(output_encoding)
		self.brand 	= brand.encode(output_encoding)

	def attach_std(self, std_price, std_currency):
		self.std_price 	= std_price
		self.std_currency 	= std_currency.encode(output_encoding)

	def get_display_string(self):
		if not hasattr(self, 'std_price'):
			return 'Item missing standardized price!\n'
		if not hasattr(self, 'std_currency'):
			return 'Item missing standardized currency!\n'
		return '{},{},{},{},{},{}\n'.format(self.name, \
											self.price, \
											self.currency, \
											self.std_price, \
											self.std_currency, \
											self.brand)

def _read_sanitized_currencies():
	currency_list = {}
	with open(sanitized_currencies_file_name) as data_file:
		currency_list = json.load(data_file)
	return currency_list

def _sanitize_currency(currency, country):
	global sanitized_currencies
	if sanitized_currencies == {}:
		sanitized_currencies = _read_sanitized_currencies()

	if country in sanitized_currencies:
		currency = sanitized_currencies[country]
	else:
		currency = re.sub(r'[^a-zA-Z]' ,'', currency)
	return currency

def fetch_prices(soup, country):
	items = soup.find_all('div', class_='infoMouseOver') 
	names = []
	prices = []
	currencies = []
	item_codes = []
	for item in items:
		names.append( item.find('span', class_='inner modelName') )
		prices.append( item.find('span', class_='value') )
		currencies.append( item.find('span', class_='currency') )
		item_code = item.find('div', class_='modelName outer')['data-ytos-opt']
		item_code = json.loads(item_code)['options']['itemSiteCode']
		item_codes.append( item_code )

	output = []
	
	for idx in range (0, len(names)):
		currency = currencies[idx].get_text()
		currency = _sanitize_currency(currency, country)
		price = (prices[idx])['data-ytos-price']
		output.append(Item(names[idx].get_text(), 	\
							float(price), 		\
							currency, 	\
							item_codes[idx]))
	return output

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
			country_string = country.get_text()
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

def _get_whitelist():
	with open(whitelist_file_name) as data_file:
		whitelist = json.load(data_file)
	return whitelist

def fetch_std_prices(database):
	for item in database:
		std_currency = standardized_currency
		std_price = CurrencyConverter.convert(item.price, item.currency, std_currency)
		item.attach_std(std_price, std_currency)
	return database

### OUTPUT
if __name__ == '__main__':
	# Parsing the soup for eligible countries
	countries = _get_selling_countries()
	whitelist = _get_whitelist()

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
		if country in whitelist:
			if whitelist[country] == False:
				continue
		else:
			print country + ' does not exist in whitelist, skipping'
			continue
		print (country)
		output_file_name = (output_file_name_base + country + '.csv').replace(' ', '_')
		output_file_path = os.path.join(output_folder_name, output_file_name)

		req = urllib2.Request(countries[country], headers=headers)
		response = urllib2.urlopen(req)
		page = response.read()

		# Parsing the soup for bags
		soup = BeautifulSoup(page, 'html.parser')
		database = fetch_prices(soup, country)
		database = fetch_std_prices(database) # !!AYS is pass by ref supported in Python?

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
