#!/usr/bin/env python
# coding: utf-8

# # Profitable App Profiles for the App Store and Google Play Markets
# 
# Our aim in this project is to find mobile app profiles that are profitable for the App Store and Google Play markets. We're working for a company that builds Android and iOS mobile apps, and our job is to enable our team of developers to make data-driven decisions with respect to the kind of apps they build.
# 
# At our company, We only build apps that are free to download and install, and our main source of revenue consists of in-app ads. This means our revenue for any given app is mostly influenced by the number of users who use our app — the more users that see and engage with the ads, the better.
# 
# 
# # Opening and Exploring Data
# 
# As of September 2018, there were approximately 2 million iOS apps available on the App Store, and 2.1 million Android apps on Google Play.
# 
# Collecting data for over four million apps requires a significant amount of time and money, so we'll try to analyze a sample of data instead. To avoid spending resources with collecting new data ourselves, we should first try to see whether we can find any relevant existing data at no cost. Luckily, these are two data sets that seem suitable for our purpose:
# 
# * A data set containing data about approximately 10,000 Android apps from Google Play; the data was collected in August 2018. You can download the data set directly from this [Link](https://www.kaggle.com/lava18/google-play-store-apps)
# * A data set containing data about approximately 7,000 iOS apps from the App Store; the data was collected in July 2017. You can download the data set directly from this [Link](https://www.kaggle.com/ramamet4/app-store-apple-data-set-10k-apps)
# 
# Lets start by opening two data sets and then continue with exploring data:

# In[2]:


from csv import reader

### The Google Play data set ###
opened_file = open("googleplaystore.csv", encoding='utf8')
read_file = reader(opened_file)
google = list(read_file)
google_play_store_header = google[0]
google_play_store = google[1:]

### The App Store data set ###
opened_file = open("AppleStore.csv", encoding='utf8')
from csv import reader
read_file = reader(opened_file)
apple = list(read_file)
apple_store_header = apple[0]
apple_store = apple[1:]


# To make it easier to explore the two data sets, we'll first write a function named explore_data() that we can use repeatedly to explore rows in a more readable way. We'll also add an option for our function to show the number of rows and columns for any data set.

# In[3]:


def explore_data(dataset, start, end, rows_and_columns= False):
    dataset_slice = dataset[start:end]    
    for row in dataset_slice:
        print(row)
        print('\n') # adds a new (empty) line after each row

    if rows_and_columns:
        print('Number of rows:', len(dataset))
        print('Number of columns:', len(dataset[0]))
print(google_play_store_header)
print('\n')
explore_data(google_play_store, 0, 3, True)


# Now let's take a look at the App Store data set.

# In[16]:


print(apple_store_header)
print('\n')
explore_data(apple_store, 0, 3, True)


# We have 7197 Apple apps in this data set, and the columns that seem interesting are: 'track_name', 'currency', 'price', 'rating_count_tot', 'rating_count_ver', and 'prime_genre'. Not all column names are self-explanatory in this case, but details about each column can be found in the data set [documentation](https://www.kaggle.com/ramamet4/app-store-apple-data-set-10k-apps/home).

# # Deleting wrong Data
# 
# The Google Play data set has a dedicated [discussion section](https://www.kaggle.com/lava18/google-play-store-apps), and we can see that [one of the discussions](https://www.kaggle.com/lava18/google-play-store-apps/discussion/66015) outlines an error for row 10472. Let's print this row and compare it against the header and another row that is correct.

# In[4]:


print(google_play_store_header)
print(google_play_store[10472])


# The row 10472 corresponds to the app Life Made WI-Fi Touchscreen Photo Frame, and we can see that the rating is 19. This is clearly off because the maximum rating for a Google Play app is 5 (as mentioned in the discussions section, this problem is caused by a missing value in the 'Category' column). As a consequence, we'll delete this row.

# In[5]:


del google_play_store[10472]


# In[6]:


explore_data(google_play_store, 10471, 10475, True)


# # Removing Duplicate data

# If we explore the Google Play data set long enough, we'll find that some apps have more than one entry. For instance, the application Instagram has four entries:

# In[7]:


unique_data = []
duplicate = []
for rows in google_play_store:
    name = rows[0]
    if name in unique_data:
        duplicate.append(name)
    else:
        unique_data.append(name)
print(len(duplicate))


# We have 1181 duplicate values in google-play-store data. We don't want to count certain apps more than once when we analyze data, so we need to remove the duplicate entries and keep only one entry per app. One thing we could do is remove the duplicate rows randomly, but we could probably find a better way.
# 
# If you examine the rows we printed for the Instagram app, the main difference happens on the fourth position of each row, which corresponds to the number of reviews. The different numbers show the data was collected at different times.

# In[8]:


print(google_play_store_header)
for app in google_play_store:
    name = app[0]
    if name == "Instagram":
        print(app)


# We can use this information to build a criterion for removing the duplicates. The higher the number of reviews, the more recent the data should be. Rather than removing duplicates randomly, we'll only keep the row with the highest number of reviews and remove the other entries for any given app.

# To remove the duplicates, we will:
# 
# * Create a dictionary, where each dictionary key is a unique app name and the corresponding dictionary value is the highest number of reviews of that app.
# * Use the information stored in the dictionary and create a new data set, which will have only one entry per app (and for each app, we'll only select the entry with the highest number of reviews).

# In[9]:


reviews_max = {}
new_google_data = []
for rows in google_play_store:
    name = rows[0]
    reviews = int(rows[3])
    if name not in reviews_max:
        reviews_max[name] = reviews
    elif name in reviews_max and reviews_max[name] < reviews:
        reviews_max[name] = reviews
for rows in google_play_store[1:]:
    name = rows[0]
    reviews = int(rows[3])
    if name in reviews_max and reviews_max[name] == reviews:
        new_google_data.append(rows)
explore_data(new_google_data, 1, 5, False)


# * We start by initializing two empty lists, google_clean and already_added.
# * We loop through the android data set, and for every iteration:
#     * We isolate the name of the app and the number of reviews.
#     * We add the current row (app) to the android_clean list, and the app name (name) to the already_added list if:
#         * The number of reviews of the current app matches the number of reviews of that app as described in the reviews_max dictionary; and
#         * The name of the app is not already in the already_added list. We need to add this supplementary condition to account for those cases where the highest number of reviews of a duplicate app is the same for more than one entry (for example, the Box app has three entries, and the number of reviews is the same). If we just check for reviews_max[name] == n_reviews, we'll still end up with duplicate entries for some apps.

# In[10]:


google_clean = []
already_added = []
for rows in google_play_store:
    name = rows[0]
    reviews = int(rows[3])
    if (reviews_max[name] == reviews) and (name not in already_added):
        google_clean.append(rows)
        already_added.append(name)
explore_data(google_clean, 1, 5, True)


# ## Removing non English App
# 
# Remember we use English for the apps we develop at our company, and we'd like to analyze only the apps that are directed toward an English-speaking audience. However, if we explore the data long enough, we'll find that both data sets have apps with names that suggest they are not directed toward an English-speaking audience.
# 
# We're not interested in keeping these apps, so we'll remove them. One way to go about this is to remove each app with a name containing a symbol that is not commonly used in English text — English text usually includes letters from the English alphabet, numbers composed of digits from 0 to 9, punctuation marks (., !, ?, ;), and other symbols (+, *, /).
# 
# Behind the scenes, each character we use in a string has a corresponding number associated with it. For instance, the corresponding number for character 'a' is 97, character 'A' is 65, and character '爱' is 29,233. We can get the corresponding number of each character using the ord() built-in function.
# 
# The numbers corresponding to the characters we commonly use in an English text are all in the range 0 to 127, according to the ASCII (American Standard Code for Information Interchange) system. Based on this number range, we can build a function that detects whether a character belongs to the set of common English characters or not. If the number is equal to or less than 127, then the character belongs to the set of common English characters.
# 
# If an app name contains a character that is greater than 127, then it probably means that the app has a non-English name. Our app names, however, are stored as strings, so how could we take each individual character of a string and check its corresponding number?
# 
# In Python, strings are indexable and iterable, which means we can use indexing to select an individual character, and we can also iterate on the string using a for loop.
# 
# * We'll write a function that takes in a string and returns False if there's any character in the string that doesn't belong to the set of common English characters, otherwise it returns True.
# 
#     * Inside the function, iterate over the input string. For each iteration check whether the number associated with the character is greater than 127. When a character is greater than 127, the function should immediately return False — the app name is probably non-English since it contains a character that doesn't belong to the set of common English characters.
# 
#     * If the loop finishes running without the return statement being executed, then it means no character had a corresponding number over 127 — the app name is probably English, so the functions should return True.
# 
# * We'll use the function to check whether these app names are detected as English or non-English:
# 
#     * 'Instagram'
#     * '爱奇艺PPS -《欢乐颂2》电视剧热播'
#     * 'Docs To Go™ Free Office Suite'
#     * 'Instachat 😜'
#     
# To minimize the impact of data loss, we'll only remove an app if its name has more than three non-ASCII characters:

# In[11]:


def english_str(st):
    non_ascii = 0
    
    for character in st:
        if ord(character) > 127:
            non_ascii += 1
    
    if non_ascii > 3:
        return False
    else:
        return True
s = 'Instagram'
print(english_str(s))
s = '爱奇艺PPS -《欢乐颂2》电视剧热播'
print(english_str(s))
s = 'Docs To Go™ Free Office Suite'
print(english_str(s))
s = 'Instachat 😜'
print(english_str(s))


# Let's use the new function to filter out non-English apps from both data sets. Loop through each data set. If an app name is identified as English, append the whole row to a separate list.
# 
# Explore the data sets and see how many rows you have remaining for each data set.

# In[12]:


google_eng = []
apple_eng =[]
for rows in google_clean:
    name = rows[0]
    if english_str(name):
        google_eng.append(rows)
        
for rows in apple_store:
    name = rows[1]
    if english_str(name):
        apple_eng.append(rows)
print(google_play_store_header)
explore_data(google_eng, 0, 5, True)
print(apple_store_header)
explore_data(apple_eng, 0, 5, True)


# ## Isolating Free Apps
# 
# As we mentioned in the introduction, we only build apps that are free to download and install, and our main source of revenue consists of in-app ads. Our data sets contain both free and non-free apps, and we'll need to isolate only the free apps for our analysis. Below, we isolate the free apps for both our data sets.

# In[13]:


def free_app(dataset, index):
    free_app = []
    for rows in dataset:
        price = rows[index]
        if (price == '0.0') or (price == '0'):
            free_app.append(rows)
    return free_app
google_free_app = free_app(google_eng, 7)
apple_free_app = free_app(apple_eng, 4)
explore_data(google_free_app, 1, 5, True)
explore_data(apple_free_app, 1, 5, True)  


# # Most Common Apps by Genre
# ## Part 1
# 
# So far, we spent a good amount of time on cleaning data, and:
# 
# 1. Removed inaccurate data
# 2. Removed duplicate app entries
# 3. Removed non-English apps
# 4. Isolated the free apps
# 
# As we mentioned in the introduction, our aim is to determine the kinds of apps that are likely to attract more users because our revenue is highly influenced by the number of people using our apps.
# 
# To minimize risks and overhead, our validation strategy for an app idea is comprised of three steps:
# 
# 1. Build a minimal Android version of the app, and add it to Google Play.
# 2. If the app has a good response from users, we develop it further.
# 3. If the app is profitable after six months, we build an iOS version of the app and add it to the App Store.
# 
# Because our end goal is to add the app on both Google Play and the App Store, we need to find app profiles that are successful on both markets. For instance, a profile that works well for both markets might be a productivity app that makes use of gamification.
# 
# Let's begin the analysis by getting a sense of what are the most common genres for each market. For this, we'll need to build frequency tables for a few columns in our data sets.

# In[17]:


def percent_tb(dataset, index):
    percent_dict = {}
    total = 0
    for row in dataset:
        total += 1
        genre = row[index]
        if genre in percent_dict:
            percent_dict[genre] += 1
        else:
            percent_dict[genre] = 1
    for content in percent_dict:
        proportion = percent_dict[content]/total
        percentage = proportion * 100
        percent_dict[content] = percentage
    return percent_dict
def descending(dataset, index):
    table = percent_tb(dataset, index)
    unsort_tb = []
    for keys in table:
        key_value_tuple = (table[keys],keys)
        unsort_tb.append(key_value_tuple)
    sort_tb = sorted(unsort_tb, reverse = True)
    for entry in sort_tb:
        print(entry[1], ':', entry[0])       
descending(google_free_app, 1)
print('\n')
descending(apple_free_app, -5)


# 
# In Apple Store: We can see that among the free English apps, more than a half (58.16%) are games. Entertainment apps are close to 8%, followed by photo and video apps, which are close to 5%. Only 3.66% of the apps are designed for education, followed by social networking apps which amount for 3.29% of the apps in our data set.
# 
# The general impression is that App Store (at least the part containing free English apps) is dominated by apps that are designed for fun (games, entertainment, photo and video, social networking, sports, music, etc.), while apps with practical purposes (education, shopping, utilities, productivity, lifestyle, etc.) are more rare. However, the fact that fun apps are the most numerous doesn't also imply that they also have the greatest number of users — the demand might not be the same as the offer.
# 
# Let's continue by examining the Genres and Category columns of the Google Play data set (two columns which seem to be related).

# In[20]:


descending(google_free_app, 1) # Category


# On Google Play: there are not that many apps designed for fun, and it seems that a good number of apps are designed for practical purposes (family, tools, business, lifestyle, productivity, etc.). However, if we investigate this further, we can see that the family category (which accounts for almost 19% of the apps) means mostly games for kids.

# In[21]:


descending(google_free_app, -4) # Genre


# The difference between the Genres and the Category columns is not crystal clear, but one thing we can notice is that the Genres column is much more granular (it has more categories). We're only looking for the bigger picture at the moment, so we'll only work with the Category column moving forward.
# 
# Up to this point, we found that the App Store is dominated by apps designed for fun, while Google Play shows a more balanced landscape of both practical and for-fun apps. Now we'd like to get an idea about the kind of apps that have most users.

# # Most Popular Apps by Genre on the App Store

# One way to find out what genres are the most popular (have the most users) is to calculate the average number of installs for each app genre. For the Google Play data set, we can find this information in the Installs column, but for the App Store data set this information is missing. As a workaround, we'll take the total number of user ratings as a proxy, which we can find in the rating_count_tot app.
# 
# Below, we calculate the average number of user ratings per app genre on the App Store:

# In[27]:


prime_genre = percent_tb(apple_free_app, -5)
for genre in prime_genre:
    total = 0
    len_genre = 0
    for row in apple_free_app:
        genre_app = row[-5]
        if genre_app == genre:
            user_rating = float(row[5])
            total += user_rating
            len_genre += 1
    average = total/len_genre
    print(genre, ":", average)


# On average, navigation apps have the highest number of user reviews, but this figure is heavily influenced by Waze and Google Maps, which have close to half a million user reviews together:

# In[28]:


for app in apple_free_app:
    if app[-5] == 'Navigation':
        print(app[1], ':', app[5]) # print name and number of ratings


# The same pattern applies to social networking apps, where the average number is heavily influenced by a few giants like Facebook, Pinterest, Skype, etc. Same applies to music apps, where a few big players like Pandora, Spotify, and Shazam heavily influence the average number.
# 
# Our aim is to find popular genres, but navigation, social networking or music apps might seem more popular than they really are. The average number of ratings seem to be skewed by very few apps which have hundreds of thousands of user ratings, while the other apps may struggle to get past the 10,000 threshold. We could get a better picture by removing these extremely popular apps for each genre and then rework the averages, but we'll leave this level of detail for later.
# 
# Reference apps have 74,942 user ratings on average, but it's actually the Bible and Dictionary.com which skew up the average rating:

# In[29]:


for app in apple_free_app:
    if app[-5] == 'Reference':
        print(app[1], ":", app[5])


# However, this niche seems to show some potential. One thing we could do is take another popular book and turn it into an app where we could add different features besides the raw version of the book. This might include daily quotes from the book, an audio version of the book, quizzes about the book, etc. On top of that, we could also embed a dictionary within the app, so users don't need to exit our app to look up words in an external app.
# 
# This idea seems to fit well with the fact that the App Store is dominated by for-fun apps. This suggests the market might be a bit saturated with for-fun apps, which means a practical app might have more of a chance to stand out among the huge number of apps on the App Store.
# 
# Other genres that seem popular include weather, book, food and drink, or finance. The book genre seem to overlap a bit with the app idea we described above, but the other genres don't seem too interesting to us:
# 
# Weather apps — people generally don't spend too much time in-app, and the chances of making profit from in-app adds are low. Also, getting reliable live weather data may require us to connect our apps to non-free APIs.
# 
# Food and drink — examples here include Starbucks, Dunkin' Donuts, McDonald's, etc. So making a popular food and drink app requires actual cooking and a delivery service, which is outside the scope of our company.
# 
# Finance apps — these apps involve banking, paying bills, money transfer, etc. Building a finance app requires domain knowledge, and we don't want to hire a finance expert just to build an app.

# # Most Popular Apps by Genre on Google Play

# For the Google Play market, we actually have data about the number of installs, so we should be able to get a clearer picture about genre popularity. However, the install numbers don't seem precise enough — we can see that most values are open-ended (100+, 1,000+, 5,000+, etc.):

# In[31]:


descending(google_free_app, 5)


# 
# One problem with this data is that is not precise. For instance, we don't know whether an app with 100,000+ installs has 100,000 installs, 200,000, or 350,000. However, we don't need very precise data for our purposes — we only want to get an idea which app genres attract the most users, and we don't need perfect precision with respect to the number of users.
# 
# We're going to leave the numbers as they are, which means that we'll consider that an app with 100,000+ installs has 100,000 installs, and an app with 1,000,000+ installs has 1,000,000 installs, and so on.
# 
# To perform computations, however, we'll need to convert each install number to float — this means that we need to remove the commas and the plus characters, otherwise the conversion will fail and raise an error. We'll do this directly in the loop below, where we also compute the average number of installs for each genre (category).

# In[34]:


g_category = percent_tb(google_free_app, 1)
for category in g_category:
    total = 0
    len_category = 0
    for row in google_free_app:
        category_app = row[1]
        if category_app == category:
            n_installs = row[5]
            s_ch = ['+',',']
            for ch in s_ch:
                n_installs = n_installs.replace(ch, '')
            total += float(n_installs)
            len_category += 1
    average = total/len_category
    print(category, ":", average)


# On average, communication apps have the most installs: 38,456,119. This number is heavily skewed up by a few apps that have over one billion installs (WhatsApp, Facebook Messenger, Skype, Google Chrome, Gmail, and Hangouts), and a few others with over 100 and 500 million installs:

# In[35]:


for app in google_free_app:
    if app[1] == 'COMMUNICATION' and (app[5] == '1,000,000,000+'
                                      or app[5] == '500,000,000+'
                                      or app[5] == '100,000,000+'):
        print(app[0], ':', app[5])


# If we removed all the communication apps that have over 100 million installs, the average would be reduced roughly ten times:

# In[43]:


under_100m = []
for app in google_free_app:
    n_install = app[5]
    n_install = n_install.replace('+','')
    n_install = n_install.replace(',','')
    if (app[1] == 'COMMUNICATION') and (float(n_installs) < 100000000):
        under_100m.append(float(n_install))
sum(under_100m)/len(under_100m)


# We see the same pattern for the video players category, which is the runner-up with 24,727,872 installs. The market is dominated by apps like Youtube, Google Play Movies & TV, or MX Player. The pattern is repeated for social apps (where we have giants like Facebook, Instagram, Google+, etc.), photography apps (Google Photos and other popular photo editors), or productivity apps (Microsoft Word, Dropbox, Google Calendar, Evernote, etc.).
# 
# Again, the main concern is that these app genres might seem more popular than they really are. Moreover, these niches seem to be dominated by a few giants who are hard to compete against.
# 
# The game genre seems pretty popular, but previously we found out this part of the market seems a bit saturated, so we'd like to come up with a different app recommendation if possible.
# 
# The books and reference genre looks fairly popular as well, with an average number of installs of 8,767,811. It's interesting to explore this in more depth, since we found this genre has some potential to work well on the App Store, and our aim is to recommend an app genre that shows potential for being profitable on both the App Store and Google Play.
# 
# Let's take a look at some of the apps from this genre and their number of installs:

# In[44]:


for app in google_free_app:
    if app[1] == 'BOOKS_AND_REFERENCE':
        print(app[0], ':', app[5])


# The book and reference genre includes a variety of apps: software for processing and reading ebooks, various collections of libraries, dictionaries, tutorials on programming or languages, etc. It seems there's still a small number of extremely popular apps that skew the average:

# In[45]:


for app in google_free_app:
    if app[1] == 'BOOKS_AND_REFERENCE' and (app[5] == '1,000,000,000+'
                                            or app[5] == '500,000,000+'
                                            or app[5] == '100,000,000+'):
        print(app[0], ':', app[5])


# However, it looks like there are only a few very popular apps, so this market still shows potential. Let's try to get some app ideas based on the kind of apps that are somewhere in the middle in terms of popularity (between 1,000,000 and 100,000,000 downloads):

# In[46]:


for app in google_free_app:
    if app[1] == 'BOOKS_AND_REFERENCE' and (app[5] == '1,000,000+'
                                            or app[5] == '5,000,000+'
                                            or app[5] == '10,000,000+'
                                            or app[5] == '50,000,000+'):
        print(app[0], ':', app[5])


# This niche seems to be dominated by software for processing and reading ebooks, as well as various collections of libraries and dictionaries, so it's probably not a good idea to build similar apps since there'll be some significant competition.
# 
# We also notice there are quite a few apps built around the book Quran, which suggests that building an app around a popular book can be profitable. It seems that taking a popular book (perhaps a more recent book) and turning it into an app could be profitable for both the Google Play and the App Store markets.
# 
# However, it looks like the market is already full of libraries, so we need to add some special features besides the raw version of the book. This might include daily quotes from the book, an audio version of the book, quizzes on the book, a forum where people can discuss the book, etc.

# # Conclusions
# 
# In this project, we analyzed data about the App Store and Google Play mobile apps with the goal of recommending an app profile that can be profitable for both markets.
# 
# We concluded that taking a popular book (perhaps a more recent book) and turning it into an app could be profitable for both the Google Play and the App Store markets. The markets are already full of libraries, so we need to add some special features besides the raw version of the book. This might include daily quotes from the book, an audio version of the book, quizzes on the book, a forum where people can discuss the book, etc.

# In[ ]:




