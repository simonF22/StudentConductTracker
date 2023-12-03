from App.database import db
from App.models import Review, Karma


def get_review(reviewID):
    return Review.query.filter_by(id=reviewID).first()

def get_reviews():
    return db.session.query(Review).all()

def get_reviews_for_student(studentID):
    return db.session.query(Review).filter_by(studentID=studentID).all()
    
def get_karma(karmaID):
    return Karma.query.get(karmaID)

def upvoteReview(review, staff):
    upvotes = review.upvoteReview(staff)
    if upvotes:
        return upvotes
    return None

def downvoteReview(review, staff):
    downvotes = review.downvoteReview(staff)
    if downvotes:
        return downvotes
    return None