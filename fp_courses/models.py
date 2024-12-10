from django.db import models
from datetime import timedelta, datetime, date
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from fp_blog.models import Article, Comment, Action

STATUS = ((0, "Inactive"), (1, "Active"))
CONTENT_TYPE = ((0, "Article"), (1, "Quiz"))

def today_date():
    return date.today()

def today_plus_one_year():
       return date.today() + timedelta(days=365)

def today_plus_10_years():
       return date.today() + timedelta(days=3650)

# Create your models here.
class Course(models.Model):
    disp_seq = models.IntegerField(default=10)
    course_code = models.IntegerField( primary_key=True)
    version = models.CharField(max_length=3)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="courses", db_constraint=False)
    featured_image = CloudinaryField('image', default='placeholder')
    effective_from = models.DateField(auto_now_add=True)
    effective_to = models.DateField(default=today_plus_10_years)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)  # Change to auto_now
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        unique_together = (('course_code', 'version'),)
        ordering = ['disp_seq', 'course_code', 'version']

    def __str__(self):
        return f"{self.course_code} {self.title}"  # Removed print statement

    def is_valid_today(self):
        # You can implement your validation logic here
        pass

class CourseContents(models.Model):
    """ Course is a set of articles delivered in a particular sequence
    fields: course_code, title1, slug, title2, version, author, featured_image, effective_from, effective_to"""
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name="course_contents", db_constraint=False)
    version = models.CharField(max_length = 3)
    seq_num = models.IntegerField(default=10)
    content_type = models.IntegerField(choices=CONTENT_TYPE, default=0) 
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="course_article", db_constraint=False)
    status = models.IntegerField(choices=STATUS, default=0)    
    
    class Meta:
        unique_together = ('course_code', 'version', 'seq_num')
        
        """ returns an overall list """
        ordering = ['course_code', 'version', 'seq_num']

    def __str__(self):
        """ returns course title """
        return f"{self.course_code} {self.version} {self.seq_num}" 
    

    def is_valid(self):
        """ Returns True or False based on CourseContent status """
        valid_today = (self.status)
        return (valid_today)


class Cohort(models.Model):
    """ Cohort refers to a group of users who will be assigned to a common course of learning """
    cohort_code = models.CharField(max_length = 25, primary_key = True)
    title = models.CharField(max_length=200, unique=True)
    subtitle = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="admin_cohorts", db_constraint=False)
    featured_image = CloudinaryField('image', default='placeholder')
    effective_from = models.DateField(default=today_date)
    effective_to = models.DateField(default=today_plus_one_year)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    members = models.ManyToManyField(User, related_name='cohort_user', blank=True)
    
    class Meta:
        """ returns an overall list """
        ordering = ['cohort_code']

    def __str__(self):
        """ returns course title """
        return f"{self.cohort_code}"
    
    def is_valid_today(self):
        """ returns True or False based on effectivedate and status """
        valid_today = (( date.today >= self.effective_from) and (date.today <= date.effective_to) and (self.status))
        return (valid_today)

    def is_a_member(self, user):
        return(user in self.members)


class Quiz(models.Model):
    """ Quiz is a multichoice set of questions related to a particle topic or article
        fields: course_code, title1, slug, title2, version, author, featured_image, effective_from, effective_to"""
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="quiz", db_constraint=False)
    quiz_code = models.IntegerField( primary_key = True)
    question_text = models.CharField(max_length = 200, default='Question text goes here?')
    ans1_text = models.CharField(max_length=200, default="Answer1 goes here")
    ans2_text = models.CharField(max_length=200, default="Answer2 goes here")
    ans3_text = models.CharField(max_length=200, default="Answer3 goes here")
    ans4_text = models.CharField(max_length=200, default="Answer4 goes here")
    correct_ans = models.IntegerField()
    explanation = models.CharField(max_length=300, default="Correct answer is X:  This is because ......")
    updated_on = models.DateField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)   
    
    
    class Meta:
        """ returns an overall list """
        ordering = ['quiz_code',]

    def __str__(self):
        """ returns quiz question """
        return f"{self.quiz_code} {self.question_text}" 
