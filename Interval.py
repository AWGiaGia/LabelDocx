

def get_continuous_interval(nums:list):
    assert len(nums) > 0

    result = []
    i = 0
    while i < len(nums):
        j = i
        while j < len(nums) and nums[i] + j - i == nums[j]:
            j += 1
        
        result.append([nums[idx] for idx in range(i,j)])

        i = j

    return result



# 将区间打包为[st_idx1,end_idx1,st_idx2,end_idx2,...st_idxn,end_idxn]的格式
def parse_interval(num:list):
    assert len(num) > 0
    res = []
    interval = get_continuous_interval(num)
    for item in interval:
        res.append(item[0])
        res.append(item[-1])
    return res

if __name__ == '__main__':
    print(get_continuous_interval([1,2,3,5,7,9,10,11,12]))
    print(get_continuous_interval([1,2,3,4,5,6]))
    print(get_continuous_interval([1]))

    print(get_continuous_interval([3,5,7,9]))
    print(get_continuous_interval([3,5,7,11,12,13,14,15]))
