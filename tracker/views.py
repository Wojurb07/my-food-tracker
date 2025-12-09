from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import Product

# Create your views here.
class IndexView(generic.ListView):
    template_name = "tracker/index.html"
    context_object_name = "product_list"
    fields = ["Product", "Type", "Date", "Amount"]

    def get_queryset(self):
        """Return the list of products."""
        return Product.objects.order_by("amount")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = self.fields
        
        # Number of visits to this view, counted in the session variable
        num_visits = self.request.session.get('num_visits', 0)
        num_visits += 1 
        self.request.session['num_visits'] = num_visits
        context['num_visits'] = num_visits

        return context
    
class DetailView(generic.DetailView):
    model = Product
    template_name = "tracker/detail.html"
    
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

