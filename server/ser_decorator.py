# -*- coding: utf-8 -*-

"""comment"""  # 文档注释 __doc__

__author__ = 'GARRYHu'

import functools
import threading
import time


def metric(fn):  # 输出函数执行时间
    @functools.wraps(fn)
    def wapper(*args, **kw):
        start = time.time()

        fn(*args, **kw)

        end = time.time()

        print('%s executed in %s ms' % (fn.__name__, end - start))

        return fn(*args, **kw)

    return wapper


def log(text):  # 输出函数调用日志
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)

        return wrapper

    return decorator


def time_limited(timer):
    '''
    一个规定函数执行时间的装饰器
    :param timer:
    :return:
    '''

    def wrapper(func):
        def __wrapper(sock,len):
            # 通过设置守护线程强制规定函数的运行时间
            t = threading.Thread(target=func,args=(sock,len))
            t.setDaemon(True)
            t.start()
            time.sleep(timer)
            if t.is_alive():
                # 若在规定的运行时间未结束守护进程，则主动抛出异常
                raise Exception('Function execution timeout')
            # print time.time()-start_time

        return __wrapper

    return wrapper