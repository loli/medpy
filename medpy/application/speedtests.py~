def fun3(a): # 3.17ms
	for x in range(1, a.shape[0] - 1):
		top = a[x-1,1:-1]
		m1 = a[x,0:-2]
		m2 = a[x,1:-1] # label
		m3 = a[x,2:]
		bottom = a[x+1,1:-1]
		for l in zip(top,m1,m2,m3,bottom):
			pass			
			#print l


l = sc.zeros(5)
def fun0(a, l): # 11.4ms
	for x in range(1, a.shape[0] - 1):
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

