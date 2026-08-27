from django.views import View
from mkt.models import Ad, Comment, Fav
# from mkt.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, from mkt.owner import OwnerListView, OwnerDetailView,
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from mkt.owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from mkt.forms import CreateForm, CommentForm
from django.db.utils import IntegrityError
from django.db.models import Q



class AdListView(OwnerListView):
    model = Ad
    template_name = "mkt/ad_list.html"

    def get_queryset(self):
        qs = super().get_queryset()

        search = self.request.GET.get("search", False)

        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(text__icontains=search)
            )

        return qs


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = 'mkt/ad_detail.html'

    def get(self, request, pk):
        ad = get_object_or_404(Ad, id=pk)

        comments = Comment.objects.filter(ad=ad).order_by('-updated_at')

        comment_form = CommentForm()

        context = {
            'ad': ad,
            'comments': comments,
            'comment_form': comment_form,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        ad = get_object_or_404(Ad, id=pk)

        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = Comment(
                text=comment_form.cleaned_data['comment'],
                owner=request.user,
                ad=ad
            )
            comment.save()

            return redirect('mkt:ad_detail', pk=ad.id)

        comments = Comment.objects.filter(ad=ad).order_by('-updated_at')

        context = {
            'ad': ad,
            'comments': comments,
            'comment_form': comment_form,
        }

        return render(request, self.template_name, context)

class CommentCreateView(LoginRequiredMixin, View):

    def post(self, request, pk):
        ad = get_object_or_404(Ad, id=pk)

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = Comment(
                text=form.cleaned_data['comment'],
                owner=request.user,
                ad=ad
            )
            comment.save()

        return redirect('mkt:ad_detail', pk=pk)


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

        form.save_m2m()

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

        form.save_m2m()

        return redirect(self.success_url)
# class AdUpdateView(OwnerUpdateView):
#     model = Ad
#     fields = ['title', 'price', 'text']

class CommentDeleteView(LoginRequiredMixin, View):
    template_name = 'mkt/comment_confirm_delete.html'

    def get(self, request, pk):
        comment = get_object_or_404(
            Comment,
            id=pk,
            owner=request.user
        )

        context = {
            'comment': comment
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        comment = get_object_or_404(
            Comment,
            id=pk,
            owner=request.user
        )

        ad_id = comment.ad.id
        comment.delete()

        return redirect('mkt:ad_detail', pk=ad_id)
class AdDeleteView(OwnerDeleteView):
    model = Ad

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ToggleFavoriteView(LoginRequiredMixin, View):

    def post(self, request, pk):
        ad = get_object_or_404(Ad, id=pk)

        fav = Fav(
            user=request.user,
            ad=ad
        )

        try:
            fav.save()
            return HttpResponse("Favorite added 42")

        except IntegrityError:
            Fav.objects.get(
                user=request.user,
                ad=ad
            ).delete()

            return HttpResponse("Favorite deleted 42")

def stream_file(request, pk):
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response