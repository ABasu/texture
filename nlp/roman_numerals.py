# -*- coding: utf-8 -*- 

################################################################################
def roman_to_int(rnum):
    rnum = rnum.upper() + "Z"
    nums = {'M': 1000, 'D': 500, 'C':100, 'L': 50, 'X': 10, 'V': 5, 'I': 1, 'Z':0}
    num_list = []
    for n in rnum:
        num_list.append(nums[n])
    total = 0
    for i, n in enumerate(num_list[:-1]):
        if num_list[i+1] <= num_list[i]:
            total += n
        else:
            total -= n
    return total
