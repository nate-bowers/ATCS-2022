from models import *
from database import init_db, db_session
from datetime import datetime

class Twitter:
    def __init__(self):
        self.currentuser = None
    """
    The menu to print once a user has logged in
    """
    def print_menu(self):
        print("\nPlease select a menu option:")
        print("1. View Feed")
        print("2. View My Tweets")
        print("3. Search by Tag")
        print("4. Search by User")
        print("5. Tweet")
        print("6. Follow")
        print("7. Unfollow")
        print("0. Logout")
    
    """
    Prints the provided list of tweets.
    """
    def print_tweets(self, tweets):
        for tweet in tweets:
            print("==============================")
            print(tweet)
        print("==============================")

    """
    Should be run at the end of the program
    """
    def end(self):
        print("Thanks for visiting!")
        db_session.remove()
    
    """
    Registers a new user. The user
    is guaranteed to be logged in after this function.
    """
    def register_user(self):
        register = False
        while(not register):
            usern = input("What will your Twitter handle be?\n")
            p1 = input("Enter a password:\n")
            p2 = input("Re-enter password:\n")

            if db_session.query(User).where(User.username == usern).count() == 0:
                if(p1 == p2):
                    newuser = User(username = usern, password = p1, following = [], followers = [], tweets = [])
                    db_session.add(newuser)
                    db_session.commit()
                    register = True
                    print("Welcome to ATCS twitter!")
                    self.currentuser = newuser
                else:
                    print("Passwords don't match. Try again\n")
            else:
                print("Usernames already taken. Try again\n")


    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        logged = False
        while logged == False:
            user = input("Username: ")
            pw = input("Password: ")
            if db_session.query(User).where(User.username == user and User.password == pw).first() == None:
                print("Incorrect username or password. Try again.\n")
            else:
                #continue because account exists
                self.currentuser = db_session.query(User).where(User.username == user and User.password == pw).first()
                
                return


    
    def logout(self):
        print("You have been logged out " + self.currentuser)
        self.currentuser = None
        return

    """
    Allows the user to login,  
    register, or exit.
    """
    def startup(self):
        print("Welcome to ATCS twitter")
        choice = int(input("Please select a menu option:\n1. Login\n2. Register User\n3. Exit\n"))
        if (choice == 1):
            self.login()
        if (choice == 2):
            self.register_user()
        else:
            self.end()

    def follow(self):
        follow = input("Who would you like to follow?\n")
        #loop through list users that this user is following
        for a in self.currentuser.following:
            if( follow == a.username):
                print("You already follow " + follow)
                return
       
        self.currentuser.following.add(db_session.query(User).where(User.username == follow))
        print("You now follow " + follow)

    def unfollow(self):
        unfollow = input("Who would you like to unfollow?\n")
        for a in self.currentuser.following:
            if(unfollow == a.username):
                self.currentuser.following.remove(db_session.query(User).where(User.username == unfollow))
                print("You no longer follow " + unfollow)
                return
        
        print("You dont follow " + unfollow)

    def tweet(self):
        tweet = input("Enter your tweet: ")
        tag_str = input("Enter your tags separated by spaces: ")
        fake_tag_list = tag_str.split()
        tag_list = []
        for tag in fake_tag_list:
            tag_list.append(tag[1:])
        
        newtweet = Tweet(content = tweet, username = self.currentuser.username, timestamp = datetime.now())
        db_session.add(newtweet)
        temp_tag = None
        temp_twag = None
        for i in range(len(tag_list)):
            temp_tag = Tag(content = tag_list[i])
            db_session.add(temp_tag)
            temp_twag = TweetTag(tweet_id = newtweet.id, tag_id = temp_tag.id)
            db_session.add(temp_twag)
        db_session.commit()

    def view_my_tweets(self):
        #get list of currentusers tweets
        user_tweets = db_session.query(Tweet).where(User.username == self.currentuser.username)
        self.print_tweets(user_tweets)
    
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        print(self.currentuser)
        following_list = []
        for user in self.currentuser.following:
            following_list.append(user.username)


        #following_list = db_session.query(Tweet).where(Tweet.username in  ):
        feed = db_session.query(Tweet).where(Tweet.username in following_list).limit(5)
        self.print_tweets(feed)

    def search_by_user(self):
        search_user = input("What user would you like to view?\n")
        if db_session.query(User).where(User.username == search_user).count() == 0:
            print("There is no user by that name")
        else:
            feed = db_session.query(Tweet).where(Tweet.username in search_user).all()
            self.print_tweets(feed)


    def search_by_tag(self):
        temp_tag = input("What tag would you like to search for?\n")
        search_tag = temp_tag[1:]
        if db_session.query(Tag).where(Tag.content == search_tag).count() == 0:
            print("There are no tweets with this tag")
        else:
            feed = db_session.query(Tweet).where(search_tag in Tweet.tags)
            self.print_tweets(feed)

    """
    Allows the user to select from the 
    ATCS Twitter Menu
    """
    def run(self):
        init_db()

        print("Welcome to ATCS Twitter!")
        self.startup()
        option = 1
        while (option in range(1,8)):
            self.print_menu()
            option = int(input(""))
            if option == 1:
                self.view_feed()
                
            elif option == 2:
                self.view_my_tweets()
                
            elif option == 3:
                self.search_by_tag()
                
            elif option == 4:
                self.search_by_user()
                
            elif option == 5:
                self.tweet()

            elif option == 6:
                self.follow()
                
            elif option == 7:
                self.unfollow()
                
            else:
                self.logout()
        
        self.end()


#Working: 
#  tweet

#Not working:
#print feed
#print my tweets
#search by tag
#search by user
#follow
#unfollow
#logout
#print tags

#I can't access current user from functions??