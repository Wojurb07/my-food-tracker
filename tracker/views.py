from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from .models import Product
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import plotly.express as px
import pandas as pd


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
def modify(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    selected_amount = float(request.POST["amount"])

    if product.amount + selected_amount < 0:
        return render(
            request,
            "tracker/detail.html",
            {
                "product": product,
                "error_message": "The amount after updating can't be negative.",
            },
        )
    
    product.amount = F("amount") + selected_amount
    product.save()
    product.refresh_from_db()
    return HttpResponseRedirect(reverse("tracker:detail", args=(product.id,)))

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

class ProductsView(LoginRequiredMixin, generic.ListView):
    template_name = "tracker/products.html"
    context_object_name = "product_list"
    fields = ["Product", "Type", "Date"]

    def get_queryset(self):
        """Return the list of products for a logged user."""

        return Product.objects.filter(owner=self.request.user).order_by("amount")

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


class ProductCreateView(LoginRequiredMixin, generic.CreateView):
    model = Product
    fields = ["product_name", "reference"]
    success_url = reverse_lazy("tracker:product_form")

    def form_valid(self, form):
        form.instance.created_at = timezone.now()
        form.instance.user = self.request.user
        
        messages.success(self.request, "Product added successfully!")
        return super().form_valid(form)