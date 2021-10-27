from django.urls import path
from myapp import views

app_name = 'myapp'

urlpatterns = [
    path('registration/', views.RegistrationView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('user/', views.UserView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('post/', views.PostCreateView.as_view()),
    path('post-list/', views.PostListView.as_view()),
    path('post-detail/', views.PostDetailView.as_view()),
    path('post/<int:post_id>/like/', views.PostLikeView.as_view()),
    path('post/<int:post_id>/dislike/', views.PostDislikeView.as_view()),
    path('user/detail/', views.UserDetailView.as_view()),
    path('user/analytics/date_from=<from>&date_to=<to>/', views.LikeStatsView.as_view()),

]
