from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from .models import Product, ReceiptImage, ProductBase
from .forms import ReceiptForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .services import ocr_service
import plotly.express as px
import pandas as pd
import torch
from doctr.models import ocr_predictor
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist


@login_required
def index(request):
    # Get some general summary information for a logged in user
    num_products = Product.objects.filter(user = request.user).count()
    three_latest_product = Product.objects.filter(user = request.user).order_by("-created_at")[:3]
    user = request.user

    context = {
        'user' : user,
        'num_products' : num_products,
        'three_latest_product' : three_latest_product,
    } 
    
    return render(request, 'tracker/index.html', context=context)

@login_required
def removeProduct(request, product_id):
    Product.objects.get(pk=product_id).delete()

    return redirect("tracker:products")

@login_required
def chart(request):

    context = { }
    return render(request, "tracker/chart.html", context)

class ProductAddOcrView(LoginRequiredMixin, generic.View):
    
    def get(self, request):
        form = ReceiptForm()
        return render(request, "tracker/product_form_ocr.html", {"form": form})

    def post(self, request):
        form = ReceiptForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request,"tracker/product_form_ocr.html"), {"form": form}

        img = form.cleaned_data.get("image")
        date = form.cleaned_data.get("created_at")
        receipt = ReceiptImage.objects.create(image = img,
                                                created_at = date)
        
        output = ocr_service.process_receipt(receipt.image.path)
        
        found_product_ids = []
        missing_products = []
        for product_info in output:
            try:
                product_base = ProductBase.objects.get(reference = product_info['code'])
                found_product_ids.append(product_base.reference)
            
            except ObjectDoesNotExist:
                missing_products.append(product_info)
        
        request.session['found_product_ids'] = found_product_ids
        request.session['missing_products'] = missing_products
        request.session["receipt_id"] = receipt.id

        return redirect("tracker:ocr_form_confirmation")

class OcrConfirmationView(LoginRequiredMixin, generic.View):
    def get(self, request):
        found_product_ids = request.session.get('found_product_ids', [])
        missing_products = request.session.get('missing_products', [])

        found_products = ProductBase.objects.filter(reference__in = found_product_ids)

        context = {"found_products":found_products,
                "missing_products":missing_products}

        return render(request, "tracker/ocr_form_confirmation.html", context)
    
    def post(self, request):
        selected_product_ids = request.POST.getlist('selected_products')
        found_product_ids = request.session.get('found_product_ids', [])
        
        approved_ids = [ref for ref in selected_product_ids if ref in found_product_ids]

        print("USER SELECTED:", selected_product_ids)
        
        # create Product objects
        approved_products = ProductBase.objects.filter(reference__in=approved_ids)

        for product_base in approved_products:
            Product.objects.create(reference = product_base,
                                            user = self.request.user)
        for key in ("found_product_ids", "missing_products", "receipt_id"):
            request.session.pop(key, None)

        return redirect("tracker:products") 


class ProductsView(LoginRequiredMixin, generic.ListView):
    template_name = "tracker/products.html"
    context_object_name = "product_list"
    fields = ["product_name", "created_at", "reference"]

    def get_queryset(self):
        """Return the list of products for a logged user."""
        return Product.objects.filter(user=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = self.fields

        # Number of visits to this view, counted in the session variable
        num_visits = self.request.session.get('num_visits', 0)
        num_visits += 1 
        self.request.session['num_visits'] = num_visits
        context['num_visits'] = num_visits

        return context
    
class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Product
    template_name = "tracker/detail.html"

class ProductAddView(LoginRequiredMixin, generic.CreateView):
    model = Product
    fields = ["reference"]
    success_url = reverse_lazy("tracker:product_form")

    def form_valid(self, form):
        form.instance.created_at = timezone.now()
        form.instance.user = self.request.user
        
        messages.success(self.request, "Product added successfully!")
        return super().form_valid(form)