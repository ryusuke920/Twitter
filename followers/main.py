import tweepy 
import pandas as pd
import TwitterAPIKey
from wordcloud import WordCloud
import MeCab

class GetAccountInfomation:
    """相互フォロワーをCSVに格納する"""
    def __init__(self, user: str) -> None:
        self.user = '@' + user
        self.consumer_key = TwitterAPIKey.API_KEY 
        self.consumer_secret = TwitterAPIKey.API_SECRET
        self.access_token = TwitterAPIKey.ACCESS_TOKEN 
        self.access_token_secret = TwitterAPIKey.ACCESS_SECRET
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

    def get_follow_ids(self) -> list:
        "フォローしているIDを取得"
        return [follow_id for follow_id in tweepy.Cursor(self.api.friends_ids, id = self.user, cursor = -1).items()]


    def get_follower_ids(self) -> list:
        "フォロワーのIDを取得"
        return [follower_id for follower_id in tweepy.Cursor(self.api.followers_ids, id = self.user, cursor = -1).items()]


    def get_mutual_ids(self) -> list:
        "相互フォロワーIDを取得"
        mutual_ids = []
        follower_ids, follow_ids = self.get_follower_ids(), self.get_follow_ids()
        for follow_id in follow_ids:
            for follower_id in follower_ids:
                if follow_id == follower_id:
                    mutual_ids.append(follow_id)
        return mutual_ids


    def get_account_name_and_ids(self) -> list:
        "アカウント名とIDの取得"
        mutual_ids = self.get_mutual_ids()
        follower_name_list, follower_id_list = [], []
        for i in range(0, len(mutual_ids), 100):
            for user in self.api.lookup_users(user_ids=mutual_ids[i : i + 100]):
                follower_name_list.append(user.name)
                follower_id_list.append(user.screen_name)
        return follower_name_list, follower_id_list


    def to_csv(self) -> None:
        "csvとして保存"
        follower_name, follower_id = self.get_account_name_and_ids()
        df = pd.DataFrame(data={"followers": follower_name, "id": follower_id})
        df.to_csv(f"./output/{self.user}_mutual_followers.csv", index=False)

    def get_tweet(self, n: int):
        "タイムラインのツイートを取得"
        result = self.api.home_timeline(count=n)
        tweet_texts = []
        for tweet in result:
            #self.show_console(tweet)
            tweet_texts.append(tweet.text)

        with open(f"./output/tweet_texts.txt", 'w') as f:
            for text in tweet_texts:
                f.write(f"{str(text)}\n")
    
    def show_console(self, tweet) -> None:
        "コンソールに表示"
        print('=' * 100)
        print('ツイートID : ', tweet.id)
        print('ツイート時間 : ', tweet.created_at)
        print('ツイート文 : ', tweet.text)
        print('ユーザー名 : ', tweet.user.name)
        print('ユーザーID : ', tweet.user.screen_name)
        print('フォロー数 : ', tweet.user.friends_count)
        print('フォロワー数 : ', tweet.user.followers_count)
        print('bio : ', tweet.user.description)
    
    def create_wordcloud_ja(self) -> None:
        "wordcloudの作成"

        with open("./output/tweet_texts.txt", 'r') as f:
            text = f.read()
 
        tagger = MeCab.Tagger() 
        tagger.parse('') 
        node = tagger.parseToNode(text)

        word_list = []
        stop_words = ['もの', 'こと', 'とき', 'そう', 'たち', 'これ', 'よう', 'これら', 'それ', 'すべて', 'https', 'http', 't.co', 't-co', 'CO', 'RT', 'さん']
        while node:
            word_type = node.feature.split(',')[0]
            word_surf = node.surface.split(',')[0]
            if word_type == '名詞' and word_surf not in stop_words and len(node.surface) != 1:
                word_list.append(node.surface)
            node = node.next

        word_chain = ' '.join(word_list)
        wordcloud = WordCloud(background_color="white",
                            font_path="./font/Corporate-Mincho-ver2.ttf",
                            width=900,
                            height=500,
                            #mask = msk,
                            contour_width=1,
                            contour_color="black",
                            stopwords=set(stop_words)).generate(word_chain)

        wordcloud.to_file(f"./output/timeline.png")

info = GetAccountInfomation("ryusuke__h")
info.to_csv()
info.get_tweet(10000)
info.create_wordcloud_ja()