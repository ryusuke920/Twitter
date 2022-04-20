import tweepy 
import pandas as pd
import TwitterAPIKey

class GetAccountInfomation:
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

GetAccountInfomation("ryusuke__h").to_csv()