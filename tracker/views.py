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
    products = Product.objects.filter(owner=request.user)
    fig = px.pie( 
        values = [product.amount for product in products],
        names = [product.product_type for product in products],
        title = "What's in the fridge"
    )
    chart = fig.to_html()

    context = { 'chart' : chart}
    return render(request, "tracker/chart.html", context)

# 1. Create the view to hande the loading of input_form
# 2. Create model to store the receipt
# 3. Add view logic to save the receipt
# 4. Setup the media file path
# 5. Display the confirmation pop-up window with the potential result of products added 

class ProductAddOcrView(LoginRequiredMixin, generic.View):
    
    def get(self, request):
        form = ReceiptForm()
        context = {}
        context['form'] = form
        return render(request, "tracker/product_form_ocr.html", context)

    def post(self, request):
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data.get("image")
            date = form.cleaned_data.get("created_at")
            receipt = ReceiptImage.objects.create(image = img,
                                                  created_at = date)
            receipt.save()
            output = ocr_service.process_receipt(receipt.image.path)
            products = []
            missing_products = []
            for product_info in output:
                try:
                    product_base = ProductBase.objects.get(reference = product_info['code'])
                    product = Product.objects.create(reference = product_base,
                                                    user = request.user)
                    products.append(product)
                    product.save()
                except ObjectDoesNotExist:
                    product = "Reference " + product_info['code'] + " can't be found in the product base."
                    missing_products.append(product)
                
            response_data = {"ocr_output" : output,
                             "products" : products,
                             "missing_products" : missing_products}
            return HttpResponse([output, products, missing_products], status=201)
        else:
            return HttpResponse("no image")

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