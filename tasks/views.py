from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from .forms import TaskForm
from .models import Task


class OwnerTaskMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


class TaskListView(OwnerTaskMixin, ListView):
    template_name = 'tasks/task_list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at', '-id')
        status = self.request.GET.get('status')
        valid_statuses = {choice[0] for choice in Task.STATUS_CHOICES}
        if status in valid_statuses:
            queryset = queryset.filter(status=status)
        return queryset


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TaskDetailView(OwnerTaskMixin, DetailView):
    template_name = 'tasks/task_detail.html'


class TaskUpdateView(OwnerTaskMixin, UpdateView):
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(OwnerTaskMixin, DeleteView):
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')
