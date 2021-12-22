import asyncio

from starlette.concurrency import run_in_threadpool


class AsyncioWorker():
    def __init__(self) -> None:
        self._tasks: list[asyncio.Task] = []

    def add_job(self, func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            task = asyncio.create_task(func(*args, **kwargs))
        else:
            task = asyncio.create_task(
                run_in_threadpool(func, *args, **kwargs))

        self._tasks.append(task)
        return task

    async def work(self):
        try:
            while True:
                new_tasks = []
                for task in self._tasks:
                    if task.done():
                        new_tasks.append(task)
                self._tasks = new_tasks
                await asyncio.sleep(1)
        except Exception as e:
            for task in self._tasks:
                task.cancel()
            raise Exception(e)


Worker = AsyncioWorker()
