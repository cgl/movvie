# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Review.review_id'
        db.delete_column(u'main_review', 'review_id')


    def backwards(self, orm):
        # Adding field 'Review.review_id'
        db.add_column(u'main_review', 'review_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0, unique=True),
                      keep_default=False)


    models = {
        u'main.movie': {
            'Meta': {'object_name': 'Movie'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'movvie_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {}),
            'release_date': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'main.review': {
            'Meta': {'object_name': 'Review'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'movie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Movie']"}),
            'rating': ('django.db.models.fields.FloatField', [], {})
        },
        u'main.sentence': {
            'Meta': {'object_name': 'Sentence'},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'review': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Review']"}),
            'sentence_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'sentiment': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        }
    }

    complete_apps = ['main']