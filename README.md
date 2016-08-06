# LHBassClassifier
Classifier to determine handedness of electric basses using photos

## Data
Electric bass images have been scraped from the [For Sale: Bass Guitars](https://www.talkbass.com/forums/for-sale-bass-guitars.126/) pages of the Talk Bass Classifieds forum. For this problem, I can artificially increase the number of left handed bass photos by mirroring images of right handed basses. I'll want to do this because left handed basses are so rare. 

##Classifier
Will be a convolutional neural network implemented using Keras with Theano backend. More details to come once data has been scraped.

Since I intend to train on a balanced data set, but left handed basses are so rare, I'll need to feed the model priors (class weights). I intend to estimate these by using sites such as Sweetwater, Rondo, Bass Central, etc. where I can see the fraction of new left handed basses they have for sale.
