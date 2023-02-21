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
d += e
print(d)

def rec(a, res):
    if a == 10:
        return 21
    else:
        res += rec(a+1, res)

print(rec(a=1, res=[]))