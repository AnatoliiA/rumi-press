from mkt.models import Ad
from django.views import View
# from mkt.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, from mkt.owner import OwnerListView, OwnerDetailView,
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from mkt.owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from mkt.forms import CreateForm

class AdListView(OwnerListView):
    model = Ad
    # By convention:
    # template_name = "mkt/Ad_list.html"


class AdDetailView(OwnerDetailView):
    model = Ad


class AdCreateView(LoginRequiredMixin, View):
    template_name = 'mkt/ad_form.html'
    success_url = reverse_lazy('mkt:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)

# class AdCreateView(OwnerCreateView):
#     model = Ad
#     # List Ad model fields to copy to the Ad form / template
#     fields = ['title', 'price', 'text']

class AdUpdateView(LoginRequiredMixin, View):
    template_name = 'mkt/ad_form.html'
    success_url = reverse_lazy('mkt:all')

    def get(self, request, pk):
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save()

        return redirect(self.success_url)
# class AdUpdateView(OwnerUpdateView):
#     model = Ad
#     fields = ['title', 'price', 'text']


class AdDeleteView(OwnerDeleteView):
    model = Ad


def stream_file(request, pk):
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response