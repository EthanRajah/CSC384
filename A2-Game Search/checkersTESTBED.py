a = []
b = [1,2,3,4]

a += [b]
print(a)

def test():
    c = [1,2,3]
    return [c]

a += test()
print(a)