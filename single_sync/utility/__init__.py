import time
from django.conf import settings

def timeit(f):
    def timed(self, *args, **kw):
        if not settings.DEBUG:
            return f(self, *args, **kw)

        ts = time.time()
        result = f(self, *args, **kw)
        te = time.time()
        print('-' * 100)
        print('func:%r  took: %2.4f sec' % \
              (f.__name__, te - ts))
        print('func:%r args:[%r, %r] ' % \
              (f.__name__, args, kw))
        print('-'*100)
        print('\n')
        return result

    return timed
