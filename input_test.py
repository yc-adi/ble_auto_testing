#!/usr/bin/env python3

in1 = input("input A:")
print(f'input 1 done: {in1}')

in2 = input()
print(f'input 2 done: {in2}')

in3 = input()
print(f'input 3 done: {in3}')
if in3.find("exit") != -1:
    exit(0)
else:
    exit(1)

