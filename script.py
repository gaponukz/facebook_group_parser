from bot import TemplateBot
from setting import settings
from bs4 import BeautifulSoup
import xlsxwriter

class FacebookParser(TemplateBot):
    path_to_login = '//*[@id="mobile_login_bar"]/div[2]/a[1]'
    path_to_login_input = '//*[@id="m_login_email"]'
    path_to_password_input = '//*[@id="m_login_password"]'
    path_to_login_button = '//*[@id="u_0_4"]/button'
    TIME_TO_SCROLL = settings['program']['time_to_scroll']

    def parse(self, group_id: str = None) -> list:
        self.driver.get(f'https://m.facebook.com/groups/{group_id}#_=_')
        try: self.driver.find_element_by_xpath(self.path_to_login).click()
        except: pass
        self.driver.find_element_by_xpath(self.path_to_login_input).send_keys(self.username)
        self.driver.find_element_by_xpath(self.path_to_password_input).send_keys(self.password)
        self.protected_sleep(3.12345678876543234567898765434567890987654)
        self.driver.find_element_by_xpath(self.path_to_login_button).click()
        self.protected_sleep(5.2345678765432345678765434567876543)

        for _ in range(self.TIME_TO_SCROLL):
            self.driver.execute_script('scrollTo(0, 1000000000000000)')
            self.protected_sleep(4.5765456789098765456789098765)

        html = BeautifulSoup(self.driver.page_source, 'html.parser')
        posts = html.select('#m_group_stories_container')[0]
        self.close()
        results = []

        for post in posts.find_all('article', {'class': '_55wo _5rgr _5gh8 async_like'}):
            try:
                author = post.find('h3', {'class': '_52jd _52jb _52jh _5qc3 _4vc- _3rc4 _4vc-'}).find('a').text
                date = post.find('div', {'class': '_52jc _5qc4 _78cz _24u0 _36xo'}).find('abbr').text
                description = post.find('div', {'class': '_5rgt _5nk5 _5msi'}).text
                like = post.find('div', {'class': '_rnk _77ke _2eo- _1e6 _4b44'}).find('div', {'class': '_1g06'}).text

                try: comment = post.find('div', {'class': '_rnk _77ke _2eo- _1e6 _4b44'}).find('span', {'class': '_1j-c'}).text
                except: comment = ''
                try: shared = post.find('div', {'class': '_rnk _77ke _2eo- _1e6 _4b44'}).find('span', {'data-sigil': 'comments-token'}).text
                except: shared = ''
                try: url = post.find('div', {'class': '_5rgt _5nk5 _5msi'}).find('a').get('href')
                except: url = None
                
                results.append({
                    'author': author,
                    'date': date,
                    'description': description,
                    'like': get_num(like),
                    'comment': get_num(comment.replace('репостов', '').split()[-1]) if comment else 0,
                    'shared': get_num(shared.split()[-1]) if shared else 0,
                    'url': ('https://m.facebook.com' + url) if url else None
                })
            
            except:
                pass
        
        return results

def author_statistics(data: dict) -> dict:
    list_of_authors = []
    authors_posts = {}

    for post in data:
        list_of_authors.append(post['author'])
    
    for post in data:
        author = post['author']
        if author in list(authors_posts):
            authors_posts[author] += 1
        else:
            authors_posts[author] = 1

    popular =  sorted(authors_posts, key = authors_posts.get, reverse = True)

    return {interest: authors_posts[interest] for interest in popular}

def get_num(data: str) -> int:
        number_zeros = {
            'млн': '000000',
            'тыс.': '000'
        }

        if not any(x in data for x in list(number_zeros)):
            return int(data)

        num, zero = data.split()
        num = float(num.replace(',', '.'))
        zero = int('1' + number_zeros[zero])

        return int(num * zero)

if __name__ == "__main__":
    login = settings['account']['login']
    password = settings['account']['password']

    parser = FacebookParser(show = True)
    parser.login(login, password)
    data = parser.parse(input("Enter group id: ")) # 1643910255830661

    filename = settings['program']['posts_filename']
    workbook = xlsxwriter.Workbook(f"{filename}.xlsx") 
    worksheet = workbook.add_worksheet()

    row, column = 0, 0
    titles = ['Author', 'Date', 'Description', 'Like', 'Comment', 'Shared', 'Url']

    for item in titles: 
        worksheet.write(row, column, item) 
        column += 1

    row += 1

    for item in data:
        worksheet.write(row, 0, item['author']) 
        worksheet.write(row, 1, item['date']) 
        worksheet.write(row, 2, item['description'])
        worksheet.write(row, 3, item['like'])
        worksheet.write(row, 4, item['comment'])
        worksheet.write(row, 5, item['shared'])
        worksheet.write(row, 6, item['url'])  

        row += 1

    workbook.close()

    filename = settings['program']['accounts_filename']
    workbook = xlsxwriter.Workbook(f"{filename}.xlsx") 
    worksheet = workbook.add_worksheet()

    row, column = 0, 0
    titles = ['Author', 'Posts count']

    for item in titles: 
        worksheet.write(row, column, item) 
        column += 1

    row += 1

    data = author_statistics(data)

    for author in list(data):
        worksheet.write(row, 0, author) 
        worksheet.write(row, 1, data[author]) 

        row += 1

    workbook.close()
