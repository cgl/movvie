# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Movie'
        db.create_table(u'main_movie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('movvie_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('release_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('rating', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'main', ['Movie'])

        # Adding model 'Review'
        db.create_table(u'main_review', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('review_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('movie', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Movie'])),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('rating', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'main', ['Review'])

        # Adding model 'Sentence'
        db.create_table(u'main_sentence', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sentence_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('review', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Review'])),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('sentiment', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'main', ['Sentence'])


    def backwards(self, orm):
        # Deleting model 'Movie'
        db.delete_table(u'main_movie')

        # Deleting model 'Review'
        db.delete_table(u'main_review')

        # Deleting model 'Sentence'
        db.delete_table(u'main_sentence')


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
            'rating': ('django.db.models.fields.FloatField', [], {}),
            'review_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
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