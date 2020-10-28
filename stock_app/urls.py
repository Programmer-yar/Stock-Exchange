from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="stock-home"),
    path('result/', views.result, name='stock-result'),
    path('pdf-result', views.pdf_result, name='pdf-result'),
    path('upload', views.upload_file, name='upload'),
    path('downloads', views.downloads, name='downloads'),
    path('inputs', views.my_inputs, name='inputs'),
    path('test', views.result_email, name='test')
    ]
