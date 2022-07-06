# R: This script for computer vision calculation. It calculates the size of the
import sys


# R: This function will output the resulting size of the convolutional layer. The input is going to
# R: complicated and like this (sorry long time ago) [padding kernel_size stride padding kernel_size string padding...]:
#
#
#   python3 conv_calc.py [padding kernel_size stride padding kernel_size string padding...]
#
#
def main():
h = int(sys.argv[1])
w = int(sys.argv[2])

convs = list(map(int, sys.argv[3:]))

if len(convs)/3 != int(len(convs)/3):
    raise TypeError('Make sure to enter every value in each layer')

for n in range((len(convs) // 3)):
    p = convs[n*3]
    k = convs[n*3 + 1]
    s = convs[n*3 + 2]

    h = ((h +(2 * p) - k) // s) + 1
    w = ((w +(2 * p) - k) // s) + 1

    print('Convolutional Layer {}\nHeight {} \nWidth {}'.format(n, h, w)) 



