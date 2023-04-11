"""
Summary
-------

This plugin allows easy, variable length summaries directly embedded into the
body of your articles.
"""

from __future__ import unicode_literals

import logging

from pelican import signals
from pelican.generators import ArticlesGenerator, StaticGenerator, PagesGenerator
import re
from bs4 import BeautifulSoup
logger = logging.getLogger(__name__)

def initialized(pelican):
    from pelican.settings import DEFAULT_CONFIG
    DEFAULT_CONFIG.setdefault('SUMMARY_LENGTH_SP','500')
    if pelican:
        pelican.settings.setdefault('SUMMARY_LENGTH_SP','500')

def extract_summary(instance):
    # if summary is already specified, use it
    # if there is no content, there's nothing to do
    if hasattr(instance, '_summary') or 'summary' in instance.metadata:
        instance.has_summary = True
        return
    else:
        instance.has_summary = False

    if not instance._content:
        instance.has_summary = False
        return

    summary_length_sp = int(instance.settings['SUMMARY_LENGTH_SP'])
    content = instance._update_content(instance._content, instance.settings['SITEURL'])
    if not instance.has_summary:
        summary = content[:summary_length_sp]
    else:
        summary = instance.metadata['summary']
    # clear format
    soup = BeautifulSoup(summary, 'lxml')
    asummary = soup.get_text().replace('\n', ' ')
    instance._content = content
    # default_status was added to Pelican Content objects after 3.7.1.
    # Its use here is strictly to decide on how to set the summary.
    # There's probably a better way to do this but I couldn't find it.
    if hasattr(instance, 'default_status'):
        instance.metadata['summary'] = asummary
    else:
        instance._summary = asummary
    instance.has_summary = True

def run_plugin(generators):
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            for article in generator.articles:
                extract_summary(article)
        elif isinstance(generator, PagesGenerator):
            for page in generator.pages:
                extract_summary(page)


def register():
    signals.initialized.connect(initialized)
    try:
        signals.all_generators_finalized.connect(run_plugin)
    except AttributeError:
        # NOTE: This results in #314 so shouldn't really be relied on
        # https://github.com/getpelican/pelican-plugins/issues/314
        signals.content_object_init.connect(extract_summary)
