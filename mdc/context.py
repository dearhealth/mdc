# -*- coding: utf-8 -*-
"""
.. module: TODO
    :platform: TODO
    :synopsis: TODO

.. moduleauthor:: Aljosha Friemann a.friemann@automate.wtf
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import time
import uuid
import logging
import threading
import collections

from contextlib import contextmanager

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.ERROR)

logging._mdc = threading.local()
start = time.time()


def get_mdc_fields():
    result = collections.defaultdict(None)
    contexts = vars(logging._mdc)
    for context_id in sorted(contexts, key=lambda x: contexts[x].__creation_time__):
        result.update(**vars(contexts[context_id]))
    return result


@contextmanager
def new_log_context(**kwargs):
    context_id = "mdc-{thread}-{context}".format(
        thread=threading.current_thread().ident, context=uuid.uuid4()
    )

    LOGGER.debug("creating context %s", context_id)

    setattr(logging._mdc, context_id, threading.local())

    context = getattr(logging._mdc, context_id)

    context.__creation_time__ = time.time() - start

    for key, value in kwargs.items():
        setattr(context, key, value)

    try:

        yield context

    finally:

        LOGGER.debug("deleting context %s", context_id)

        try:
            delattr(logging._mdc, context_id)
        except AttributeError:
            LOGGER.warning("context was already deleted %s", context_id)


MDContext = new_log_context
