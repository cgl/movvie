from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from main import views

urlpatterns = patterns('',
    # ex: /polls/
    url(r'movies/$', views.all, name='all'),
    url(r'tweets/$', views.tweets, name='get_tweets'),
    url(r'about/$', views.about, name='about'),
    url(r'tweets/campaign/(?P<camp_id>\w+)/$', views.campaign.as_view() , name='campaign2', ),
#    url(r'tweets/campaign/(?P<camp_id>\w+)/$', views.campaign_json, name='campaign_json'),

    url(r'tweets/campaign/(?P<camp_id>\w+)/(?P<start>\d+)/(?P<limit>\d+)/$', views.campaign, name='campaign'),
    url(r'tweets/campaign/(?P<camp_id>\w+)/json/(?P<start>\d+)/(?P<limit>\d+)/$', views.campaign_json, name='campaign_json'),
    # ex: /polls/5/
#    url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
#    url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
#    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)
