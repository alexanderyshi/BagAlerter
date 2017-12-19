from bs4 import BeautifulSoup
import urllib2

ysl_kate_url = 'https://www.ysl.com/ca/shop-product/women/kate'

dummy_user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-Agent' : dummy_user_agent }
req = urllib2.Request(ysl_kate_url, headers=headers)
response = urllib2.urlopen(req)
page = response.read()

 # Parsing the soup
soup = BeautifulSoup(page, 'html.parser')

### these are of type <class 'bs4.element.ResultSet'>
# items = soup.find_all('div', class_='infoMouseOver')
names = soup.find_all('span', class_='inner modelName')
prices = soup.find_all('span', class_='value')
currencies = soup.find_all('span', class_='currency')

if prices[0].get_text() == '':
	prices = prices[1:]
	print 'culled empty price'

for item in range (0, len(names)):
	display_string = names[item].get_text() + ':' + prices[item].get_text() + currencies[item].get_text()
	print display_string

