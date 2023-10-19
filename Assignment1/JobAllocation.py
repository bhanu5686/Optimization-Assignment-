import graphviz
import random
from docplex.mp.model import Model

class JobAllocation:
	__graph = [] #stores the entire graph
	__vertexMap = {} #stores the end points of each edge
	__edgeMap = {} #stores a unique key for each edge, its id and weight
	__n = 0 #number of vertices
	__e = 0 #number of edges
	__solver = None #cplex
	__graphviz = None #graphviz
	__colors = ["red","blue","green","yellow","magenta","aqua","brown","crimson","coral","darkgoldenrod","darkgreen","darkkhaki","darkorange","gold","orange","lightblue","lightcoral","salmon","khaki","maroon","olive","purple","teal","darkred"]
	__noc = 24
	__colorIndex = 0

	def __init__(self, fileName):
		#read from file
		edgeFiles = open(fileName)
		graphStructure = edgeFiles.readlines()
		self.__n = len(graphStructure)
		edgeFiles.close()
		edges = []
		#store edges in an array
		for i in range(self.__n):
			vertices = graphStructure[i].split(' ')
			for j in range(self.__n):
				if int(vertices[j]) != 0:
					edge = []
					edge.append(i)
					edge.append(j+self.__n)
					edge.append(float(vertices[j]))
					edges.append(edge)

		edgeNo = 0
		for edge in edges: #for each edge
			n1,n2,w = edge[0], edge[1], edge[2]
			self.__graph.append([n1,n2,w]) #append a new edge to the graph
			self.__vertexMap.setdefault(n1, []).append(n2) #add vertices to vertex map
			self.__vertexMap.setdefault(n2, []).append(n1) #add vertices to vertex map
			minN, maxN = 0, 0 #find minimum and maximum out of the two vertices
			if (n1 < n2):
				minN = n1
				maxN = n2
			else:
				minN = n2
				maxN = n1
			key = 1103*minN+1193*maxN #form a unique key
			if key not in self.__edgeMap: #if key is not present in the edge map, add with edge number and weight
				self.__edgeMap.setdefault(key, []).append(edgeNo)
				self.__edgeMap.setdefault(key, []).append(minN)
				self.__edgeMap.setdefault(key, []).append(maxN)
				self.__edgeMap.setdefault(key, []).append(w)
			edgeNo += 1
		self.__e = len(self.__graph)

	def solve(self, type):
		self.__colorIndex = 0
		if (type == 0):
			self.__solver = Model(name='JobAllocationILP')
		elif (type == 1):
			self.__solver = Model(name='JobAllocationLP')

		constNo = 0

		#xe and we
		if (type == 0):
			for i in range(self.__e):
				self.__solver.binary_var(name='x'+str(i)) #add binary variables for each edge
		elif (type == 1):
			for i in range(self.__e):
				self.__solver.continuous_var(name='x'+str(i)) ##add continuous variables for each edge

		#constraints
		for key in self.__vertexMap: #for each vertex
			edges = []
			for value in self.__vertexMap[key]: #for each vertex at the other end of the edge
				minN, maxN = 0, 0 #get the minimum and maximum out of the two
				if (key < value):
					minN = key
					maxN = value
				else:
					minN = value
					maxN = key
				edgeKey = 1103*minN+1193*maxN #form the unique key
				e, n1, n2, w = self.__edgeMap[edgeKey] #get the edge id and weight
				edges.append(self.__solver.get_var_by_name(name='x'+str(e))) #append the constraint variable
			self.__solver.add_constraint(sum(edge for edge in edges) == 1, ctname="c"+str(constNo)) #add the constraint
			constNo += 1

		#objective function
		edges = []
		for key in self.__edgeMap: #for each edge
			e, n1, n2, w = self.__edgeMap[key] #get the edge number and the weight
			edges.append(w*self.__solver.get_var_by_name(name='x'+str(e)))

		self.__solver.set_objective("min",sum(edge for edge in edges))
		if (type == 0):
			print("=============================================")
			print("                ILP solution")
			print("=============================================")
		elif (type == 1):
			print("=============================================")
			print("                 LP solution")
			print("=============================================")
		self.__solver.print_information()
		self.__solver.solve()
		self.__solver.print_solution()

		if (type == 0):
			self.__graphviz = graphviz.Graph('job-allocation', filename='JobAllocationILP')
		elif (type == 1):
			self.__graphviz = graphviz.Graph('job-allocation', filename='JobAllocationLP')

		self.__graphviz.graph_attr['ranksep'] = 'equally'
		c = graphviz.Graph('c0')
		c.attr(rank='same')
		for i in range(self.__n):
			c.node(str(i),label = 'J-'+str(i+1))
		self.__graphviz.subgraph(c)
		c = graphviz.Graph('c1')
		c.attr(rank='same')
		for i in range(self.__n,2*self.__n):
			c.node(str(i),label = 'E-'+str(i-self.__n+1))
		self.__graphviz.subgraph(c)
		for key in self.__edgeMap:
			e, n1, n2, w = self.__edgeMap[key]
			xValue = self.__solver.get_var_by_name(name='x'+str(e))
			if (xValue.solution_value == 1.0):
				self.__graphviz.edge(str(n1),str(n2),label = str(w),color = self.__colors[self.__colorIndex])
				self.__graphviz.node(str(n1),color = self.__colors[self.__colorIndex])
				self.__graphviz.node(str(n2),color = self.__colors[self.__colorIndex])
				self.__colorIndex += 1
				if (self.__colorIndex >= 24):
					self.__colorIndex -= 24
		i,j = 0,1
		while (j < self.__n):
			self.__graphviz.edge(str(i),str(j),color = 'white')
			i = j
			j += 1
		i,j = self.__n,self.__n+1
		while (j < 2*self.__n):
			self.__graphviz.edge(str(i),str(j),color = 'white')
			i = j
			j += 1
		self.__graphviz.render(view=True)


#######################################################
print("=================================================")
print("                 Job Allocation")
print("=================================================")
print("Enter the input file name-")
print("(Write 'random' to generate a random input file)")
fileName = input()
if (fileName == "random"):
	print("Enter the number of vertices-")
	n = int(input())
	file = open("randomInput.dat","w")
	for i in range(n):
		randomVertices = ""
		for j in range(n):
			num = random.randint(25,125)
			randomVertices += str(num)
			randomVertices += " "
		file.writelines(randomVertices+"\n")
	file.close()
	fileName = "randomInput.dat"
jobAlloc = JobAllocation(fileName) #create object
jobAlloc.solve(0) #solve for ILP
jobAlloc.solve(1) #solve for LP