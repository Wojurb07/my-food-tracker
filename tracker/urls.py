from django.urls import path, include

from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:product_id>/modify", views.modify, name="modify"),
    path("add_product/", views.ProductCreateView.as_view(), name="product_form")
]