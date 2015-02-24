# Create your views here.
from main.models import Movie as Movvie ,Review
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import urllib2, json
from django.views.decorators.cache import cache_page
import sys

import analysis

def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")

def all(request):
    movies = Movvie.objects.all()

    return render_to_response('index.html',
                              {"movs": movies},
                               context_instance=RequestContext(request))
def about(request):
    return render_to_response('about.html',
                              {},
                               context_instance=RequestContext(request))

@cache_page(60 * 45)
def tweets(request):
    print("tweetsssss")
    campaign_list_url = 'http://direnaj-staging.cmpe.boun.edu.tr/campaigns/list?auth_user_id=direnaj&auth_password=tamtam'
    response = urllib2.urlopen(campaign_list_url)
    #campaign_filter_url = 'http://direnaj-staging.cmpe.boun.edu.tr/campaigns/filter?auth_user_id=direnaj&auth_password=tamtam&limit=10&skip=0'
    #response = urllib2.urlopen()
    camp_json = json.load(response)
    campaigns =  [{'id':ins['campaign_id'], 'desc':ins['description']} for ins in camp_json if ins['campaign_id'].lower().rfind("deneme") < 0 and ins['description'] not in (u'',u'bos')]
    campaigns.reverse()
    return render_to_response('tweets.html',
                              {"camps": campaigns[0:20]},
                               context_instance=RequestContext(request))

from django.utils import simplejson

def campaign_json_inner(camp_id,start,limit):
    response = urllib2.urlopen('http://direnaj-staging.cmpe.boun.edu.tr/statuses/filter?skip=0&auth_user_id=direnaj&auth_password=tamtam&campaign_id=%s&limit=%s&skip=%s' % (camp_id,limit,start))
    camp_json = json.load(response)
    print(analysis.normalize("hello I am hre"))
    tweets =  [{'text' : tweet_json['tweet']['text'], 'normalized_text' : analysis.normalize(tweet_json['tweet']['text'])} for tweet_json in camp_json['results']]
    return tweets

def campaign_default(request,camp_id):
    return campaign(request,camp_id,0,10)

@cache_page(60 * 4500)
def campaign(request,camp_id,start,limit):
    #response = urllib2.urlopen('http://direnaj-staging.cmpe.boun.edu.tr/statuses/filter?skip=0&auth_user_id=direnaj&auth_password=tamtam&campaign_id=%s&limit=100' % camp_id)
    #response = urllib2.urlopen('http://direnaj-staging.cmpe.boun.edu.tr/campaigns/filter?auth_user_id=direnaj&auth_password=tamtam&limit=10&skip=0')
    #camp_json = json.load(response)
    tweets = campaign_json_inner(camp_id,start,limit)
    return render_to_response('tweets.html',
                              {"tweets": tweets},
                               context_instance=RequestContext(request))

@cache_page(60 * 4500)
def campaign_json(request,camp_id,start,limit):
    tweets = campaign_json_inner(camp_id,start,limit)
    return HttpResponse(simplejson.dumps(tweets), mimetype='application/json')
