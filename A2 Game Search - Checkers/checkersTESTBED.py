a = []
b = [1,2,3,4]

a += [b]
print(a)

def test():
    c = [1,2,3]
    return None

a.append(test())
print(a)

c = [[1,2,3], [4,5,6]]
d = []
d += c
e = [[11,22,33],[44,55,66]]
if 1 in e[0]:
    print('yes')

cache = dict()
cache['hi'] = 10
if 'no' not in cache.keys():
    print('worked')