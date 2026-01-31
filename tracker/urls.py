from django.urls import path, include

from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.index, name="index"),
    path("chart/", views.chart, name="chart"),
    path("products/", views.ProductsView.as_view(), name="products"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:product_id>/remove_product/", views.removeProduct, name="remove_product"),
    path("add_product/", views.ProductAddView.as_view(), name="product_form"),
    path("product_form_ocr/", views.ProductAddOcrView.as_view(), name="product_form_ocr"),
    path("product_form_ocr/ocr_form_confirmation/", views.OcrConfirmationView.as_view(), name="ocr_form_confirmation")
]