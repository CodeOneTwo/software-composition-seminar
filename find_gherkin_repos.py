import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

request = requests.get('https://api.github.com/search/repositories?q=stars:>500&sort=stars&order=desc')

wanted = []
while request.headers['link'].split(',')[0].find("rel=\"next\"") is not -1:
    results = request.json()
    for repo in results['items']:
        if 'Gherkin' in requests.get(results['items'][0]['languages_url']).json().keys():
            wanted.append(repo)
    request = requests.get(get_next_link(request.headers['link']))


print(f'End of request list: {request.headers["link"]}')

def get_next_link(link_header: str) -> str:
    """ returns the link of the next page """
    next_url = link_header.split(',')[0].split(';')[1:-1]
    logging.info(next_url)
    return next_url
