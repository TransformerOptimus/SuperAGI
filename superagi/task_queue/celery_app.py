from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

celery_app.conf.worker_concurrency = 10

@celery_app.task(name="test_function")
def test_fucntion(*args, **kwargs):
    # Implement your function logic here
    c = 0
    print("Inside Celery!")
    while c<1000:
        c = c+1
    print("Done!")


# celery -A celery_app worker --loglevel=info
