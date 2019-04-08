# -*- coding: utf-8 -*-
import logging
from threading import Thread, current_thread, Event, Semaphore

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Threadpool(object):

    def __init__(self, workers):
        self.workers = workers
        self.semaphore = Semaphore(workers)
        self.threads = []
        self.stop_event = Event()
        self.stop_event.clear()

    def start_thread(self, target, name, *args, **kwargs):
        if self.stop_event.is_set():
            logger.warning("Stop event set!")
            return

        self.semaphore.acquire()
        thread = Thread(target=self.thread_wrapper, name=name, args=(target, self.stop_event) + args, kwargs=kwargs)
        thread.start()
        self.threads.append(thread)

    def thread_wrapper(self, target, exception_event, *args, **kwargs):
        thread_name = current_thread().name
        logger.debug("Processing domain: {}".format(thread_name))
        try:
            target(*args, **kwargs)
        except TimeoutError:
            logger.warning("Could not fetch url for {}".format(thread_name))
        except Exception:
            exception_event.set()
            logger.exception('unhandled exception in %s', thread_name)
            raise
        finally:
            logger.debug("Finished processing domain: {}".format(thread_name))
            logger.debug('{0} - thread ended'.format(thread_name))
            self.semaphore.release()

    def join_threads(self):
        """End all threads and join them back into the main thread"""
        for thread in self.threads:
            logger.debug("Joining thread {0}".format(thread.name))
            thread.join()
            logger.debug("Thread {0} has ended".format(thread.name))

    def kill(self):
        logger.error("Killing the threadpool")
        self.stop_event.set()
        self.join_threads()
