def run():
    print("Dummy Runs!!", flush=True)


var_a = 1
import time


def little_sleep(i):
    time.sleep(0.0001)
    # print(f'\r {i} \r', end='')


def wait(i):
    while i:
        little_sleep(i)
        i -= 1


def test():
    wait(20)
