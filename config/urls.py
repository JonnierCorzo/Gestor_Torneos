"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # Torneos (ya los tenías)
    path('torneos/', views.torneos_list, name='torneos_list'),
    path('torneos/nuevo/', views.torneo_create, name='torneo_create'),
    path('torneos/<int:pk>/', views.torneo_detail, name='torneo_detail'),
    path('torneos/<int:pk>/editar/', views.torneo_update, name='torneo_update'),
    path('torneos/<int:pk>/eliminar/', views.torneo_delete, name='torneo_delete'),

    # Jugadores
    path('jugadores/', views.jugadores_list, name='jugadores_list'),
    path('jugadores/nuevo/', views.jugador_create, name='jugador_create'),

    # Partidos
    path('partidos/', views.partidos_list, name='partidos_list'),
    path('partidos/nuevo/', views.partido_create, name='partido_create'),
    path('partidos/<int:pk>/editar/', views.partido_update, name='partido_update'),
    path('partidos/<int:pk>/resultado/', views.partido_set_resultado, name='partido_set_resultado'),
    path('partidos/generar/', views.partidos_generar, name='partidos_generar'),
    
    # Equipos
    path('equipos/', views.equipos_list, name='equipos_list'),
    path('equipos/nuevo/', views.equipo_create, name='equipo_create'),
    path('equipos/<int:pk>/editar/', views.equipo_update, name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', views.equipo_delete, name='equipo_delete'),
    
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls'))
]  
