from App.database import db
from .student import Student
from datetime import datetime
from .karma import Karma

# Define the association table for staff upvotes on reviews
review_staff_upvoters = db.Table(
    'review_staff_upvoters',
    db.Column('reviewID', db.Integer, db.ForeignKey('review.id')),
    db.Column('staffID', db.String(10), db.ForeignKey('staff.id')),
)

review_staff_downvoters = db.Table(
    'review_staff_downvoters',
    db.Column('reviewID', db.Integer, db.ForeignKey('review.id')),
    db.Column('staffID', db.String(10), db.ForeignKey('staff.id')),
)


class Review(db.Model):
  __tablename__ = 'review'
  id = db.Column(db.Integer, primary_key=True)
  reviewerID = db.Column(db.String(10), db.ForeignKey('staff.id'))
  studentID = db.Column(db.String(10), db.ForeignKey('student.id'))
  created = db.Column(db.DateTime, default=datetime.utcnow)
  comment = db.Column(db.String(400), nullable=False)
  isPositive = db.Column(db.Boolean, nullable=False)
  upvotes = db.Column(db.Integer, nullable=False)
  downvotes = db.Column(db.Integer, nullable=False)
  reviewer = db.relationship('Staff', backref=db.backref('reviews_created', lazy='joined'), foreign_keys=[reviewerID])
  staffUpvoters = db.relationship('Staff', secondary=review_staff_upvoters, backref=db.backref('reviews_upvoted', lazy='joined'))  #for staff who have voted on the review
  staffDownvoters = db.relationship('Staff', secondary=review_staff_downvoters, backref=db.backref('reviews_downvoted', lazy='joined'))  #for staff who have voted on the review


  def __init__(self, reviewer, student, isPositive, comment):
    self.reviewerID = reviewer.id
    self.reviewer = reviewer
    self.studentID = student.id
    self.isPositive = isPositive
    self.comment = comment
    self.upvotes = 0
    self.downvotes = 0
    self.created = datetime.now()

  # adds 1 to the upvotes for the review when called
  def upvoteReview(self, staff): 
    if staff in self.staffUpvoters:
      return self.upvotes

    else:
      if staff not in self.staffUpvoters:  
        self.upvotes += 1
        self.staffUpvoters.append(staff)

      if staff in self.staffDownvoters:
        self.downvotes -= 1
        self.staffDownvoters.remove(staff)

      student = Student.query.get(self.studentID)
      self.notify_student(student)

      try:
        db.session.add(self)
        db.session.commit()

        return self.upvotes
      except:
        db.session.rollback()
        return False

    return False

  #adds 1 to the downvotes for the review when called
  def downvoteReview(self, staff): 
    if staff in self.staffDownvoters:
      return self.downvotes
    
    else:
      if staff not in self.staffDownvoters: 
        self.downvotes += 1
        self.staffDownvoters.append(staff)

      if staff in self.staffUpvoters: 
        self.upvotes -= 1
        self.staffUpvoters.remove(staff)
        
      student = Student.query.get(self.studentID)
      self.notify_student(student)

      try:
        db.session.add(self)
        db.session.commit()

        return self.downvotes
      except:
        db.session.rollback()
        return False
    
    return False

  def notify_student(self, student):
    student.updateKarma()
    return

  def to_json(self):
    return {
        "id": self.id,
        "reviewerID" : self.reviewer.id,
        "reviewer": self.reviewer.firstname + " " + self.reviewer.lastname,
        "studentID": self.studentID,
        "created": self.created.strftime("%d-%m-%Y %H:%M"),  #format the date/time
        "comment": self.comment,
        "isPositive": self.isPositive,
        "upvotes": self.upvotes,
        "downvotes": self.downvotes
    }