# from argparse import ArgumentParser
#
#
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#
# def sf_task_handle(func):
#     def inner(*args, **kwargs):
#         from processing.providers.aws import AwsSfProvider
#
#         provider = AwsSfProvider()
#
#         try:
#             func(*args, **kwargs)
#         except Exception as e:
#             provider.sf_send_task_failure()
#             raise e
#
#         provider.sf_send_task_success()
#
#     return inner
#
#
