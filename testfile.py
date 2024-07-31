from concurrent.futures import ProcessPoolExecutor
from time import sleep

def task2(m):
    while True:
        print('ttttt')
        sleep(2)
def task(message):
    while True:
        print('test')
        sleep(5)

def main():
   executor = ProcessPoolExecutor(5)
   future = executor.submit(task, ("Completed"))
   f = executor.submit(task2, ("Completed"))
   
if __name__ == '__main__':
    main()
