import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

request = requests.get('https://api.github.com/search/repositories?q=stars:>500&sort=stars&order=desc')



def get_next_link(link_header: str) -> str:
    """ returns the link of the next page """
    logging.info(f'header: {link_header}')
    for url in link_header.split(', '):
        logger.info(f'processing url: {url}')
        if url.find("rel=\"next\"") != -1:
            print('foooound it')
            next_url = url
            break
    next_url = next_url.split(';')[0][1:-1]
    logging.info(next_url)
    return next_url

wanted = []
while get_next_link(request.headers['link']) != -1:
    results = request.json()
    for repo in results['items']:
        if 'Gherkin' in requests.get(results['items'][0]['languages_url']).json().keys():
            logger.info(f'found repo: {repo.full_name}')
            wanted.append(repo)

    logger.info(wanted)
    request = requests.get(get_next_link(request.headers['link']))


print(f'End of request list: {request.headers["link"]}')

