

f = set()
def test(a): # 239ms for 50*50*50 / 2.78s for 100*100*100
	f = set()
	for x in range(0, a.shape[0] - 1):
		for y in range(0, a.shape[1] - 1):
			for l in zip(a[x,y,:-1], a[x+1,y,:-1], a[x,y+1,:-1], a[x,y,1:]): #label/right/bottom/deep
				for n in l[1:]: f.add((l[0], n))
	return f

def test2d(a): # 239ms for 50*50*50 / 2.78s for 100*100*100
	f = set()
	for x in range(0, a.shape[0] - 1):
			label = a[x,:-1]
			right = a[x+1,:-1]
			bottom = a[x,1:]
			print len(label), len(right), len(bottom)
			for l in zip(label, right, bottom): #label/right/bottom
				for n in l[1:]: f.add((l[0], n))
	return f

def test2(a): # 266ms for 50*50*50 / 2,87s for 100*100*100
	f = []
	for x in range(0, a.shape[0] - 1):
		for y in range(0, a.shape[1] - 1):
			for l in zip(a[x,y,:-1], a[x+1,y,:-1], a[x,y+1,:-1], a[x,y,1:]): #label/right/bottom/deep
				for n in l[1:]: f.append((l[0], n))
	return set(f)


v = list(scipy.random.randint(0, 100, 10000))
def fu(v): # 1.79ms
	f = []
	for x in v[1:]:
		f.append((v[0],x))
	set(f)

v = list(scipy.random.randint(0, 100, 10000))
def fu(v): #1.62ms (using a list as input is faster than arrays)
	f = set()
	for x in v[1:]:
		f.add((v[0],x))

def fun3(a): # 2.63ms (4.1ms)
	for x in range(1, a.shape[0]):
		for l in zip(a[x,:-1],a[x-1,:-1],a[x,1:]): #label/top/right
			pass			
			#print l


l = sc.zeros(5)
def fun0(a, l): # 11.4ms
	for x in range(0, a.shape[0] - 1):
		#print ''
		l[0] = a[x-1,1]
		l[1] = a[x,0]
		l[2] = a[x,1]
		l[3] = a[x,2]
		l[4] = a[x+1,1]
		for y in range(1, a.shape[1] - 1):
			if not 1 == y:
				l[1:3] = l[2:4]
				l[0] = a[x-1,y]
				l[3] = a[x,y+1]
				l[4] = a[x+1,y]
			#print l


n = ndimage.generate_binary_structure(2, 1) # 3*3
l = a[n] # 3*3 intial region
def fun1(a, n, l): # 10.5ms # !The shorter (e.g. uin8) the input data, the better!
	for x in range(1, a.shape[0] - 1):
		#print ''
		if not 1 == x:
			l[0] = a[x-1,1]
			l[1] = a[x,0]
			l[2] = a[x,1]
			l[3] = a[x,2]
			l[4] = a[x+1,1]
		for y in range(1, a.shape[1] - 1):
			if not 1 == y:
				l[1:3] = l[2:4]
				l[0] = a[x-1,y]
				l[3] = a[x,y+1]
				l[4] = a[x+1,y]
			#print l

n = ndimage.generate_binary_structure(2, 1) # 3*3
def fun2(a, n): # 21.7ms
	for x in range(1, a.shape[0] - 1):
		sx = slice(x - 1, x + 2)
		for y in range(1, a.shape[1] - 1):
			region = a[sx, slice(y - 1, y + 2)]
			l = region[n]
			#print l


# data
a = array([[2, 2, 2, 5, 0, 3],
       [2, 2, 2, 0, 0, 0],
       [0, 0, 1, 1, 0, 0],
       [4, 0, 1, 1, 0, 0],
       [0, 0, 0, 0, 1, 0],
       [0, 0, 0, 0, 0, 0]], dtype=uint8)

[[[2, 2, 2, 0, 3],
  [2, 2, 2, 0, 0],
  [0, 0, 1, 0, 0],
  [4, 0, 0, 0, 0]],
 [[2, 2, 2, 0, 3],
  [2, 2, 2, 0, 0],
  [0, 0, 1, 0, 0],
  [4, 0, 0, 0, 0]],
 [[2, 2, 2, 0, 3],
  [2, 2, 2, 0, 0],
  [0, 0, 1, 0, 0],
  [4, 0, 0, 0, 0]]], dtype=uint8)

# expected results
[ 2.  2.  2.  2.  0.]
[ 2.  2.  2.  0.  1.]
[ 5.  2.  0.  0.  1.]
[ 0.  0.  0.  0.  0.]
[ 2.  0.  0.  1.  0.]
[ 2.  0.  1.  1.  1.]
[ 0.  1.  1.  0.  1.]
[ 0.  1.  0.  0.  0.]
[ 0.  4.  0.  1.  0.]
[ 1.  0.  1.  1.  0.]
[ 1.  1.  1.  0.  0.]
[ 0.  1.  0.  0.  1.]
[ 0.  0.  0.  0.  0.]
[ 1.  0.  0.  0.  0.]
[ 1.  0.  0.  1.  0.]
[ 0.  0.  1.  0.  0.]

