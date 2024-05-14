from zenrows import ZenRowsClient
from module_package import *


@retry
def get_zenrowa(url, params=None):
    api_list = ['9189cd9423ce5a590dea040cc142b474cc612567', '0ed1b4d860a82d93b51edce0fe8d32c949d7cbc7', '6f269d15ae0a60430ed5b5043197076de785fc91']
    for api_key in api_list:
        client = ZenRowsClient(api_key)
        r = client.get(url, params = params)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        elif 499 >= r.status_code >= 400:
            print(f'client error response, status code {r.status_code} \nrefer: {r.url}')
            status_log(r)
        elif 599 >= r.status_code >= 500:
            print(f'server error response, status code {r.status_code} \nrefer: {r.url}')
            count = 1
            while count != 10:
                print('while', count)
                client = ZenRowsClient("0ed1b4d860a82d93b51edce0fe8d32c949d7cbc7")
                r = client.get(url, params=params)
                print('status_code: ', r.status_code)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    return soup
                else:
                    print('retry ', count)
                    count += 1
                    time.sleep(count * 2)
        else:
            status_log(r)
            return None


if __name__ == '__main__':
    timestamp = datetime.now().date().strftime('%Y%m%d')
    file_name = os.path.basename(__file__).rstrip('.py')
    url = 'https://www.carolina.com/'
    base_url = 'https://www.carolina.com'
    soup = get_zenrowa(url, params = {'js_render': 'false'})
    content = soup.find('li', class_='nav-item c-nav-menu-link').find_all('li', class_='row c-nav-menu-l1')
    for single_content in content:
        inner_content = single_content.find('div', class_='c-nav-menu-subnav col-12 col-lg-7')
        if inner_content.find('ul', class_='row'):
            all_urls = inner_content.find('ul', class_='row').find_all('li')
            for single_url in all_urls:
                main_url = f"{base_url}{single_url.a['href']}"
                inner_request = get_zenrowa(main_url, params = {'js_render': 'false'})
                '''GET PAGINATION'''
                if inner_request.find('ul', class_='c-pagination pagination justify-content-start pagination-lg'):
                    total_page = inner_request.find('ul', class_='c-pagination pagination justify-content-start pagination-lg').find_all(
                        'li')[-2].text.strip()
                    for i in range(0, int(total_page)):
                        number = int(i) * int(60)
                        page_link = f'{main_url}?Nf=product.cbsLowPrice%7CGT+0.0%7C%7Cproduct.startDate%7CLTEQ+1.71504E12%7C%7Cproduct.startDate%7CLTEQ+1.71504E12&No={number}&Nr=&'
                        page_soup = get_zenrowa(page_link, params = {'js_render': 'false'})
                        inner_data = page_soup.find_all('div', class_='c-feature-product qv-model')
                        for single_data in inner_data:
                            product_url = f'{base_url}{single_data.find('a')["href"]}'
                            print(product_url)
                            product_request = get_zenrowa(product_url, params = {'js_render': 'false'})
                            if product_request is None:
                                continue
                            '''PRODUCT NAME AND PRODUCT QUANTITY'''
                            try:
                                product_name = strip_it(product_request.find('div', class_='col prod-nav-title').text.strip())
                                if re.search('Pack of \d+', str(product_name)):
                                    product_quantity = re.search('Pack of \d+', str(product_name)).group().replace('Pack of', '').strip()
                                else:
                                    product_quantity = strip_it(product_request.find('input', attrs={'name': 'quantity'})['value'])
                            except:
                                product_name = ''
                                product_quantity = '1'
                            '''PRODUCT NAME'''
                            try:
                                product_id = strip_it(product_request.find('span', id='pdp-skuId').text.strip())
                            except:
                                product_id = ''
                            '''PRODUCT PRICE'''
                            try:
                                if product_request.find('span', class_='pdp-order-price'):
                                    product_price = strip_it(product_request.find('span', class_='pdp-order-price').text.strip())
                                elif product_request.find('div', class_='pdp-order-price'):
                                    product_price = strip_it(product_request.find('div', class_='pdp-order-price').text.strip())
                                else:
                                    product_price = ''
                            except Exception as e:
                                print('product price', e)
                                product_price = ''
                            print('current datetime------>', datetime.now())
                            dictionary = get_dictionary(product_ids=product_id, product_names=product_name,
                                                        product_quantities=product_quantity,
                                                        product_prices=product_price, product_urls=product_url)
                            articles_df = pd.DataFrame([dictionary])
                            articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first',
                                                        inplace=True)
                            if os.path.isfile(f'{file_name}.csv'):
                                articles_df.to_csv(f'{file_name}.csv', index=False, header=False,
                                                   mode='a')
                            else:
                                articles_df.to_csv(f'{file_name}.csv', index=False)
                            write_visited_log(product_id)
                else:
                    inner_data = inner_request.find_all('div', class_='c-feature-product qv-model')
                    for single_data in inner_data:
                        product_url = f'{base_url}{single_data.find('a')["href"]}'
                        print(product_url)
                        product_request = get_zenrowa(product_url, params = {'js_render': 'false'})
                        if product_request is None:
                            continue
                        '''PRODUCT NAME AND PRODUCT QUANTITY'''
                        try:
                            product_name = strip_it(product_request.find('div', class_='col prod-nav-title').text.strip())
                            if re.search('Pack of \d+', str(product_name)):
                                product_quantity = re.search('Pack of \d+', str(product_name)).group().replace(
                                    'Pack of', '').strip()
                            else:
                                product_quantity = strip_it(product_request.find('input', attrs={'name': 'quantity'})['value'])
                        except:
                            product_name = ''
                            product_quantity = '1'
                        '''PRODUCT NAME'''
                        try:
                            product_id = strip_it(product_request.find('span', id='pdp-skuId').text.strip())
                        except:
                            product_id = ''
                        '''PRODUCT PRICE'''
                        try:
                            if product_request.find('span', class_='pdp-order-price'):
                                product_price = strip_it(product_request.find('span', class_='pdp-order-price').text.strip())
                            elif product_request.find('div', class_='pdp-order-price'):
                                product_price = strip_it(product_request.find('div', class_='pdp-order-price').text.strip())
                            else:
                                product_price = ''
                        except Exception as e:
                            print('product price', e)
                            product_price = ''
                        print('current datetime------>', datetime.now())
                        dictionary = get_dictionary(product_ids=product_id, product_names=product_name,
                                                    product_quantities=product_quantity,
                                                    product_prices=product_price, product_urls=product_url)
                        articles_df = pd.DataFrame([dictionary])
                        articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first', inplace=True)
                        if os.path.isfile(f'{file_name}.csv'):
                            articles_df.to_csv(f'{file_name}.csv', index=False, header=False,
                                               mode='a')
                        else:
                            articles_df.to_csv(f'{file_name}.csv', index=False)
                        write_visited_log(product_id)
                write_visited_log(main_url)
        else:
            if 'distance-learning-science-kits' not in str(single_content):
                main_url = f"{base_url}{single_content.find('a', class_='c-nav-menu-l1-label')['href']}"
                inner_request = get_zenrowa(main_url, params = {'js_render': 'false'})
                '''GET PAGINATION'''
                if inner_request.find('ul', class_='c-pagination pagination justify-content-start pagination-lg'):
                    total_page = inner_request.find('ul', class_='c-pagination pagination justify-content-start pagination-lg').find_all(
                        'li')[-2].text.strip()
                    for i in range(0, int(total_page)):
                        number = int(i) * int(60)
                        page_link = f'{main_url}?Nf=product.cbsLowPrice%7CGT+0.0%7C%7Cproduct.startDate%7CLTEQ+1.71504E12%7C%7Cproduct.startDate%7CLTEQ+1.71504E12&No={number}&Nr=&'
                        page_soup = get_zenrowa(page_link, params = {'js_render': 'false'})
                        inner_data = page_soup.find_all('div', class_='c-feature-product qv-model')
                        for single_data in inner_data:
                            product_url = f'{base_url}{single_data.find('a')["href"]}'
                            print(product_url)
                            product_request = get_zenrowa(product_url, params = {'js_render': 'false'})
                            if product_request is None:
                                continue
                            '''PRODUCT NAME AND PRODUCT QUANTITY'''
                            try:
                                product_name = strip_it(product_request.find('div', class_='col prod-nav-title').text.strip())
                                if re.search('Pack of \d+', str(product_name)):
                                    product_quantity = re.search('Pack of \d+', str(product_name)).group().replace('Pack of', '').strip()
                                else:
                                    product_quantity = strip_it(product_request.find('input', attrs={'name': 'quantity'})['value'])
                            except:
                                product_name = ''
                                product_quantity = '1'
                            '''PRODUCT NAME'''
                            try:
                                product_id = strip_it(product_request.find('span', id='pdp-skuId').text.strip())
                            except:
                                product_id = ''
                            '''PRODUCT PRICE'''
                            try:
                                if product_request.find('span', class_='pdp-order-price'):
                                    product_price = strip_it(product_request.find('span', class_='pdp-order-price').text.strip())
                                elif product_request.find('div', class_='pdp-order-price'):
                                    product_price = strip_it(product_request.find('div', class_='pdp-order-price').text.strip())
                                else:
                                    product_price = ''
                            except Exception as e:
                                print('product price', e)
                                product_price = ''
                            print('current datetime------>', datetime.now())
                            dictionary = get_dictionary(product_ids=product_id, product_names=product_name,
                                                        product_quantities=product_quantity,
                                                        product_prices=product_price, product_urls=product_url)
                            articles_df = pd.DataFrame([dictionary])
                            articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first',
                                                        inplace=True)
                            if os.path.isfile(f'{file_name}.csv'):
                                articles_df.to_csv(f'{file_name}.csv', index=False, header=False,
                                                   mode='a')
                            else:
                                articles_df.to_csv(f'{file_name}.csv', index=False)
                            write_visited_log(product_id)
                else:
                    inner_data = inner_request.find_all('div', class_='c-feature-product qv-model')
                    for single_data in inner_data:
                        product_url = f'{base_url}{single_data.find('a')["href"]}'
                        print(product_url)
                        product_request = get_zenrowa(product_url, params = {'js_render': 'false'})
                        if product_request is None:
                            continue
                        '''PRODUCT NAME AND PRODUCT QUANTITY'''
                        try:
                            product_name = strip_it(product_request.find('div', class_='col prod-nav-title').text.strip())
                            if re.search('Pack of \d+', str(product_name)):
                                product_quantity = re.search('Pack of \d+', str(product_name)).group().replace('Pack of', '').strip()
                            else:
                                product_quantity = strip_it(product_request.find('input', attrs={'name': 'quantity'})['value'])
                        except:
                            product_name = ''
                            product_quantity = '1'
                        '''PRODUCT NAME'''
                        try:
                            product_id = strip_it(product_request.find('span', id='pdp-skuId').text.strip())
                        except:
                            product_id = ''
                        '''PRODUCT PRICE'''
                        try:
                            if product_request.find('span', class_='pdp-order-price'):
                                product_price = strip_it(product_request.find('span', class_='pdp-order-price').text.strip())
                            elif product_request.find('div', class_='pdp-order-price'):
                                product_price = strip_it(product_request.find('div', class_='pdp-order-price').text.strip())
                            else:
                                product_price = ''
                        except Exception as e:
                            print('product price', e)
                            product_price = ''
                        print('current datetime------>', datetime.now())
                        dictionary = get_dictionary(product_ids=product_id, product_names=product_name,
                                                    product_quantities=product_quantity,
                                                    product_prices=product_price, product_urls=product_url)
                        articles_df = pd.DataFrame([dictionary])
                        articles_df.drop_duplicates(subset=['product_id', 'product_name'], keep='first', inplace=True)
                        if os.path.isfile(f'{file_name}.csv'):
                            articles_df.to_csv(f'{file_name}.csv', index=False, header=False,
                                               mode='a')
                        else:
                            articles_df.to_csv(f'{file_name}.csv', index=False)
                        write_visited_log(product_id)
                write_visited_log(main_url)
