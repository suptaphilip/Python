'''
Created on Dec 30 2013
@author: Kelly Chan

Python Version: V2.7.3

Course: Python Data Mining
Lesson: Recommendation
Methods: 

'''

import codecs
from math import sqrt

users = {"Angelica": {"Blues Traveler": 3.5, 
                      "Broken Bells": 2.0,
                      "Norah Jones": 4.5, 
                      "Phoenix": 5.0, 
                      "Slightly Stoopid": 1.5,
                      "The Strokes": 2.5, 
                      "Vampire Weekend": 2.0},
         "Bill": {"Blues Traveler": 2.0, 
                  "Broken Bells": 3.5, 
                  "Deadmau5": 4.0,
                  "Phoenix": 2.0, 
                  "Slightly Stoopid": 3.5, 
                  "Vampire Weekend": 3.0},
         "Chan": {"Blues Traveler": 5.0, 
                  "Broken Bells": 1.0, 
                  "Deadmau5": 1.0,
                  "Norah Jones": 3.0, 
                  "Phoenix": 5, 
                  "Slightly Stoopid": 1.0},
         "Dan": {"Blues Traveler": 3.0, 
                 "Broken Bells": 4.0, 
                 "Deadmau5": 4.5,
                 "Phoenix": 3.0, 
                 "Slightly Stoopid": 4.5, 
                 "The Strokes": 4.0,
                 "Vampire Weekend": 2.0},
         "Hailey": {"Broken Bells": 4.0, 
                    "Deadmau5": 1.0, 
                    "Norah Jones": 4.0,
                    "The Strokes": 4.0, 
                    "Vampire Weekend": 1.0},
         "Jordyn": {"Broken Bells": 4.5, 
                    "Deadmau5": 4.0, 
                    "Norah Jones": 5.0,
                    "Phoenix": 5.0, 
                    "Slightly Stoopid": 4.5, 
                    "The Strokes": 4.0,
                    "Vampire Weekend": 4.0},
         "Sam": {"Blues Traveler": 5.0, 
                 "Broken Bells": 2.0, 
                 "Norah Jones": 3.0,
                 "Phoenix": 5.0, 
                 "Slightly Stoopid": 4.0, 
                 "The Strokes": 5.0},
         "Veronica": {"Blues Traveler": 3.0, 
                      "Norah Jones": 5.0, 
                      "Phoenix": 4.0,
                      "Slightly Stoopid": 2.5, 
                      "The Strokes": 3.0} }


users2 = {"Amy": {"Dr. Dog": 4, 
                  "Lady Gaga": 3, 
                  "Phoenix": 4},
          "Ben": {"Dr. Dog": 5, 
                  "Lady Gaga": 2},
          "Clara": {"Lady Gaga": 3.5, 
                    "Phoenix": 4}}

class recommender:
    def __init__(self, data, k=1, metric='pearson', n=5):
        """ initialize recommender
        currently, if data is dictionary the recommender is initialized to it.
        For all other data types of data, no initialization occurs
        k is the k value for k nearest neighbor
        metric is which distance formula to use
        n is the maximum number of recommendations to make"""
        
        self.k = k
        self.n = n
        self.username2id = {}
        self.userid2name = {}
        self.productid2name = {}
        
        # for some reason I want to save the name of the metric
        self.metric = metric
        if self.metric == 'pearson':
            self.fn = self.pearson
        #
        # if data is dictionary set recommender data to it
        #
        if type(data).__name__ == 'dict':
            self.data = data    
    
    
    def convertProductID2name(self, prod_id):
        """Given product id number return product name"""
        if prod_id in self.productid2name:
            return self.productid2name[prod_id]
        else:
            return prod_id    
        
        
    def userRatings(self, uid, n):
        """Return n top ratings for user with id"""
        print ("Ratings for " + self.userid2name[uid])
        ratings = self.data[uid]
        ratings = list(ratings.items())
        ratings = [(self.convertProductID2name(k), v) for (k, v) in ratings]
        # finally sort and return
        ratings.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
        ratings = ratings[:n]
        for rating in ratings:
            print("%s\t%i" % (rating[0], rating[1]))
            
            
    def loadBookDB(self, path=''):
        """loads the BX book dataset. Path is where the BX files are located"""
        self.data = {}
        i = 0
        #
        # First load book ratings into self.data
        #
        f = codecs.open(path + "BX-Book-Ratings.csv", 'r', 'utf8')
        for line in f:
            i += 1
            #separate line into fields
            fields = line.split(';')
            user = fields[0].strip('"')
            book = fields[1].strip('"')
            rating = int(fields[2].strip().strip('"'))
            if user in self.data:
                currentRatings = self.data[user]
            else:
                currentRatings = {}
            currentRatings[book] = rating
            self.data[user] = currentRatings
        f.close()
        
        #
        # Now load books into self.productid2name
        # Books contains isbn, title, and author among other fields
        #
        f = codecs.open(path + "BX-Books.csv", 'r', 'utf8')
        for line in f:
            i += 1
            #separate line into fields
            fields = line.split(';')
            isbn = fields[0].strip('"')
            title = fields[1].strip('"')
            author = fields[2].strip().strip('"')
            title = title + ' by ' + author
            self.productid2name[isbn] = title
        f.close()
        
        #
        # Now load user info into both self.userid2name and self.username2id
        #
        f = codecs.open(path + "BX-Users.csv", 'r', 'utf8')
        for line in f:
            i += 1
            #separate line into fields
            fields = line.split(';')
            userid = fields[0].strip('"')
            location = fields[1].strip('"')            
            if len(fields) > 3:
                age = fields[2].strip().strip('"')
            else:
                age = 'NULL'            
            if age != 'NULL':
                value = location + ' (age: ' + age + ')'
            else:
                value = location
            self.userid2name[userid] = value
            self.username2id[location] = userid
        f.close()
        print(i)
        
    def pearson(self, rating1, rating2):
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        if n == 0:
            return 0
        # now compute denominator
        denominator = sqrt(sum_x2 - pow(sum_x, 2) / n) * sqrt(sum_y2 - pow(sum_y, 2) / n)
        if denominator == 0:
            return 0
        else:
            return (sum_xy - (sum_x * sum_y) / n) / denominator
    
    
    def computeNearestNeighbor(self, username):
        """creates a sorted list of users based on their distance to username"""
        distances = []
        for instance in self.data:
            if instance != username:
                distance = self.fn(self.data[username], self.data[instance])
                distances.append((instance, distance))
        # sort based on distance -- closest first
        distances.sort(key=lambda artistTuple: artistTuple[1], reverse=True)
        return distances
    
    
    def recommend(self, user):
        """Give list of recommendations"""
        recommendations = {}
        # first get list of users ordered by nearness
        nearest = self.computeNearestNeighbor(user)
        #
        # now get the ratings for the user
        #
        userRatings = self.data[user]
        #
        # determine the total distance
        totalDistance = 0.0
        for i in range(self.k):
            totalDistance += nearest[i][1]
        # now iterate through the k nearest neighbors
        # accumulating their ratings
        for i in range(self.k):
            # compute slice of pie
            weight = nearest[i][1] / totalDistance
            # get the name of the person
            name = nearest[i][0]
            # get the ratings for this person
            neighborRatings = self.data[name]
            #
            # now find bands neighbor rated that user didn't
            for artist in neighborRatings:
                if not artist in userRatings:
                    if artist not in recommendations:
                        recommendations[artist] = neighborRatings[artist] * weight
                    else:
                        recommendations[artist] = recommendations[artist] + neighborRatings[artist] * weight
            
            # now make list from dictionary
            recommendations = list(recommendations.items())
            recommendations = [(self.convertProductID2name(k), v) for (k, v) in recommendations]
            # finally sort and return
            recommendations.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
            # Return the first n items
            return recommendations[:self.n]
    
    
    
    def computeDeviations(self):
        #for each person in the data:
        # get their ratings
        for ratings in self.data.values():        
            #for each item & rating in that set of ratings:
            for (item, rating) in ratings.items():
                self.frequencies.setdefault(item, {})
                self.deviations.setdefault(item, {})
            #for each item2 & rating2 in that set of ratings:
            for (item2, rating2) in ratings.items():
                if item != item2:
                    #add the difference between the ratings to our computation
                    self.frequencies[item].setdefault(item2, 0)
                    self.deviations[item].setdefault(item2, 0.0)
                    self.frequencies[item][item2] += 1
                    self.deviations[item][item2] += rating - rating2
            for (item, ratings) in self.deviations.items():
                for item2 in ratings:
                    ratings[item2] /= self.frequencies[item][item2]
       
       
    def slopeOneRecommendations(self, userRatings):
        recommendations = {}
        frequencies = {}
        # for every item and rating in the user's recommendations
        for (userItem, userRating) in userRatings.items():
            #for every item in our dataset that the user didn't rate
            for (diffItem, diffRatings) in self.deviations.items():
                if diffItem not in userRatings and userItem in self.deviations[diffItem]:
                    freq = self.frequencies[diffItem][userItem]
                    recommendations.setdefault(diffItem, 0.0)
                    frequencies.setdefault(diffItem, 0)
                    # add to the running sum representing the numerator of the formula
                    recommendations[diffItem] += (diffRatings[userItem] + userRating) * freq
                    # keep a running sum of the frequency of diffitem
                    frequencies[diffItem] += freq
                    recommendations = [(k, v / frequencies[k])
                                       for (k, v) in recommendations.items()]
        # finally sort and return
        recommendations.sort(key=lambda artistTuple: artistTuple[1], reverse = True)
        return recommendations  

r = recommender(users)
print r.recommend('Jordyn')
print r.recommend('Hailey')

r = recommender(users2)
r.computeDeviations()
print r.deviations

g = users2['Ben']
print r.slopeOneRecommendations(g)