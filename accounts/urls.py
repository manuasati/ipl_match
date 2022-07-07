from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),

	path('register/', views.registerPage, name="register"),
	path('login/', views.loginPage, name="login"),  
	path('logout/', views.logoutUser, name="logout"),

    path('enroll/', views.enrollPage, name="enroll"),

    path('ajax/post-guess/', views.postGuess, name='post-guess'),
    # path('customer/<str:pk_test>/', views.customer, name="customer"),

    # path('postPrediction/<str:pk>/', views.createOrder, name="create_order"),
    # path('update_prediction/<str:pk>/', views.updateOrder, name="update_order"),
    # path('delete_prediction/<str:pk>/', views.deleteOrder, name="delete_order"),


]