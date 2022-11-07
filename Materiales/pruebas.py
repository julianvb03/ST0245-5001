from queue import PriorityQueue

pq = PriorityQueue()
pq.put(87)
pq.put(6)
pq.put(1)
if pq.empty():
    dato = True
else:
    dato = False
print(pq.get())