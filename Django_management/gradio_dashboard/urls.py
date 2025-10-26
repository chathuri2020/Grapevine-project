from django.urls import path
from . import views

app_name = 'gradio_dashboard'
urlpatterns = [
    path('single_image/', views.single_image, name='single_image'),
    path('batch_zip/', views.batch_zip, name='batch_zip'),
    path('report/', views.report, name='report'),

    # Your JavaScript must use this exact path:
    path('single_image_t/', views.single_image_api, name='single_image_api'),
]
