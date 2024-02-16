import uuid
from django.views.generic import TemplateView
from django.conf import settings
from django.core.cache import caches
import logging
import pika 
import time


class MainView(TemplateView):
    template_name = 'main.html'

    def cache_set(self, cache_db='default'):
        try:
            cache = caches[cache_db]
            k = str(uuid.uuid1())
            cache.set(k, k, 60)
            return f"{k} - Ok"
        except Exception as e:
            return e

    def cache_keys(self, cache_db='default'):
        try:
            cache = caches[cache_db]
            if cache_db == 'memcached':
                return cache._cache.keys()
            return cache.keys('*')
        except Exception as e:
            return e

    def mq_check_conection(self):
        creds = pika.PlainCredentials(
            username=settings.MQ['username'], password=settings.MQ['password']
        )
        params = pika.ConnectionParameters(
            host=settings.MQ['host'],
            virtual_host=settings.MQ['vhost'],
            credentials=creds
        )
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.basic_publish('', 'my-alphabet-queue', 'abc')
            return "Ok"
        except Exception as e:
            return e

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['redis_save'] = f"redis: save {self.cache_set()}"
        context['redis_keys'] = f"redis: keys {self.cache_keys()}"
        context['memcached_save'] = f"memcached: save {self.cache_set(cache_db='memcached')}"
        context['mq'] = f"mq {self.mq_check_conection()}"
        context['mailhog'] = "Unfortunately, I have no expertise in how to work with mailhog"
        return context
