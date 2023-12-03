import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
import random
from App.main import create_app
from App.database import db, create_db
from App.models import *
from App.controllers import *


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''

#run tests with "pytest App/tests/test_app.py" command in shell

class UserUnitTests(unittest.TestCase):

    ''' Admin model methods'''

    def test_new_admin (self):
        newAdmin = Admin("Bob", "Boblast",  "bobpass")
        assert newAdmin.firstname == "Bob" and newAdmin.lastname == "Boblast"
    
    def test_adminJSON (self):
        admin = Admin("Bob", "Boblast", "bobpass")
        admin_json = admin.to_json()
        self.assertDictEqual(admin_json, {
            "id": "A1",
            "firstname" : "Bob",
            "lastname" : "Boblast"
        })

    def test_admin_hashed_password (self):
        password = "bobpass"
        #hashed = generate_password_hash(password, method='sha256')
        admin = Admin("Bob", "Boblast",  password)
        admin.set_password(password)
        assert admin.password != password

    def test_admin_check_password (self):
        password = "bobpass"
        admin = Admin("Bob", "Boblast", password)
        assert admin.check_password(password)


    ''' Staff model methods '''

    def test_new_staff (self):
        newStaff = Staff( "0152", "Bob", "Charles", "bobpass", "bob.charles@staff.com")
        assert newStaff.firstname == "Bob" and newStaff.lastname == "Charles" and newStaff.id == "0152" and newStaff.email == "bob.charles@staff.com"

    def test_staffJSON (self):
        staff = Staff( "0152", "Bob", "Charles", "bobpass", "bob.charles@staff.com")
        staff_json = staff.to_json()
        self.assertDictEqual(staff_json, { 
            "id": "0152",
            "firstname" : "Bob",
            "lastname" : "Charles",
            "email" : "bob.charles@staff.com"
        })

    def test_staff_hashed_password (self):
        password = "bobpass"
        #hashed = generate_password_hash(password, method='sha256')
        staff = Staff( "0152", "Bob", "Charles", password, "bob.charles@staff.com")
        staff.set_password(password)
        assert staff.password != password

    def test_staff_check_password (self):
        password = "bobpass"
        staff = Staff( "0152", "Bob", "Charles", password, "bob.charles@staff.com")
        assert staff.check_password(password)


    ''' Student model methods '''

    def test_new_student (self):
        newStudent = Student( "0021", "Nick", "Dell", "786-444-4343", "Full-Time", "2")
        assert newStudent.id == "0021" and newStudent.firstname == "Nick" and newStudent.lastname == "Dell" and newStudent.contact == "786-444-4343" and newStudent.studentType == "Full-Time" and newStudent.yearOfStudy == "2"
    
    def test_studentJSON (self):
        student = Student( "0041", "Nick", "Dell", "786-444-4343", "Full-Time", "2")
        student_json = student.to_json()
        self.assertDictEqual(student_json, {
            "id": "0041",
            "firstname" : "Nick",
            "lastname" : "Dell",
            "contact" : "786-444-4343",
            "studentType" : "Full-Time",
            "yearOfStudy" : "2",
            "karmaScore" : None,
            "karmaRank" : None
        })

    ''' Karma model methods '''

    def test_new_karma (self):
        newKarma = Karma(10, 4)
        assert newKarma.score == 10 and newKarma.rank == 4
    
    def test_karmaJSON (self):
        karma = Karma(10, 4)
        karma_json = karma.to_json()
        self.assertDictEqual(karma_json, {
            "karmaID" : None,
            "score" : 10,
            "rank" : 4,
            "studentID" : None
        })

    ''' Review model methods ''' 

    def test_new_review (self):
        student = Student("0021", "Nick", "Dell", "786-444-4343", "Full-Time", "2")
        staff = Staff( "0152", "Bob", "Charles", "bobpass", "bob.charles@staff.com")
        newReview = Review(staff, student, True, "test review")
        assert newReview.studentID == "0021" and newReview.isPositive == True and newReview.comment == "test review"

    def test_reviewJSON (self):
        staff = Staff("0152", "Bob", "Charles", "bobpass", "bob.charles@staff.com")
        student = Student("0021", "Nick", "Dell", "786-444-4343", "Full-Time", "2")
        review = Review(staff, student, True, "test review")
        review_json = review.to_json()
        self.assertDictEqual(review_json, {
            "id" : None,
            "reviewerID" : "0152",
            "reviewer" : "Bob Charles",
            "studentID" : "0021",
            "created" : review.created.strftime("%d-%m-%Y %H:%M"),
            "comment" : "test review",
            "isPositive" : True,
            "upvotes" : 0,
            "downvotes" : 0
        }) 

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


class UsersIntegrationTests(unittest.TestCase):
    
    def test_authenticate_admin(self): 
        admin = create_admin("bob", "boblast", "bobpass")
        token = jwt_authenticate_admin(admin.id, "bobpass")
        assert token is not None

    def test_authenticatne_staff(self): 
        admin = get_admin("A1")
        staff = create_staff(admin, "342", "Bob", "Charles", "bobpass", "bob.charles@staff.com")
        token = jwt_authenticate_staff(staff.id, "bobpass")
        assert token is not None 

    def test_create_admin(self):
        newAdmin = create_admin("bob", "boblast", "bobpass")
        assert newAdmin.firstname == "bob"
        assert newAdmin.lastname == "boblast"
        assert newAdmin.check_password("bobpass") 

    def test_create_student(self):
        admin = get_admin("A1")
        newStudent = create_student(admin, "813", "Joe", "Dune", "0000-653-4343", "Full-Time", "2")
        assert newStudent.id == "813" 
        assert newStudent.firstname == "Joe" 
        assert newStudent.lastname == "Dune" 
        assert newStudent.contact == "0000-653-4343" 
        assert newStudent.studentType == "Full-Time" 
        assert newStudent.yearOfStudy == 2
        assert newStudent.karmaID == 2

    def test_create_staff(self):
        admin = get_admin("A1")
        newStaff = create_staff(admin, "0021", "Bob", "Charles", "bobpass", "bob.charles@staff.com")
        assert newStaff.id == "0021"
        assert newStaff.firstname == "Bob" 
        assert newStaff.lastname == "Charles" 
        assert newStaff.check_password("bobpass") 
        assert newStaff.email == "bob.charles@staff.com" 


    def test_search_students(self):
        staff = get_staff(342)
        assert searchStudents(staff, "Joe") is not None
    
    def test_update_student(self): 
        student = get_student("813") 
        admin = get_admin("A1")
        oldFirstname = student.firstname
        oldLastname = student.lastname 
        oldContact = student.contact 
        oldStudentType = student.studentType
        oldYearOfStudy = student.yearOfStudy
        update_student(admin, student, "Joey", "Dome", "0000-123-4567", "Part-Time", "5")
        assert student.firstname != oldFirstname and student.firstname == "Joey"
        assert student.lastname != oldLastname and student.lastname == "Dome"
        assert student.contact != oldContact and student.contact == "0000-123-4567"
        assert student.studentType != oldStudentType and student.studentType == "Part-Time"
        assert student.yearOfStudy != oldYearOfStudy and student.yearOfStudy == 5

    def test_create_review(self): 
        admin = create_admin("rev", "revlast", "revpass")
        staff = create_staff(admin, "Jon", "Den", "password", "546", "john@example.com")
        student = create_student(admin, "0031", "Jim", "Lee", "jim@school.com", "Full-time", "1")
        review = create_review(staff.id, student.id, True, "This is a great review")
        assert admin and staff and student
        assert review.reviewerID == staff.id
        assert review.studentID == student.id 
        assert review.isPositive == True 
        assert review.comment == "This is a great review"

    def test_get_reviews_for_student(self): 
        admin = create_admin("Red", "redlast", "redpass")
        staff = create_staff(admin, "Xem", "Zenm", "password", "111", "zenm@example.com")
        student = create_student(admin, "222", "Demn", "Sam", "demn@school.com", "Evening", 2)
        assert admin and staff and student
        assert create_review(staff.id, student.id, True, "What a good student")
        assert create_review(staff.id,  student.id, True, "He answers all my questions in class")
        reviews = get_reviews_for_student(student.id)
        for review in reviews: 
            assert review.studentID == student.id 

    def test_upvote(self):
        admin = create_admin("White", "whitelast", "whitepass")
        staff1 = create_staff(admin, "5555", "Geo", "Twin1", "password", "twin1@example.com")
        staff2 = create_staff(admin, "4444", "Geo", "Twin2", "password", "twin2@example.com")
        student = create_student(admin, "9999", "Kil", "Me", "void@school.com", "Full-Time", "4")
        review = create_review(staff1.id, student.id, True, "Do i even need to review this student")
        assert admin and staff1 and staff2 and student and review
        old_upVotes = review.upvotes
        old_downvotes = review.downvotes
        assert old_upVotes + 1 == upvoteReview(review, staff2) 
        assert old_downvotes == review.downvotes

    def test_downvote(self):
        admin = create_admin("Black", "blacklast", "blackpass")
        staff1 = create_staff(admin, "6666", "Geo", "Twin3", "password", "twin3@example.com")
        staff2 = create_staff(admin, "7777", "Geo", "Twin4", "password", "twin4@example.com")
        student = create_student(admin, "9998", "Still", "Here", "null@school.com", "Full-Time", "5")
        review = create_review(staff1.id, student.id, False, "Do i even need to review this horrible thing called a student")
        assert admin and staff1 and staff2 and student and review
        old_upVotes = review.upvotes
        old_downvotes = review.downvotes
        assert old_upVotes == review.upvotes
        assert old_downvotes + 1 == downvoteReview(review, staff2) 

    def test_karma(self):
        admin = create_admin("Loom", "Loomlast", "loompass")
        staff1 = create_staff(admin, "882", "Geo", "Twin8", "password", "twin3@example.com")
        staff2 = create_staff(admin, "991", "Geo", "Twin9", "password", "twin4@example.com")
        student = create_student(admin, "787", "Still", "Herehere", "null@school.com", "Full-Time", "5")
        review = create_review(staff1.id, student.id, True, "Good student")
        old_upVotes = review.upvotes
        old_downvotes = review.downvotes
        upvoteReview(review, staff2)
        karma = get_karma(student.karmaID)
        assert karma.score == 1
        assert karma.rank != 99