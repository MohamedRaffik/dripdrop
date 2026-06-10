from app.tasks.app import QueueTask


def test_queue_task_runs_sync_run():
    class SyncTask(QueueTask):
        def run(self):
            return "sync-result"

    assert SyncTask().__call__() == "sync-result"
