from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator  # Specifically imported 
from django.db.models import Q  # This is a text search capability
from .models import Article, Comment, Action
from .forms import CommentForm, UserCommentForm, ArticleForm, UserForm, surveyForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# DMcC 21/11/23 Function-based article retrieval to faciliate tag-search
def ArticleList(request):
    """ returns a list of articles after applying any user-entered search filter """   
    queryset = Article.objects.filter(status=1).order_by('-updated_on')
    # If the user has given a search term then check this filter
    search_post = request.GET.get('search')
    if search_post:
        queryset = queryset.filter(Q(content__icontains=search_post))

#   pagination text based on testdrive.io/blog/django-pagination for fbv    
    page_num = request.GET.get('page', 1)
    paginator = Paginator(queryset, 4) #articles per page

    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # if the page is our of range, deliver the last page
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'index.html', {'page_obj': page_obj})


class ArticleSearch(generic.ListView):
    # DMcC 21/11/23 the below search field text from stackoverflow.com re adding a search field #
#    def dynamic_articles_view(request):
#        context['object_list'] = article.objects.filter(tags__icontains=request.GET.get('search'))
#       Print("In dynamic_articles_view")
#        return render(request, "index.html", context)
    model = Article
    queryset1 = Article.objects.filter(status=1).order_by('-updated_on')
    queryset = queryset1.filter(tags=3)
    template_name = 'index.html'
    
# Detailed Article View
# DMcC 09/10/24:  Note this will only return published articles (status=1)
# Unpublished articles may only be previewed by sys administrator within a different class in this views.py
#

class ArticleDetail(View):
    def get(self, request, slug, *args, **kwargs):
        mode = 'Published'
        queryset = Article.objects.filter(status=1)
        article = get_object_or_404(queryset, slug=slug)
        comments = article.comments.filter(approved=True).order_by(
            '-created_on')
        actions = article.actions.order_by('action_seq')
        number_of_actions = actions.count()

        liked = False
        if article.likes.filter(id=self.request.user.id).exists():
            liked = True
        bookmarked = False
        if article.favourites.filter(id=self.request.user.id).exists():
            bookmarked = True

        commented = False
        commented_unapproved = False
        print('User ', self.request.user.id)
        if article.comments.filter(id=self.request.user.id).exists():
            commented = True
            if article.comments.filter(id=self.request.user.id,
                                       approved=False).exists():
                print('Unmoderated responses exist for this user')
                commented_unapproved = True
        return render(
                      request,
                      "article_detail.html",
                      {
                       "article": article,
                       "mode": mode,
                       "comments": comments,
                       "commented": commented,
                       "commented_unapproved": commented_unapproved,
                       "actions": actions,
                       "number_of_actions": number_of_actions,
                       "liked": liked,
                       "bookmarked": bookmarked,
                       "comment_form": CommentForm(),
                       },
                     )

    def post(self, request, slug, *args, **kwargs):
        queryset = Article.objects.filter(status=1)
        article = get_object_or_404(queryset, slug=slug)
        comments = article.comments.filter(approved=True).order_by(
            '-created_on')
        actions = article.actions.order_by('action_seq')
        number_of_actions = actions.count()
        liked = False
        if article.likes.filter(id=self.request.user.id).exists():
            liked = True
        bookmarked = False
        if article.favourites.filter(id=self.request.user.id).exists():
            bookmarked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
                    request,
                    "article_detail.html",
                    {
                        "article": article,
                        "comments": comments,
                        "commented": True,
                        "commented_unapproved": True,
                        "comment_form": CommentForm(),
                        "liked": liked,
                        "bookmarked": bookmarked,
                        "actions": actions,
                        "number_of_actions": number_of_actions,
                       
                    },
                    )


# This is used when article is liked/unliked
# from within the article detail page
class ArticleLike(View):
    def post(self, request, slug, *args, **kwargs):
        article = get_object_or_404(Article, slug=slug)
        if article.likes.filter(id=request.user.id).exists():
            article.likes.remove(request.user)
        else:
            article.likes.add(request.user)
        return HttpResponseRedirect(reverse('article_detail', args=[slug]))


# This is used when article is liked/unliked
# from within the index/article summary page
# DMcC 15/11/23 this still needs some work as the
# user is currently returned to the article detail page after like/unlike
class ArticleSummaryLike(View):
    def post(self, request, slug, *args, **kwargs):
        article = get_object_or_404(Article, slug=slug)
        number_of_actions = article.actions.count()
        if article.likes.filter(id=request.user.id).exists():
            article.likes.remove(request.user)
        else:
            article.likes.add(request.user)

# DMcC 18/11/23 want to play around with a render rather than a return
# statement at the endof this logic,
# could ths be used to return to the index page
# when this option is taken from the index page to start with?
            return render(
                          request,
                          "index.html",
                          {
                           "article": article,
                           "comments": comments,
                           "comment_count": comments.count,
                           "commented": commented,
                           "actions": actions,
                           "number_of_actions": number_of_actions,
                           "liked": liked,
                           "bookmarked": bookmarked,
                          },
                         )


# This is used when article is bookmarked/unbookmarked
# from within the index/article summary OR article detail page
# DMcC 15/11/23 this still needs some work as the user is currently
#  returned to the article detail page after bookmarking
class ArticleBookmark(View):
    def post(self, request, slug, *args, **kwargs):
        article = get_object_or_404(Article, slug=slug)
        if article.favourites.filter(id=request.user.id).exists():
            article.favourites.remove(request.user)
            messages.add_message(request, messages.SUCCESS,
                                 "Article removed from your Reading List")
        else:
            article.favourites.add(request.user)
            messages.add_message(request, messages.SUCCESS,
                                 "Article added to your Reading List")
        return HttpResponseRedirect(reverse('article_detail', args=[slug]))


class ArticleComment(View):
    def post(self, request, slug, *args, **kwargs):
        article = get_object_or_404(Article, slug=slug)
        comments = article.comments.filter(approved=True).order_by(
            '-created_on')

        return render(
                      request,
                      "index.html",
                      {
                       "article": article,
                       "comments": comments,
                       "comment_count": comments.count,
                       "commented": commented,
                       "actions": actions,
                       "liked": liked,
                       "bookmarked": bookmarked,
                      },
            )


def maint_articles(request):
    """ This is a sysadmin view to show all articles,
    and allow the sysadmin to edit/delete """
    print('In view maint_articles')
    articles = Article.objects.all()

    # sort by SKU in order asc/desc
    articles = articles.order_by('-updated_on')
    context = {
        'articles': articles,
    }

    return render(request, 'fp_blog/maint_articles.html', context)


# DMcC 09/10/24 inserted the below code modified from jeweller add_product
# Add @login_required decorator to ensure user logged in
# before executing the view (otherwise redirects them to login)
@login_required
def add_article(request):
    """ Sysadmin:  Add a article to the store """
    # If not a superuser kick user out of function
    if not request.user.is_superuser:
        messages.error(request, 'Restricted: Must have SysAdmin rights'
                       + ' to Add articles!')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            stringy = (f'Successfully added article title { article.slug },'
                       + f'{ article.title }.')
            messages.success(request, stringy)

            # return redirect(reverse('add_article'))
            # go to the new article detail - sysadmin can check result
            # return redirect(reverse('article_detail', args=[article.id]))

            # DMcC 11/10/24 - go back to the maintenance screen (as article may not yet be 'published'
            # and therefore wont appear on the 'normal' article view 
            # - success message should also pop up at top of screen
            # return HttpResponseRedirect(reverse('article_detail', args=[article.slug]))
            
            return redirect('maint_articles')  # Redirect to your articles list page
        else:
            messages.error(request, 'Failed to add article.'
                           + ' Please ensure the form is valid.')
    else:
        form = ArticleForm()
    template = 'fp_blog/add_article.html'
    context = {
        'form': form,
    }

    return render(request, template, context)



# DMcC 09/10/24:  Preview articles (regardless of published status)
def article_preview(request, article_id):
    """ A view to show individual article details """
    mode = 'Preview'
    article = get_object_or_404(Article, pk=article_id)
            
    # getting all aspects of the article (this will be added to later to include article tags, bookmarks etc)
    context = {
            'article': article,
            'mode': mode,
            }
    return render(request, 'article_detail.html', context)

# DMcC 09/10/24 Recycled code (was originally used for product edit in jeweller project)
# Add @login_required decorator to ensure user logged in
# @login_required
def edit_article(request, article_id):
    """ Edit an article  """
    # If not a superuser kick user out of function
    if not request.user.is_superuser:
        messages.error(request, 'Restricted: Must have SysAdmin rights '
                       + 'to edit articles!')
        return redirect(reverse('home'))
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)

        if form.is_valid():
            form.save()
            stringy = f'Successfully updated article{article.id }, {article.title}'
            messages.success(request, stringy)
            
            # DMcC 11/10/4: The piece of code below (which is duplicated elsewhere and will need to be refactored ) is to redisplay the maintenance screen
            articles = Article.objects.all()

            # sort by article in desc order (most recent on top)
            articles = articles.order_by('-updated_on')
            context = {
                'articles': articles,
            }
            return render(request, 'fp_blog/maint_articles.html', context)
        else:
            messages.error(request, 'Failed to update article.'
                           + ' Please ensure the form is valid.')
    else:
        form = ArticleForm(instance=article)
        messages.info(request, f'You are editing {article.title}')

    template = 'fp_blog/edit_article.html'
    context = {
        'form': form,
        'article': article,
    }

    return render(request, template, context)

# created by Ste 11/10/24 4:06am 
# made as to allow deletion of articles as I see no code to this prior. very basic => needs login permission etc added.

def delete_article(request, id):
    article = get_object_or_404(Article, id=id)
    if request.method == 'POST':
        article.delete()
        return redirect('maint_articles')  # Redirect to your articles list page


#created Ste 14/10/24 
# made for maint_users html page. 
# def maint_users(request):
#       users = User.objects.all()
#       return render(request, 'fp_blog/maint_users.html', {'users': users})
#
#
def maint_users(request):
    """ This is a sysadmin view to show all users,
    and allow the sysadmin to edit/delete """
    print('In view maint_users')
    users = User.objects.all()

    print('Users:  ', users)

    # sort by ??? in order asc/desc
    users = users.order_by('date_joined')
    context = {
        'users': users,
    }

    return render(request, 'fp_blog/maint_users.html', context)


#created 16/10/24 1am
   
def edit_user(request, user_id):
    """ Edit an article  """
    # If not a superuser kick user out of function
    if not request.user.is_superuser:
        messages.error(request, 'Restricted: Must have SysAdmin rights '
                       + 'to edit users!')
        return redirect(reverse('home'))
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            stringy = f'Successfully updated user{user.id }, {user.username}'
            messages.success(request, stringy)
            
            return redirect('maint_users')  # Redirect to your users list page
        else:
            messages.error(request, 'Failed to update user.'
                           + ' Please ensure the form is valid.')
    else:
        form = UserForm(instance=user)
        messages.info(request, f'You are editing {user.username}')

    template = 'fp_blog/edit_user.html'
    context = {
        'form': form,
        'user': user,
    }

    return render(request, template, context)

   
@login_required
def add_user(request):
    """ Sysadmin:  Add a User to the db """
    # If not a superuser kick user out of function
    if not request.user.is_superuser:
        messages.error(request, 'Restricted: Must have SysAdmin rights'
                       + ' to Add articles!')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            stringy = (f'Successfully added article title { user.username },'
                       + f'{ user.username }.')
            messages.success(request, stringy)

            # return redirect(reverse('add_article'))
            # go to the new article detail - sysadmin can check result
            # return redirect(reverse('article_detail', args=[article.id]))

            # DMcC 11/10/24 - go back to the maintenance screen (as article may not yet be 'published'
            # and therefore wont appear on the 'normal' article view 
            # - success message should also pop up at top of screen
            # return HttpResponseRedirect(reverse('article_detail', args=[article.slug]))
            
            return redirect('maint_users')  # Redirect to your articles list page
        else:
            messages.error(request, 'Failed to add user.'
                           + ' Please ensure the form is valid.')
    else:
        form = UserForm()
    template = 'fp_blog/add_user.html'
    context = {
        'form': form,
    }

    return render(request, template, context)

def toggle_activate_user(request, user_id):
    """ Deactiveate / reactivate User accounts """
    # DMcC 17/10/24  added as an alterative to deleting accounts as there 
    # could be assocated information (articles etc) which would like to preserve rather than deleting entire user

    # If not a superuser kick user out of function
    if not request.user.is_superuser:
        messages.error(request, 'Restricted: Must have SysAdmin rights '
                       + 'to activate/deactivate users!')
        return redirect(reverse('home'))
    user = get_object_or_404(User, pk=user_id)
    print('User active setting ', user.is_active)
    new_active = not(user.is_active)
    user.is_active = new_active
    print('New user active setting ', user.is_active)

    user.save()
    stringy_action=''
    if not user.is_active:
        stringy_action = 'de'
    

    stringy = f'Successfully ' + stringy_action + 'activated user{user.id }, {user.username}'
    messages.success(request, stringy)
            
    return redirect('maint_users')  # Redirect to your users list page
    


def delete_user(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        user.delete()
    return redirect('maint_users')  # Redirect to your users list page
    
def user_preview(request, user_id):
    """ A view to show individual user details """
    mode = 'Preview'
    user = get_object_or_404(user, pk=user_id)
            
    # getting all aspects of the user (this will be added to later to include user tags, bookmarks etc)
    context = {
            'user': user,
            'mode': mode,
            }
    return render(request, 'user_detail.html', context)
    
    
#
#
#
# 23/10/24 - ste first Survey set up.
@login_required
def survey1(request):
    if request.method == 'POST':
        form = surveyForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            return render(request, 'success_template.html', {'user': user})  # Change to your success template
    else:
        form = surveyForm()  # Initialize the form for GET requests

    return render(request, 'fp_blog/survey1.html', {'form': form})



def error_400(request, exception):
    data = {}
    return render(request,'400.html', data)

def error_403(request, exception):
    data = {}
    return render(request,'403.html', data)

def error_404(request, exception):
    data = {}
    return render(request,'404.html', data)

def error_500(request, *args, **argv):
    return render(request,'500.html', status=500)
