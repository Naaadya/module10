from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.login_page, name = 'Home'),
    path('logout/', views.logout_page, name = 'Logout'),
    path('createUser/', views.createUser, name = 'Create'),
    path('registerUser/',views.registerUser, name= 'Register'),
    path('profile/', views.profile, name = 'Profile'),
    path('company/', views.companies, name = 'Company'),
    path('add-user-to-company/<int:company_id>', views.addUserToCompany, name = 'Add user to company'),
    path('deleteCompany/', views.deleteCompany),
    path('company/<int:company_id>', views.houses),
    path('deleteHouse/<int:company_id>', views.deleteHouse),
    path('company/<int:company_id>/<int:house_id>', views.apartments),
    path('deleteApartment/<int:company_id>/<int:house_id>',views.deleteApartment)
]
