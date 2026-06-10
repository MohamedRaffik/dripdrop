from app.tasks.app import QueueTask


def test_queue_task_runs_sync_run():
    class SyncTask(QueueTask):
        def run(self):
            return "sync-result"

    assert SyncTask().__call__() == "sync-result"


def test_queue_task_runs_async_run():
    class AsyncTask(QueueTask):
        async def run(self):
            return "async-result"

    assert AsyncTask().__call__() == "async-result"
