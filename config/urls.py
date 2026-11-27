from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='tasks:list')),
    path('admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('tasks/', include('tasks.urls')),
]
