from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from data.models import Topic

from django.contrib.admin.views.decorators import staff_member_required
import random


@staff_member_required
def topics_overview(request):
    topics = Topic.objects.order_by('name')
    return render(request, 'dashboard/topics/overview.html', {'topics': topics, 'debug': settings.DEBUG})


@staff_member_required
def papers_for_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    papers = list(topic.papers.all())
    return render(request, 'dashboard/topics/topic_papers.html',
                  {'topic': topic, 'papers': papers, 'debug': settings.DEBUG})


@staff_member_required
def merge_generated(request):
    if request.method == 'POST':
        new_topic = Topic()
        new_topic.save()
        for topic in Topic.objects.all():
            if topic.name.startswith('Generated:'):
                for paper in topic.papers.all():
                    paper.topic = new_topic
                    paper.save()
                topic.delete()
        new_topic.name = 'Generated Merged'
        new_topic.save()
        messages.add_message(request, messages.SUCCESS, f"Merged Topics")
        return redirect('topics')
    return 404


@staff_member_required
def merge_topics(request):
    if request.method == 'POST':
        topic1_id = request.POST.get('topic1', None)
        topic2_id = request.POST.get('topic2', None)
        if topic1_id is not None and topic2_id is not None:
            topic1, topic2 = [get_object_or_404(Topic, pk=id) for id in [topic1_id, topic2_id]]
            # we put all papers from topic 2 into topic 1 and delete topic2
            for paper in topic2.papers.all():
                paper.topic = topic1
                paper.save()
            topic1.keywords += ', ' + topic2.keywords
            topic1.save()
            topic2.delete()
            messages.add_message(request, messages.SUCCESS, f"Merged Topics")
            return redirect('topics')
        else:
            messages.add_message(request, messages.ERROR, f"Topics not found")
    topics = Topic.objects.order_by('name')
    return render(request, 'dashboard/topics/merge.html', {'topics': topics, 'debug': settings.DEBUG})
