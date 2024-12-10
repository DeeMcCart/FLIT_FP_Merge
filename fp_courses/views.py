from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic, View
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator  # Specifically imported 
from django.db.models import Q  # This is a text search capability
from .models import Course, Cohort, CourseContents, Quiz

from .forms import CourseForm, QuizForm  # Cuasing all the issues. 

from fp_personal.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date
import pandas as pd
import numpy as np




# Create your views here.
def MyCourses(request):
    # courses need to link to courses and have a questionaire after them. possibly multiple questions.
    # so maybe is we had a 2d array where each column had the course and then multiple choice questions after them. 
    # courses Structure => courses[ Course ID, Course ID, Course ID,]    Main = [ID , course ID , Quiz ID , Quiz ID , Quiz ID , Quiz ID]     Quiz[] =[Quiz ID , Q1 , ANS1 , ANS2 , ANS3 , ANS4 ,]  x several times etc. and that will be the course ANS1 will always be correct answer but the html will be told to randomize the order. 
    # List of course ID's 
    # need to make a diffrent array for users scores and add it to their profile.
    # need to make a menu to display all courses.
    # need to make a page to allow an admin to make a custome test / course.
    
    # DMcC 26/11/24 - I need to do some more work to ensure only cohorts that are valid for the user are returned.... 
    # Just need to wait for my brain to become usable again!
    print("in view MyCourses, current user is ", request.user)
    cohorts = ['Public',]
    print("Initial cohorts (whether logged in or not) are ", cohorts)
    queryset1 = Cohort.objects.filter(status=1).order_by('-updated_on') 
    print("Additional cohorts for logged in user (not yet filtered by user) are", queryset1)
    courses = []
    queryset = Course.objects.filter(status=1).order_by('-updated_on')
    print(queryset)
    context = {
        queryset,
    }    
    return render(request, 'fp_courses/my_courses.html', context)

@login_required
def user_cohorts_courses(request):
  user = request.user
  
  # Get user's cohorts (adjust queryset based on your relationships)
  cohorts = user.cohort_user.all()

  # Iterate through cohorts and get assigned courses (adjust queryset)
  courses = []
  for cohort in cohorts:
    assigned_courses = cohort.course.all()
    courses.extend(assigned_courses)

  context = {
      'cohorts': cohorts,
      'courses': courses,
  }
  return render(request, 'fp_courses/user_cohorts_courses.html', context)


def maint_courses(request):
    """ This is a sysadmin view to show all Courses,
    and allow the sysadmin to edit/delete """
    print('In view maint_courses')
    courses = Course.objects.all()

    # sort by SKU in order asc/desc
    courses = courses.order_by('-updated_on')
    context = {
        'courses': courses,
    }
    
    return render(request, 'fp_courses/maint_courses.html', context)

@login_required
def add_course(request):
    """ Sysadmin: Add a course to the site """
    if not request.user.is_superuser:
        messages.error(request, 'Restricted: Must have SysAdmin rights to Add courses!')
        return redirect(reverse('home'))

    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES)
        print(" made it past first if statement")
        if course_form.is_valid():
            course = course_form.save(commit=False)
            course.slug = course.title
            course.author = request.user
            course.updated_on = date.today()
            course.save()
            print(" course form is valid")
            stringy = f'Successfully added course {course.course_code}, {course.title}'
            messages.success(request, stringy)
            return redirect('maint_courses')  # Redirect after successful submission
    else:
        course_form = CourseForm()  # Initialize form for GET request
        print(" else statement for failsafe.")

    print(course_form.errors)
    return render(request, 'fp_courses/add_course.html', {'form': course_form})


def edit_course(request, id):
     
    
    if not request.user.is_superuser:
        print("Not user")
        messages.error(request, 'Restricted: Must have SysAdmin rights '
                       + 'to edit a course!')
        return redirect(reverse('home'))
    course = get_object_or_404(Course, pk=id)
    original_course_code = course.course_code
    if request.method == 'POST':
        print("got this far")
        course_form = CourseForm(request.POST, request.FILES, instance=course)
        # DMcC 09/11/24 - Set updated_on field to today
        if course_form.is_valid():
            course = course_form.save(commit=False)
            if course.course_code != original_course_code:
                # course code has been changed, delete the original instance
                Course.objects.filter(pk=id).delete()
            course.updated_on = date.today()
            course.save()
            stringy = f'Successfully updated Course { course.course_code }, {course.title}'
            messages.success(request, stringy)
            
            # DMcC 11/10/4: The piece of code below (which is duplicated elsewhere and will need to be refactored ) is to redisplay the maintenance screen
            courses = Course.objects.all()

            # sort by course in desc order (most recent on top)
            courses = courses.order_by('-updated_on')
            context = {
                'courses': courses,
            }
            return render(request, 'fp_courses/maint_courses.html', context)
        else:
            messages.error(request, 'Failed to update course.'
                           + ' Please ensure the form is valid.')
    else:
        course_form = CourseForm(instance=course)
        messages.info(request, f'You are editing {course.title}')

    template = 'fp_courses/edit_course.html'
    context = {
        'form': course_form,
        'course': course,
    }

    return render(request, template, context)

def delete_course(request, id):
    course = get_object_or_404(Course, course_code=id)
    if request.method == 'POST':
        course.delete()
        return redirect('maint_courses')  # Redirect to your courses list page

def course_preview(request, course_code):
    """ A view to show individual course details """
    mode = 'Preview'
    course = get_object_or_404(Course, pk=course_code)
            
    # getting all aspects of the course (this will be added to later to include course tags, bookmarks etc)
    context = {
            'course': course,
            'mode': mode,
            }
    return render(request, 'fp_courses/course_preview.html', context)

def maint_quizzes(request):
    """ This is a sysadmin view to show all Quizzes,
    and allow the sysadmin to edit/delete """
    quiz = Quiz.objects.all()

    # sort by SKU in order asc/desc
    quiz = quiz.order_by('quiz_code')
    context = {
        'quiz': quiz,
    }
    
    return render(request, 'fp_courses/maint_quizzes.html', context)

@login_required
def add_quiz(request): # content has been copied from add course. needs editing. 
    
    """ Sysadmin: Add a quiz to the site """
    if not request.user.is_superuser:
        messages.error(request, 'Restricted: Must have SysAdmin rights to Add quizzes!')
        return redirect(reverse('home'))

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, request.FILES)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.slug = quiz.question_text
            quiz.author = request.user
            quiz.updated_on = date.today()
            quiz.save()
            print(" quiz form is valid")
            stringy = f'Successfully added course {quiz.quiz_code}, {quiz.question_text}'
            messages.success(request, stringy)
            return redirect('maint_quizzes')  # Redirect after successful submission
    else:
        quiz_form = QuizForm()  # Initialize form for GET request
        print(" else statement for failsafe.")

    print(quiz_form.errors)

    return render(request, 'fp_courses/add_quiz.html', {'form': quiz_form} )




def edit_quiz(request, id):
    
    if not request.user.is_superuser:
        print("Not user")
        messages.error(request, 'Restricted: Must have SysAdmin rights '
                       + 'to edit a quiz!')
        return redirect(reverse('home'))
    quiz = get_object_or_404(Quiz, pk=id)
    original_quiz_code = quiz.quiz_code
    if request.method == 'POST':
        print("got this far")
        quiz_form = QuizForm(request.POST, request.FILES, instance=quiz)
        # DMcC 09/11/24 - Set updated_on field to today
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            if quiz.quiz_code != original_quiz_code:
                # course code has been changed, delete the original instance
                Quiz.objects.filter(pk=id).delete()
            quiz.updated_on = date.today()
            quiz.save()
            stringy = f'Successfully updated quiz { quiz.quiz_code }, {quiz.question_text}'
            messages.success(request, stringy)
            
            # DMcC 11/10/4: The piece of code below (which is duplicated elsewhere and will need to be refactored ) is to redisplay the maintenance screen
            quiz = Quiz.objects.all()

            # sort by quiz in desc order (most recent on top)
            quiz = quiz.order_by('-updated_on')
            context = {
                'quiz': quiz,
            }
            return render(request, 'fp_courses/maint_quizzes.html', context)
        else:
            messages.error(request, 'Failed to update quiz.'
                           + ' Please ensure the form is valid.')
    else:
        quiz_form = QuizForm(instance=quiz)
        messages.info(request, f'You are editing {quiz.question_text}')

    template = 'fp_courses/edit_quiz.html'
    context = {
        'form': quiz_form,
        'quiz': quiz,
    }

    return render(request, template, context)


def delete_quiz(request, id):
    
    quiz = get_object_or_404(Quiz, quiz_code=id)
    if request.method == 'POST':
        quiz.delete()
        return redirect('maint_quizzes')  # Redirect to your courses list page
    
    return render(request, 'fp_courses/delete_quiz.html')

def quiz_preview(request):
    
    return render(request, 'fp_courses/quiz_preview.html')