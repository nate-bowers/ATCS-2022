from models import *
from database import init_db, db_session
from datetime import datetime

class Twitter:
    def __init__(self):
        #currentuser is the user object that is logged in
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
        #keep asking for account data until valid data is entered
        while(not register):
            usern = input("What will your Twitter handle be?\n")
            p1 = input("Enter a password:\n")
            p2 = input("Re-enter password:\n")
            #if passwords match and username is not taken, create new user object
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
        #continuously ask for login creditials until valid ones are given
        #once valid creditals are given, set currentuser to the current user
        while logged == False:
            user = input("Username: ")
            pw = input("Password: ")
            if db_session.query(User).where((User.username == user) & (User.password == pw)).first() == None:
                print("Incorrect username or password. Try again.\n")
            else:
                #continue because account exists
                self.currentuser = db_session.query(User).where((User.username == user) & (User.password == pw)).first()
                return
    
    def logout(self):
        #set currentuser to none which allows no changes to someones account
        print("You have been logged out " + str(self.currentuser))
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
        elif (choice == 2):
            self.register_user()
        else:
            self.end()

    def follow(self):
        follow = input("Who would you like to follow?\n")
        #check if they are already following the user
        for a in self.currentuser.following:
            if( follow == a.username):
                print("You already follow " + follow)
                return
        #check if user exists
        #if they do, add them to current users following list
        #if they don't, tell user that they don't exist
        all_users = db_session.query(User).all()
        for a in all_users:
            if a.username == follow:
                self.currentuser.following.append(db_session.query(User).where(User.username == follow).first())
                db_session.commit()
                print("You now follow " + follow)
                return
        print("That user does not exist.")    

    def unfollow(self):
        unfollow = input("Who would you like to unfollow?\n")
        #find user in the list of following and remove them
        #if they are not found, then the user must not follow them
        for a in self.currentuser.following:
            if(unfollow == a.username):
                self.currentuser.following.remove(db_session.query(User).where(User.username == unfollow).first())
                db_session.commit()
                print("You no longer follow " + unfollow)
                return
        
        print("You dont follow " + unfollow)

    def tweet(self):
        #obtain tweet message and raw tags
        tweet = input("Enter your tweet: ")
        tag_str = input("Enter your tags separated by spaces: ")
        fake_tag_list = tag_str.split()
        tag_list = []
        for tag in fake_tag_list:
            tag_list.append(tag[1:])
        date = datetime.now()
        #create and add new tweet to database
        newtweet = Tweet(content = tweet, username = self.currentuser.username, timestamp = date)
        db_session.add(newtweet)
        db_session.commit()
        temp_tag = None
        temp_twag = None
        for i in range(len(tag_list)):
            #if tag already doesn't exist, create tag and add it to database
            if db_session.query(Tag).where(Tag.content == tag_list[i]).count() == 0:
                temp_tag = Tag(content = tag_list[i])
                db_session.add(temp_tag)
                newtweet.tags.append(temp_tag)
            #if tag exists, just add tag to the new tweets list of tags
            else:
                temp_tag = db_session.query(Tag).where(Tag.content == tag_list[i]).first()
                temp_tweet = db_session.query(Tweet).where(Tweet.timestamp == date).first()
                temp_tag.tweets.append(temp_tweet)           
        db_session.commit()

    def view_my_tweets(self):
        #get and print list of currentusers tweets
        self.print_tweets(self.currentuser.tweets)
    
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        #get and print list of 5 most recent tweets by currentusers' followed users
        following_list = []
        #make list of currentusers following usernames
        for user in self.currentuser.following:
            following_list.append(user.username)
        #I could not figure out how to see if the tweets username was in my list of usernames
        #this is my best attempt:
        #feed = db_session.query(Tweet).filter(Tweet.username.rsid.in_(following_list)).limit(5)
        #This is my inefficient work around:
        feed = []
        tweet_list = db_session.query(Tweet).order_by(Tweet.timestamp.desc()).all()
        #go thru all tweets and see if the username is in following_list
        #if it is, add to list until it is 5 long
        for tweet in tweet_list:
            if len(tweet_list) !=5:
                if(tweet.username in following_list):
                    feed.append(tweet)     
        self.print_tweets(feed)    

    def search_by_user(self):
        search_user = input("What user would you like to view?\n")
        #discern if user exists, if they do, get all tweets made by them
        if db_session.query(User).where(User.username == search_user).count() == 0:
            print("There is no user by that name")
        else:
            feed = db_session.query(Tweet).where(Tweet.username == search_user).all()
            self.print_tweets(feed)

    def search_by_tag(self):
        #take in tag that user is searching for
        temp_tag = input("What tag would you like to search for?\n")
        search_tag = temp_tag[1:]
        #check if tag exists
        if db_session.query(Tag).where(Tag.content == search_tag).count() == 0:
            print("There are no tweets with this tag")
        else:
            feed = []
            #iterate thru all tags in all tweets to see if they match. If they do, add to feed
            all_tweets = db_session.query(Tweet).order_by(Tweet.timestamp.desc()).all()
            for tweet in all_tweets:
                for tag in tweet.tags:
                    if(search_tag == tag.content):
                        feed.append(tweet)
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
# login
# log out
# view my tweets
# follow
# unfollow
# tweet 
# view feed
# print tags
#search by user
#search by tag

#Not working:
