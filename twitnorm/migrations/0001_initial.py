# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tweet'
        db.create_table(u'twitnorm_tweet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'twitnorm', ['Tweet'])


    def backwards(self, orm):
        # Deleting model 'Tweet'
        db.delete_table(u'twitnorm_tweet')


    models = {
        u'twitnorm.tweet': {
            'Meta': {'object_name': 'Tweet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['twitnorm']