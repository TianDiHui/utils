#!/usr/bin/env python
# -*- coding=utf-8 -*-

# 关闭浏览器缓存
# https://stackoverflow.com/questions/2095520/fighting-client-side-caching-in-django
# This approach (slight modification of L. De Leo's solution) with a custom middleware has worked well for me as a site wide solution:
from django.utils.cache import add_never_cache_headers


class DisableClientSideCachingMiddleware(object):
    def process_response(self, request, response):
        add_never_cache_headers(response)
        return response