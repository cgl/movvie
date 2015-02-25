# Create your views here.
from main.models import Movie as Movvie ,Review
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import urllib2, json
from django.views.decorators.cache import cache_page
import sys,traceback

import standalone

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
def get_campaigns(request):
    print("campaigns")
    campaign_list_url = 'http://direnaj-staging.cmpe.boun.edu.tr/campaigns/list?auth_user_id=direnaj&auth_password=tamtam'
    response = urllib2.urlopen(campaign_list_url)
    #campaign_filter_url = 'http://direnaj-staging.cmpe.boun.edu.tr/campaigns/filter?auth_user_id=direnaj&auth_password=tamtam&limit=10&skip=0'
    #response = urllib2.urlopen()
    camp_json = json.load(response)
    campaigns =  [{'id':ins['campaign_id'], 'desc':ins['description']} for ins in camp_json if ins['campaign_id'].lower().rfind("deneme") < 0 and ins['description'] not in (u'',u'bos')]
    campaigns.reverse()
    return render_to_response('tweets.html',
                              {"title" : "Campaigns",
                               "camps": campaigns[0:20] },
                              context_instance=RequestContext(request))

from django.utils import simplejson

def campaign_json_inner(camp_id,start,limit):
    response = urllib2.urlopen('http://direnaj-staging.cmpe.boun.edu.tr/statuses/filter?skip=0&auth_user_id=direnaj&auth_password=tamtam&campaign_id=%s&limit=%s&skip=%s' % (camp_id,limit,start))
    camp_json = json.load(response)
    print("hello I am hre")
    tweets =  [{'text' : tweet_json['tweet']['text']} for tweet_json in camp_json['results']]
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
                              {
                                  "title" : "Tweets",
                                  "tweets": tweets},
                               context_instance=RequestContext(request))

@cache_page(60 * 4500)
def campaign_json(request,camp_id,start,limit):
    tweets = campaign_json_inner(camp_id,start,limit)
    return HttpResponse(simplejson.dumps(tweets), mimetype='application/json')


def norm_text(request):
    normed_text = ""
    print("about to norm")
    if request.method == 'POST':
        #user = request.user
        text = request.POST.get('norm_text', None)
        print("***"+text)
        try:
            obj = standalone.main(text)
            print("Number of OOV token %d " % len(obj.oov_tokens))
            normed_text = " ".join([word for word,_,_ in obj.normalization])
        except:
            traceback.print_exc()
    print("Normalization completed")
    return HttpResponse(simplejson.dumps({"normalization":normed_text}),
                    mimetype='application/javascript')

"""
Traceback (most recent call last):
  File "/home/cagil/repos/movvie/main/views.py", line 79, in norm_text
    obj = standalone.main(text)
  File "/home/cagil/repos/CWA-Normalizer/standalone.py", line 12, in main
    tweet_obj.print_normalized()
  File "/home/cagil/repos/CWA-Normalizer/standalone.py", line 96, in print_normalized
    print(" ".join(output))
UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 0: ordinal not in range(128)
Done
[25/Feb/2015 19:37:03] "POST /main/norm/ HTTP/1.1" 200 35
"""
