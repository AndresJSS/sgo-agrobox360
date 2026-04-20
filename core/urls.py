"""
URL configuration for core project.

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
from django.urls import path
from operaciones.views import dashboard, eliminar_cultivo, editar_cultivo, traspaso_sistema, cosechar_cultivo, historial, pagina_tareas, completar_tarea, crear_tarea, editar_tarea, eliminar_tarea

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('eliminar-cultivo/<int:id>/', eliminar_cultivo, name='eliminar_cultivo'),
    path('editar-cultivo/<int:id>/', editar_cultivo, name='editar_cultivo'),
    path('traspaso-sistema/<int:id>/', traspaso_sistema, name='traspaso_sistema'),
    path('cosechar-cultivo/<int:id>/', cosechar_cultivo, name='cosechar_cultivo'),
    path('historial/', historial, name='historial'),
    path('tareas/', pagina_tareas, name='tareas'),
    path('tareas/crear/', crear_tarea, name='crear_tarea'),
    path('tareas/completar/<int:tarea_id>/', completar_tarea, name='completar_tarea'),
    path('tareas/editar/<int:tarea_id>/', editar_tarea, name='editar_tarea'),
    path('tareas/eliminar/<int:tarea_id>/', eliminar_tarea, name='eliminar_tarea'),
]
