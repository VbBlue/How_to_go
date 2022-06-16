from django.urls import path
from GOHelp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('bizlist/', views.BizListView.as_view(), name='biz_list'),
    path('biz/<str:pk>', views.BizDetailView.as_view(), name='info-detail'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('bookmark_in/', views.bookmark_in, name='bookmark_in'),
    path('bookmark_out/', views.bookmark_out, name='bookmark_out'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bmk_list'),
]