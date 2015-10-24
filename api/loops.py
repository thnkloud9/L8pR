from flask import current_app as app
import urllib.request
from bs4 import BeautifulSoup
import feedparser


class Loop(object):
    resource = {
        'auth_field': 'user_id',
        'unique_to_user': True,
        'resource_methods': ['GET', 'POST', 'DELETE'],
        'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
        'public_methods': ['GET'],
        'schema': {
            'shows': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'shows',
                        'field': '_id',
                        'embeddable': True
                    }
                }
            },
            'strip_messages': {
                'type': 'list'
            }
        }
    }

    def get_tweets(query):
        from TwitterSearch import TwitterSearch, TwitterSearchOrder
        import itertools
        tso = TwitterSearchOrder()
        tso.set_keywords(query.get('query', '').split(' '))
        # tso.set_language('en')
        tso.set_include_entities(False)
        ts = TwitterSearch(
            consumer_key=app.config.get('TWITTER_CONSUMER_KEY'),
            consumer_secret=app.config.get('TWITTER_CONSUMER_SECRET'),
            access_token=app.config.get('TWITTER_ACCESS_TOKEN'),
            access_token_secret=app.config.get('TWITTER_ACCESS_TOKEN_SECRET')
        )
        return list(itertools.islice(ts.search_tweets_iterable(tso), 0, int(query.get('count', 5))))

    def get_rss(query):
        if 'rss' in query.get('query') or 'atom' in query.get('query'):
            link = query.get('query')
        else:
            page = urllib.request.urlopen(query.get('query'))
            soup = BeautifulSoup(page, 'html.parser')
            link = soup.find('link', type='application/rss+xml').get('href')
        feed = feedparser.parse(link)
        return {
            'link': feed['feed']['link'],
            'title': feed['feed']['title'],
            'subtitle': feed['feed']['subtitle'],
            'items': feed['items'][:int(query.get('count', 5))]
        }

    def retrieve_content(loop):
        queries = loop.get('strip_messages', [])
        sources = {
            'rss': Loop.get_rss,
            'twitter': Loop.get_tweets
        }
        for query in queries:
            if 'results' not in query or len(query['results']) < 1:
                query['results'] = sources[query['type']](query)
        app.data.driver.db['loops'].update({'_id': loop['_id']},
                                           {'$set': {'strip_messages': queries}})

    def on_updated(updated, original):
        if 'strip_messages' in updated:
            loop = original.copy()
            loop.update(updated)
            Loop.retrieve_content(loop)

if __name__ == '__main__':
    query = dict(query='http://www.hejorama.com',
                 count=5)
    rss = Loop.get_rss(query)
    assert(len(rss['items']) == 5)
    assert(rss['title'])
    assert(rss['link'])
    print(rss)
    # from app import get_app
    # with get_app().app_context():
    #     query = dict(query='#yo',
    #                  count=5)
    #     rss = Loop.get_tweets(query)
    #     print(rss)
