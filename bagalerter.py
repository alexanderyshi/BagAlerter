from bs4 import BeautifulSoup
import urllib2
import os

### CONFIG
ysl_kate_url = 'https://www.ysl.com/ca/shop-product/women/kate'
dummy_user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-Agent' : dummy_user_agent }

url = ysl_kate_url

file_name ='bags.csv'
output_encoding = 'utf8'

### HELPERS

class Item:

	def __init__(self, name, price, currency, brand):
		self.name 	= name.encode(output_encoding)
		self.price 	= price.replace(',','').encode(output_encoding)
		self.currency = currency.encode(output_encoding)
		self.brand 	= brand.encode(output_encoding)

	def get_display_string(self):
		return '{},{},{},{}\n'.format(self.name, self.price, self.currency, self.brand)

def _parse_by_name():
	### these are of type <class 'bs4.element.ResultSet'>
	names = soup.find_all('span', class_='inner modelName')
	prices = soup.find_all('span', class_='value')
	currencies = soup.find_all('span', class_='currency')

	if prices[0].get_text() == '':
		prices = prices[1:]
		print 'culled empty price'

	output = []
	
	for idx in range (0, len(names)):
		output.append(Item(names[idx].get_text().strip(), 	\
							prices[idx].get_text(), 		\
							currencies[idx].get_text(), 	\
							'YSL'))
	return output

# !!AYS not working
def _parse_by_relation():
	### these are of type <class 'bs4.element.ResultSet'>
	items = soup.find_all('div', class_='infoMouseOver')

	os.remove(file_name)
	f = open(file_name, 'a')
	for item in items:
		for child in item.children:
			print child
			f.write(child.encode('utf16'))
	f.close()

### OUTPUT

# Getting the web page
req = urllib2.Request(ysl_kate_url, headers=headers)
response = urllib2.urlopen(req)
page = response.read()

# Parsing the soup
soup = BeautifulSoup(page, 'html.parser')
database = _parse_by_name()

# Output formatting
if os.path.isfile(file_name):
	os.remove(file_name)

f = open(file_name, 'a')
for item in database:
	display_string = item.get_display_string()
	f.write(display_string)
f.close()
