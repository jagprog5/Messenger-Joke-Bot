import fbchat
import json
import os
import requests

def main():
    config_file = open(get_same_dir_path("config.txt"), "r")
    account_info = json.load(config_file)
    account_email = account_info["email"]
    account_password = account_info["password"]

    client = JokeBot(account_email, account_password)
    client.listen()

class JokeBot(fbchat.Client):
    def onPendingMessage(self, thread_id, thread_type, metadata, msg):
        # called when there is a new message, with no prior thread or friend request
        thread_list = self.fetchThreadList(limit=1, thread_location=fbchat.ThreadLocation.PENDING)
        for thread in thread_list:
            id = thread.uid
            self.sendJoke(id)

    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type, ts, metadata, msg):
        if author_id != self.uid:   # ignore messages by itself (otherwise infinite loops will be caused)
            self.sendJoke(author_id)

    def onFriendRequest(self, from_id, msg):
        self.friendConnect(from_id) # accept the request
        self.sendJoke(from_id)
    
    def sendJoke(self, id):
        joke = None

        response = requests.get("https://icanhazdadjoke.com/", headers={'Accept': 'application/json'})

        if response.status_code is 200: 
            joke = response.json()["joke"]
        else:
            user_info = self.fetchUserInfo(id)
            user = user_info[str(id)]
            name = user.first_name
            joke = "Sorry " + name + ", I can't think of a joke right now."

        the_message = fbchat.Message(text=joke)
        self.send(the_message, thread_id=id, thread_type=fbchat.ThreadType.USER)

def get_same_dir_path(file):
    dir = os.path.dirname(os.path.realpath(__file__))
    return dir + "\\" + file

if __name__ == "__main__":
    main()
