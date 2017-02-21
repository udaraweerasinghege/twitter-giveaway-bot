from config import APP_KEY, APP_SECRET, TOKEN_KEY, TOKEN_SECRET
from twython import Twython, TwythonStreamer
import pickle

def get_previously_tweeted():
    with open ('already_tweeted', 'rb') as fp:
        tweet_list = pickle.load(fp)
    return tweet_list

def set_previously_tweeted(tweet_ids_list):
    with open('already_tweeted', 'wb') as fp:
        pickle.dump(tweet_ids_list, fp)
    return

def setup_bot():
    twitter_bot = Twython(app_key=APP_KEY, app_secret=APP_SECRET, oauth_token=TOKEN_KEY, oauth_token_secret=TOKEN_SECRET)
    return twitter_bot


def get_search_statuses(t):
    search = t.search(q='#giveaway',
                  count=200)
    return search['statuses']

def get_favourites(twitter):
    favs = twitter.get_favorites(count=100)
    favs_list = [str(t['id']) for t in favs]
    return favs_list

def build_tweets_map(statuses):
    to_retweet = {}
    for tweet in statuses:
        user = tweet['user']
        if tweet['retweeted'] == False and user['screen_name']!='udara_takes':
            tweet_id = tweet['id_str']
            to_retweet[tweet_id] = {
                'screen_name': user['screen_name'],
                'user_id': user['id_str'],
                'text': tweet['text']
        }
    return to_retweet

def retweet(twitter, tweets_map, should_not_tweet_ids, favourites):
    should_not_tweet_ids_copy = [id for id in should_not_tweet_ids]
    print(len(should_not_tweet_ids_copy))
    num_retweets = 0
    for t_id, t_info in tweets_map.items():
        tweet_id = t_id
        user_id = t_info['user_id']
        # don't retweet if already retweeted
        if t_id not in should_not_tweet_ids_copy and t_id not in favourites:
            try:
                #like tweet
                twitter.create_favorite(id=tweet_id)
                # follow them
                twitter.create_friendship(user_id=user_id)
                #retweet tweet
                twitter.retweet(id=tweet_id)
                # add to list of tweeted ids
                # print('Retweeted {} and followed {}'.format(t_info['text'], t_info['screen_name']))
                should_not_tweet_ids_copy.append(t_id)
                num_retweets += 1
            except Exception as e:
                print(e, 'status:{}'.format(t_info['text']))
                print('Retweeted {} tweets'.format(num_retweets))
                continue

    print('Retweeted {} tweets'.format(num_retweets))
    return should_not_tweet_ids_copy




previously_tweeted = get_previously_tweeted()
twitter = setup_bot()
valid_statuses = get_search_statuses(twitter)
tweets_map = build_tweets_map(valid_statuses)
favourites = get_favourites(twitter)

new_list_of_tweets = retweet(twitter, tweets_map, previously_tweeted, favourites)
set_previously_tweeted(new_list_of_tweets)
print('donezo')






