1: # Artificial Intelligence Algorithms
2: 
3: ## Basic Search
4: 
5: ![img-0.jpeg](img-0.jpeg)
6: 
7: Instructor: Farah AIT SALAHT
8: 
9: ESILV- Leonard de Vinci Graduated School of Engineering
10: # Previous session
11: 
12: ## What did we learn:
13: 
14: - Introduction to Artificial Intelligence for problem solving and decision-making and intelligent agents
15: - What makes an Agents?
16: 
17: ![img-1.jpeg](img-1.jpeg)
18: # What makes an Agents?
19: 
20: - Example: Vacuum-cleaner world – Roomba!
21: 
22: ![img-2.jpeg](img-2.jpeg)
23: 
24: (dirt)
25: 
26: - Percepts: location and contents, e.g., [A,Dirty]
27: - Actions: Left, Right, Suck
28: 
29: - Example of an agent function:
30: 
31: |  Percept sequence | Action  |
32: | --- | --- |
33: |  [A, Clean] | Right  |
34: |  [A, Dirty] | Suck  |
35: |  [B, Clean] | Left  |
36: |  [B, Dirty] | Suck  |
37: |  [A, Clean], [A, Clean] | Right  |
38: |  [A, Clean], [A, Dirty] | Suck  |
39: |  ⋮ | ⋮  |
40: # What makes one rational?
41: 
42: A rational agent always acts to **maximize the utility function**, given current state/percept
43: 
44: 
45: # What makes one rational?
46: 
47: How do we choose the best sequence of actions?
48: 
49: This involves defining the
50: « search problems »
51: # Search process?
52: 
53: 
54: # Information Retrieval vs. Search
55: 
56: 
57: 
58: ![img-6.jpeg](img-6.jpeg)
59: 
60: ![img-7.jpeg](img-7.jpeg)
61: 
62: ![img-8.jpeg](img-8.jpeg)
63: # Definition of Search
64: 
65: ## Finding a (best) sequence of actions to solve a problem
66: 
67: - We will consider the problem of designing goal-based agents in
68:   - Deterministic
69:   - Fully observable
70:   - Discret
71:   - Known environments.
72: # Today
73: 
74: ## Solving problems by searching
75: 
76: - Problem-solving agents
77: - Search Problems
78: - Uninformed Search Methods
79:   1. Depth-First Search
80:   2. Breadth-First Search
81:   3. Iterative Deepening Search
82:   4. Uniform-Cost Search
83: 
84: ![img-9.jpeg](img-9.jpeg)
85: # Agents that Plan ahead
86: 
87: - An agent enjoying a touring vacation in United States.
88: - He is in the city of Boston and must find his friend in San Francisco.
89: - Which route to follow?
90: - We assume that our agent always have access to information about the world (the map).
91: 
92: ![img-10.jpeg](img-10.jpeg)
93: # Building a Problem-Solving Agent
94: 
95: - What goal / problem does the agent try to achieve / solve?
96: - What knowledge does the agent need?
97: - What actions does the agent need to do?
98: # Agents that Plan ahead
99: 
100: To find a way to reach the destination (goal), the agent can follow this four-phase problem-solving process:
101: 
102: ## 1. Goal formulation:
103: 
104: - How do you describe the goal?
105:   - as a problem to be solved
106:   - as a situation to be reached
107:   - as a set of properties to be acquired.
108: - **Our example:** The agent adopts the **goal** of reaching San Francisco.
109: - Goals organize behavior by limiting the objectives and hence the actions to be considered.
110: 
111: ![img-11.jpeg](img-11.jpeg)
112: # Agents that Plan ahead
113: 
114: To find a way to reach the destination (goal), the agent can follow this four-phase problem-solving process:
115: 
116: ## 2. Problem formulation:
117: 
118: - The agent devises a description of the states and actions necessary to reach the goal
119: - Define an abstract model of the relevant part of the world.
120:   - Removing detail from a representation while retaining relevant information for solving the problem.
121: - **Example:**
122:   - consider the actions of traveling from one city to an adjacent city
123:   - the state of the world that will change due to an action is the current city.
124: 
125: ![img-12.jpeg](img-12.jpeg)
126: 
127: Key West
128: # Agents that Plan ahead
129: 
130: To find a way to reach the destination (goal), the agent can follow this four-phase problem-solving process:
131: 
132: ## 3. Search:
133: 
134: - Before taking any action in the real world, the agent simulates sequences of actions in its model, searching until it finds a sequence of actions that reaches the goal. Such a sequence is called a **solution**.
135: 
136: ## 4. Execution:
137: 
138: The agent can now execute the actions in the solution, one at a time.
139: 
140: ![img-13.jpeg](img-13.jpeg)
141: # Today
142: 
143: ## Solving problems by searching
144: 
145: - Problem-solving agents
146: - Search Problems
147: - Uninformed Search Methods
148:   1. Depth-First Search
149:   2. Breadth-First Search
150:   3. Iterative Deepening Search
151:   4. Uniform-Cost Search
152: 
153: ![img-14.jpeg](img-14.jpeg)
154: # Search problems
155: 
156: ## Search: sequence of actions to achieve goal.
157: 
158: - Search algorithm takes a problem as input and returns a solution in the form of a sequence of actions.
159: - Once solution is found, actions it recommends are executed.
160: 
161: Formulate -> Search -> Actions
162: 
163: - When executing, the agent is running open loop, i.e., it ignores percepts since it already knows in advance what they will be.
164: # Problem formulation
165: 
166: A search problem can be defined formally as follows:
167: 
168: a) **State space** — The set of all possible states in the environment.
169: 
170: b) **Initial state** — The starting state of the agent. Example: *Boston*.
171: 
172: c) **Goal States (Goal Test)** — Desired end states the agent aims to reach. **Example:** San Francisco.
173: 
174: d) **Actions Available to the Agent** — Possible moves or decisions the agent can make. Given a state $s$, $ACTIONS(s)$ returns a finite set of actions that can be executed in $s$. Each of these actions is considered applicable in $s$.
175: 
176: **Example:** $ACTIONS(Boston) = \{To\_KeyWest, To\_NewYork, To\_Chicago\}$
177: # Problem formulation
178: 
179: A search problem can be defined formally as follows:
180: 
181: e) A **transition model** — describes what each action does. $RESULT(s, a)$ returns the state that results from doing action $a$ in state $s$.
182: 
183: For example, $RESULT(Boston, To\_Chicago) = Chicago$.
184: 
185: f) **Action cost function** — denoted by $ACTION-COST(s, a, s')$, gives a numeric cost of applying action $a$ in state $s$ to reach state $s'$.
186: 
187: - A problem-solving agent should use a cost function that reflects its own performance measure;
188: - For example, for route-finding agents, the cost of an action might be the length in kilometers, or it might be the time it takes to complete the action, etc.
189: # Problem formulation
190: 
191: - The state space can be represented as a **graph** in which the vertices are states and the directed edges between them are actions.
192: 
193: - In a **state space graph**, each state occurs only once!
194: - In case of an undirected graph, each edge indicates two actions, one in each direction.
195: 
196: - A sequence of actions forms a **path**
197: 
198: - A **solution** is a path from the initial state to a goal state.
199: 
200: - We assume that action costs are additive; that is, the total cost of a path is the sum of the individual action costs.
201: 
202: - An **optimal solution** has the lowest path cost among all solutions.
203: 
204: - In this course, we assume that all action costs will be positive, to avoid certain complications.
205: 
206: ![img-15.jpeg](img-15.jpeg)
207: # Problem formulation
208: 
209: ![img-16.jpeg](img-16.jpeg)
210: 
211: ![img-17.jpeg](img-17.jpeg)
212: 
213: - State space: Cities
214: - Initial state: Boston
215: - Goal test: is state == San Francisco?
216: - Actions: Go to adjacent city
217: - Action cost: e.g., cost = distance
218: - Transition model: RESULT(Boston, To_Chicago) = Chicago
219:   RESULT(Boston, To_New York) = New York
220:   RESULT(Chicago, To_Danver) = Denver
221:   ...
222: - Example of path: {NewYork, Nashville, Austin}
223: - Solutions:
224:   - {Boston, NewYork, Nashville, Austin, Phoenix, SanFrancisco}
225:   - {Boston, Chicago, SanFrancisco}
226:   ...
227: - Optimal solution?? Depends on the objective
228: # Problem formulation
229: 
230: ## Other example
231: 
232: ![img-18.jpeg](img-18.jpeg)
233: 
234: A vacuum-cleaner world with just two locations.
235: 
236: ## State space
237: 
238: ![img-19.jpeg](img-19.jpeg)
239: 
240: ![img-20.jpeg](img-20.jpeg)
241: 
242: ![img-21.jpeg](img-21.jpeg)
243: 
244: ![img-22.jpeg](img-22.jpeg)
245: 
246: ![img-23.jpeg](img-23.jpeg)
247: 
248: 
249: 
250: ![img-25.jpeg](img-25.jpeg)
251: 
252: ![img-26.jpeg](img-26.jpeg)
253: 
254: ## Goal State
255: 
256: ![img-27.jpeg](img-27.jpeg)
257: 
258: ![img-28.jpeg](img-28.jpeg)
259: 
260: ![img-29.jpeg](img-29.jpeg)
261: 
262: ![img-30.jpeg](img-30.jpeg)
263: 
264: ![img-31.jpeg](img-31.jpeg)
265: 
266: ![img-32.jpeg](img-32.jpeg)
267: 
268: ![img-33.jpeg](img-33.jpeg)
269: 
270: ![img-34.jpeg](img-34.jpeg)
271: 
272: The eight possible states of the vacuum world
273: 
274: States 7 and 8 are goal states.
275: # Problem formulation
276: 
277: Example
278: 
279: ![img-35.jpeg](img-35.jpeg)
280: 
281: A vacuum-cleaner world with just two locations.
282: 
283: Initial state
284: 
285: ![img-36.jpeg](img-36.jpeg)
286: 
287: ![img-37.jpeg](img-37.jpeg)
288: 
289: ![img-38.jpeg](img-38.jpeg)
290: 
291: ![img-39.jpeg](img-39.jpeg)
292: 
293: 
294: 
295: ![img-41.jpeg](img-41.jpeg)
296: 
297: ![img-42.jpeg](img-42.jpeg)
298: 
299: ![img-43.jpeg](img-43.jpeg)
300: 
301: Actions
302: 
303: - Right (R)
304: - Left (L)
305: - Suck (S)
306: 
307: Any state can be designated as the initial state.
308: # Problem formulation
309: 
310: ## Example
311: 
312: ![img-44.jpeg](img-44.jpeg)
313: 
314: A vacuum-cleaner world with just two locations.
315: 
316: ## Transition model
317: 
318: - **Suck** removes any dirt from the agent's cell;
319: - **Right** moves the agent one cell in the right direction, unless it hits a wall, in which case the action has no effect.
320: - **Left** moves the agent one cell in the left direction, unless it hits a wall, in which case the action has no effect.
321: 
322: ## Action cost
323: 
324: - Each action costs 1.
325: # Problem formulation
326: 
327: Example
328: 
329: ![img-45.jpeg](img-45.jpeg)
330: 
331: A vacuum-cleaner world with just two locations.
332: 
333: State space graph
334: 
335: ![img-46.jpeg](img-46.jpeg)
336: 
337: - Example of path:
338: {R, S, R, S, L}, From initial state 1
339: - Example of solution:
340: {S, L, S, R, S}, From initial state 1
341: - Example of optimal solution:
342: {S, R, S}, From initial state 1
343: # Problem Formulation involves Abstraction
344: 
345: ## Example: Missionaries and Cannibals
346: 
347: ![img-47.jpeg](img-47.jpeg)
348: 
349: - 3 missionaries and 3 cannibals on left side
350: - Boat holds 1 or 2 people
351: - Never leave missionaries outnumbered by cannibals
352: - **States:**
353:   (# cannibals, # missionaries, # boats) on left side of river
354: - **Starting state / Goal state:**
355:   - (3,3,1) / (0,0,0)
356: - **Actions:**
357:   - Remove up to 2 people to other side and the resulting state is safe
358: - **Path cost:** number of crossing
359: # Problem formulation
360: 
361: - The process of removing detail from a representation is called *abstraction*.
362: - A good problem formulation has the right level of detail.
363: - The abstraction is *valid* if we can elaborate any abstract solution into a solution in the more detailed world;
364:   - a sufficient condition is that for every detailed state that is “in Boston,” there is a detailed path to some state that is “in Key west,” and so on.
365: - The abstraction is *useful* if carrying out each of the actions in the solution is easier than the original problem; in our case, the action “drive from Boston to Key West” can be carried out without further search or planning by a driver with average skill.
366: # How to Search
367: 
368: Given:
369: 
370: - Initial state
371: - Actions
372: - Transition model
373: - Goal state
374: - Path cost
375: 
376: 
377: 
378: How do we find a solution (best solution)?
379: # How to Search
380: 
381: ## Generating action sequences
382: 
383: ![img-49.jpeg](img-49.jpeg)
384: 
385: ![img-50.jpeg](img-50.jpeg)
386: 
387: The search strategy determines which state to expand next.
388: # Search Tree
389: 
390: - A sequences of actions and their outcomes
391: - The root node corresponds to the starting state
392: - The children of a node correspond to the successor states of that node's state
393: - A path through the tree corresponds to a sequence of actions
394:   - A solution is a path ending in the goal state
395: - **Nodes vs. states**
396:   - A state is a representation of the world, while a **node** is a data structure that is part of the search tree
397:     - Node keeps track of a **state description**, a **parent node** (the node that generated this node), an **action** (the action that was applied to the parent to generate this node), a **path cost** (the cost of the path from the start state to this state), **depth** (number of steps in the path from the start state), and possibly other info.
398: - For most problems, we can never actually build the whole tree
399: 
400: ![img-51.jpeg](img-51.jpeg)
401: # State Space Graphs vs. Search Trees
402: 
403: ## State Space Graph
404: 
405: ![img-52.jpeg](img-52.jpeg)
406: 
407: State : e
408: 
409: Each NODE in the
410: search tree is an
411: entire PATH in the
412: state space graph.
413: 
414: ## Search Tree
415: 
416: ![img-53.jpeg](img-53.jpeg)
417: 
418: Node: (e, [S,d,e], 2,...)
419: 
420: Node: (e, [S,e], 1,...)
421: 
422: Node: (Current state, path from initial state, cost, depth...)
423: # Search tree process
424: 
425: - Begin at the start state and **expand** it by making a list of all possible successor states
426: - Maintain a **frontier** or a list of unexpanded states
427: - At each step, pick a state from the frontier to expand
428: - Keep going until you reach a goal state
429: - **Objective:** *Try to expand as few states as possible*
430: 
431: ![img-54.jpeg](img-54.jpeg)
432: # Tree Search example
433: 
434: ![img-55.jpeg](img-55.jpeg)
435: 
436: |  expended node | Frontier  |
437: | --- | --- |
438: |   | {S}  |
439: |  S not goal | {d,e,p}  |
440: |  d not goal | {e,p,b,c,e}  |
441: |  e not goal | {e,p,b,c,h,r}  |
442: |  r not goal | {e,p,b,c,h,f}  |
443: |  f not goal | {e,p,b,c,h,c,G}  |
444: |  G is goal | {e,p,b,c,h,c}  |
445: 
446: ![img-56.jpeg](img-56.jpeg)
447: # Quiz: State Space Graphs vs. Search Trees
448: 
449: Consider this 4-state graph:
450: 
451: ![img-57.jpeg](img-57.jpeg)
452: 
453: How big is its search tree (from $s$)?
454: 
455: ![img-58.jpeg](img-58.jpeg)
456: 
457: ![img-59.jpeg](img-59.jpeg)
458: 
459: Important: Lots of repeated structure in the search tree!
460: # Tree search algorithm
461: 
462: ## Remark — Handle repeated states
463: 
464: - Every time you **expand a node**, add that state to the **explored set**; do not put explored states on the frontier again
465: - Every time you add a node to the frontier, check whether it already exists in the frontier with a higher path cost, and if yes, replace that node with the new one
466: - This approach is called **Graph search**
467: # General Graph Search
468: 
469: Consider this 4-state graph:
470: 
471: ![img-60.jpeg](img-60.jpeg)
472: 
473: How big is its graph search (from s)?
474: 
475: ![img-61.jpeg](img-61.jpeg)
476: # Tree search vs. Graph search
477: 
478: ## General Tree Search
479: 
480: **function TREE-SEARCH(problem) returns** a solution, or failure
481: 
482: initialize the **frontier** using the initial state of **problem**
483: 
484: **loop do**
485: 
486: if the **frontier** is empty **then return** failure
487: 
488: choose a leaf **node** and remove it from the **frontier**
489: 
490: if the **node** contains a goal state **then return** the corresponding solution
491: 
492: **expand** the chosen **node**, adding the resulting **nodes** to the **frontier**
493: 
494: **VS.**
495: 
496: ## General Graph Search
497: 
498: **function GRAPH-SEARCH(problem) returns** a solution, or failure
499: 
500: initialize the **frontier** using the initial state of **problem**
501: 
502: initialize the **explored set** to be empty
503: 
504: **loop do**
505: 
506: if the **frontier** is empty **then return** failure
507: 
508: choose a leaf **node** and remove it from the **frontier**
509: 
510: if the **node** contains a goal state **then return** the corresponding solution
511: 
512: add the **node** to the **explored set**
513: 
514: **expand** the chosen **node**, adding the resulting **nodes** to the **frontier**
515: 
516: but only if the **node** is not already in the **frontier** or **explored set**
517: # Search algorithm
518: 
519: **Main question:** which frontier nodes to explore? How to expand as few nodes as possible, while achieving the goal?
520: 
521: - **Search Strategy**
522:   - A search strategy determines the order in which nodes are expanded.
523: 
524: ![img-62.jpeg](img-62.jpeg)
525: # Properties of Search Methods
526: 
527: Strategies are evaluated along the following criteria:
528: 
529: - ▶ **Completeness:** is the strategy guaranteed to find a solution when there is one?
530: - ▶ **Time Complexity:** how long does it take to find a solution?
531: - ▶ **Space Complexity:** how much memory does it require to perform the search?
532: - ▶ **Optimality:** Does the strategy find the best-quality solution when more than one solution exists?
533: 
534: • Time and space complexity are measured in terms of :
535: 
536: - • $b$ is the branching factor
537: - • $m$ is the maximum depth
538: - • solutions at various depths
539: 
540: • Number of nodes in entire tree?
541: 
542: • $1 + b + b^2 + \dots b^m = O(b^m)$
543: 
544: ![img-63.jpeg](img-63.jpeg)
545: # Search Strategies
546: 
547: ???
548: 
549: 
550: 
551: What kinds of search algorithms are there?
552: # Search Algorithms
553: 
554: • Uninformed search algorithms
555: 
556: - Have no knowledge other the problem definition
557: - Has a start state
558: - Will recognize the goal state
559: 
560: • Informed search algorithms:
561: 
562: - Finds the solution efficiently
563: - Leverage information about the environment
564: - Use a heuristics - An under-estimate of cost to reach the goal
565: - Or path cost - Distance traveled to current state
566: 
567: ![img-65.jpeg](img-65.jpeg)
568: # Today
569: 
570: ## Solving problems by searching
571: 
572: - Problem-solving agents
573: - Search Problems
574: - **Uninformed Search Methods**
575:   1. Depth-First Search
576:   2. Breadth-First Search
577:   3. Iterative Deepening Search
578:   4. Uniform-Cost Search
579: 
580: 
581: # Uninformed search strategies
582: 
583: - **Uninformed search** also known as unguided search, blind search, or brute-force search is a search methodology that has no additional information about the domain of the problem apart from the representation of the problem which is usually a tree.
584:   - Can only traverse state space blindly in hope of somehow hitting a goal state at some point
585: - **Uninformed search algorithms:**
586:   - Depth-first Search
587:   - Breadth-first Search
588:   - Iterative deepening search
589:   - Uniform Cost Search
590: # Today
591: 
592: ## Solving problems by searching
593: 
594: - Problem-solving agents
595: - Search Problems
596: - Uninformed Search Methods
597: 1. Depth-First Search
598: 2. Breadth-First Search
599: 3. Iterative Deepening Search
600: 4. Uniform-Cost Search
601: 
602: 
603: # 1. Depth-First Search
604: 
605: Depth-First Search (DFS):
606: 
607: - Always expand node at the deepest level of the tree, e.g., one of the most recently generated nodes
608: - When hit a dead-end, backtrack to last choice
609: - Frontier can be maintained as a last-in first-out (LIFO) queue (aka. a stack).
610: - The elements are added to the stack one at a time.
611: - The one selected and taken off the frontier at any time is the last element that was added.
612: 
613: ![img-68.jpeg](img-68.jpeg)
614: # 1. Depth-First Search Example
615: 
616: DFS Search(problem, stack )
617: 
618: # of nodes tested: 0, expanded: 0
619: 
620: |  Explored node | Frontier  |
621: | --- | --- |
622: |   | {(S, path:[S])}  |
623: 
624: **Strategy:** expand a deepest node first
625: 
626: **Implementation:** Frontier is a LIFO stack
627: 
628: State Space Graph
629: 
630: ![img-69.jpeg](img-69.jpeg)
631: 
632: Graph Search
633: # 1. Depth-First Search Example
634: 
635: DFS Search(problem, stack )
636: 
637: # of nodes tested: 0, expanded: 0
638: 
639: |  Explored node | Frontier  |
640: | --- | --- |
641: |   | {(S, path:[S])}  |
642: |  S not goal |   |
643: 
644: State Space Graph
645: 
646: ![img-70.jpeg](img-70.jpeg)
647: 
648: Graph Search
649: 
650: ![img-71.jpeg](img-71.jpeg)
651: # 1. Depth-First Search Example
652: 
653: DFS Search(problem, stack )
654: 
655: # of nodes tested: 1, expanded: 1
656: 
657: |  Explored node | Frontier  |
658: | --- | --- |
659: |   | {(S, path:[S])}  |
660: |  S not goal | {(C, path: [S,C]), (B, path: [S,B]), (A, path: [S,A])}  |
661: 
662: State Space Graph
663: 
664: ![img-72.jpeg](img-72.jpeg)
665: 
666: Graph Search
667: 
668: ![img-73.jpeg](img-73.jpeg)
669: # 1. Depth-First Search Example
670: 
671: DFS Search(problem, stack )
672: 
673: # of nodes tested: 2, expanded: 2
674: 
675: |  Explored node | Frontier  |
676: | --- | --- |
677: |   | {(S, path:[S])}  |
678: |  S not goal | {(C, path: [S,C]), (B, path: [S,B]), (A, path: [S,A])}  |
679: |  A not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (D, path: [S,A,E])}  |
680: 
681: State Space Graph
682: 
683: ![img-74.jpeg](img-74.jpeg)
684: 
685: Graph Search
686: 
687: ![img-75.jpeg](img-75.jpeg)
688: # 1. Depth-First Search Example
689: 
690: DFS Search(problem, stack )
691: 
692: # of nodes tested: 3, expanded: 3
693: 
694: |  Explored node | Frontier  |
695: | --- | --- |
696: |   | {(S, path:[S])}  |
697: |  S not goal | {(C, path: [S,C]), (B, path: [S,B]), (A, path: [S,A])}  |
698: |  A not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (D, path: [S,A,E])}  |
699: |  D not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (H, path: [S,A,D,H])}  |
700: 
701: State Space Graph
702: 
703: ![img-76.jpeg](img-76.jpeg)
704: 
705: Graph Search
706: 
707: ![img-77.jpeg](img-77.jpeg)
708: # 1. Depth-First Search Example
709: 
710: DFS Search(problem, stack )
711: 
712: # of nodes tested: 4, expanded: 3
713: 
714: |  Explored node | Frontier  |
715: | --- | --- |
716: |   | {S}  |
717: |  S not goal | {C, B, A}  |
718: |  A not goal | {C,B, E, D}  |
719: |  D not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (H, path: [S,A,D,H])}  |
720: |  H not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E])} **no expand**  |
721: 
722: State Space Graph
723: 
724: ![img-78.jpeg](img-78.jpeg)
725: 
726: Graph Search
727: 
728: ![img-79.jpeg](img-79.jpeg)
729: # 1. Depth-First Search Example
730: 
731: DFS Search(problem, stack )
732: 
733: # of nodes tested: 4, expanded: 3
734: 
735: |  Explored node | Frontier  |
736: | --- | --- |
737: |   | {S}  |
738: |  S not goal | {C, B, A}  |
739: |  A not goal | {C,B, E, D}  |
740: |  D not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (H, path: [S,A,D,H])}  |
741: |  H not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E])}  |
742: 
743: State Space Graph
744: 
745: ![img-80.jpeg](img-80.jpeg)
746: 
747: Graph Search
748: 
749: ![img-81.jpeg](img-81.jpeg)
750: # 1. Depth-First Search Example
751: 
752: DFS Search(problem, stack )
753: 
754: # of nodes tested: 4, expanded: 3
755: 
756: |  Explored node | Frontier  |
757: | --- | --- |
758: |   | {S}  |
759: |  S not goal | {C, B, A}  |
760: |  A not goal | {C,B, E, D}  |
761: |  D not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (H, path: [S,A,D,H])}  |
762: |  H not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E])}  |
763: 
764: State Space Graph
765: 
766: ![img-82.jpeg](img-82.jpeg)
767: 
768: Graph Search
769: 
770: ![img-83.jpeg](img-83.jpeg)
771: # 1. Depth-First Search Example
772: 
773: DFS Search(problem, stack )
774: 
775: # of nodes tested: 5, expanded: 4
776: 
777: |  Explored node | Frontier  |
778: | --- | --- |
779: |   | {S}  |
780: |  S not goal | {C, B, A}  |
781: |  A not goal | {C,B, E, D}  |
782: |  D not goal | {C, B, E, H}  |
783: |  H not goal | {C, B, E}  |
784: |  E not goal | {(C, path: [S,C]), (B, path: [S,B]), (G, path: [S,A,E, G])}  |
785: 
786: State Space Graph
787: 
788: ![img-84.jpeg](img-84.jpeg)
789: 
790: Graph Search
791: 
792: ![img-85.jpeg](img-85.jpeg)
793: # 1. Depth-First Search Example
794: 
795: DFS Search(problem, stack )
796: 
797: # of nodes tested: 6, expanded: 4
798: 
799: |  Explored node | Frontier  |
800: | --- | --- |
801: |   | {S}  |
802: |  S not goal | {C, B, A}  |
803: |  A not goal | {C,B, E, D}  |
804: |  D not goal | {C, B, E, H}  |
805: |  H not goal | {C, B, E}  |
806: |  E not goal | {C, B, G}  |
807: |  **G is goal** | **Stop**  |
808: 
809: Expansion order: (S, A, D, H, E, G)
810: 
811: State Space Graph
812: 
813: ![img-86.jpeg](img-86.jpeg)
814: 
815: Path: S, A, E, G
816: Cost: 15
817: 
818: Graph Search
819: 
820: ![img-87.jpeg](img-87.jpeg)
821: # 1. Depth-First Search
822: 
823: **Depth-first search:** In depth-first search, the frontier acts like a last-in first-out queue (a stack). The elements are added to the stack one at a time. The one selected and taken off the frontier at any time is the last element that was added.
824: 
825: 
826: 
827: ![img-89.jpeg](img-89.jpeg)
828: 
829: ![img-90.jpeg](img-90.jpeg)
830: # 1. Depth-First Search Example
831: 
832: ## Depth-First Search algorithm
833: 
834: **function** DEPTH-FIRST-SEARCH( *problem* ) **returns** a solution, or failure
835: 
836: *node* ← a node with STATE = *problem*.INITIAL-STATE, PATH-COST = 0
837: 
838: **if** *problem*.GOAL-TEST( *node*.STATE) **then return** SOLUTION( *node* )
839: 
840: *frontier* ← a LIFO queue with *node* as the only element
841: 
842: *explored* ← an empty set
843: 
844: **loop do**
845: 
846: **if** EMPTY?( *frontier* ) **then return** failure
847: 
848: *node* ← POP( *frontier* ) /* chooses the deepest node in *frontier* */
849: 
850: add *node*.STATE to *explored*
851: 
852: **for each** *action* **in** *problem*.ACTIONS( *node*.STATE) **do**
853: 
854: *child* ← CHILD-NODE( *problem*, *node*, *action* )
855: 
856: **if** *child*.STATE is not in *explored* or *frontier* **then**
857: 
858: **if** *problem*.GOAL-TEST( *child*.STATE) **then return** SOLUTION( *child* )
859: 
860: *frontier* ← INSERT( *child*, *frontier* )
861: # 1. DFS Properties
862: 
863: - What nodes DFS expand?
864: 
865: - Some left prefix of the tree.
866: - Could process the whole tree!
867: - If $m$ is finite, takes time $O(b^m)$
868: 
869: - How much space does the fringe take?
870: 
871: - Only has siblings on path to root, so $O(bm)$, i.e., linear space!
872: 
873: - Is it complete?
874: 
875: - $m$ could be infinite, so only if we prevent cycles (more later)
876: - Complete in finite spaces
877: 
878: - Is it optimal?
879: 
880: - No, it finds the “leftmost” solution, regardless of depth or cost
881: 
882: ![img-91.jpeg](img-91.jpeg)
883: 
884: ![img-92.jpeg](img-92.jpeg)
885: # Today
886: 
887: ## Solving problems by searching
888: 
889: - Problem-solving agents
890: - Search Problems
891: - Uninformed Search Methods
892:   1. Depth-First Search
893:   2. Breadth-First Search
894:   3. Iterative Deepening Search
895:   4. Uniform-Cost Search
896: 
897: 
898: ## 2. Breadth-First Search
899: 
900: Breadth-First Search (BFS):
901: 
902: - Nodes are expanded in the same order in which they are generated.
903: - Frontier can be maintained as a First-In, First-Out (FIFO) queue. Thus, the path that is selected from the frontier is the one that was added earliest.
904: - This approach implies that the paths from the start node are generated in order of the number of arcs in the path.
905: - One of the paths with the fewest arcs is selected at each stage.
906: 
907: BFS
908: Looking wide before looking deep
909: 
910: 
911: 
912: ![img-95.jpeg](img-95.jpeg)
913: 
914: Queue:
915: 
916: ![img-96.jpeg](img-96.jpeg)
917: ## 2. Breadth-First Search Example
918: 
919: BFS_Search(problem, queue )
920: 
921: # of nodes tested: 0, expanded: 0
922: 
923: |  expnd. node | node list  |
924: | --- | --- |
925: |   | {(S, path:[S])}  |
926: 
927: Strategy: expand a shallowest node first
928: 
929: Implementation: Fringe/Frontier is a FIFO queue
930: 
931: State Space Graph
932: 
933: ![img-97.jpeg](img-97.jpeg)
934: 
935: Graph Search
936: ## 2. Breadth-First Search Example
937: 
938: BFS_Search(problem, queue )
939: 
940: # of nodes tested: 1, expanded: 1
941: 
942: |  Explored node | node list  |
943: | --- | --- |
944: |   | {(S, path:[S])}  |
945: |  S not goal | {(A, path:[S,A]), (B, path:[S,B]), (C, path:[S,C])}  |
946: 
947: State Space Graph
948: 
949: ![img-98.jpeg](img-98.jpeg)
950: 
951: Graph Search
952: 
953: ![img-99.jpeg](img-99.jpeg)
954: ## 2. Breadth-First Search Example
955: 
956: BFS_Search(problem, queue )
957: 
958: # of nodes tested: 2, expanded: 2
959: 
960: |  Explored node | node list  |
961: | --- | --- |
962: |   | {(S, path:[S])}  |
963: |  S not goal | {(A, path:[S,A]), (B, path:[S,B]), (C, path:[S,C])}  |
964: |  A not goal | {(B, path:[S,B]), (C, path:[S,C]), (D, path:[S,A,D]), (E, path:[S,A,E])}  |
965: 
966: State Space Graph
967: 
968: ![img-100.jpeg](img-100.jpeg)
969: 
970: Graph Search
971: 
972: ![img-101.jpeg](img-101.jpeg)
973: ## 2. Breadth-First Search Example
974: 
975: BFS_Search(problem, queue )
976: 
977: # of nodes tested: 3, expanded: 3
978: 
979: |  Explored node | node list  |
980: | --- | --- |
981: |   | {(S, path:[S])}  |
982: |  S not goal | {(A, path:[S,A]), (B, path:[S,B]), (C, path:[S,C])}  |
983: |  A not goal | {(B, path:[S,B]), (C, path:[S,C]), (D, path:[S,A,D]), (E, path:[S,A,E])}  |
984: |  B not goal | {(C, path:[S,C]), (D, path:[S,A,D]), (E, path:[S,A,E]), (G, path:[S,B,G])}  |
985: 
986: State Space Graph
987: 
988: ![img-102.jpeg](img-102.jpeg)
989: 
990: Graph Search
991: 
992: ![img-103.jpeg](img-103.jpeg)
993: ## 2. Breadth-First Search Example
994: 
995: BFS_Search(problem, queue )
996: 
997: # of nodes tested: 4, expanded: 4
998: 
999: |  Explored node | node list  |
1000: | --- | --- |
1001: |   | {S}  |
1002: |  S not goal | {A, B, C}  |
1003: |  A not goal | {B, C, D, E}  |
1004: |  B not goal | {C, D, E, G}  |
1005: |  C not goal | {(D, path:[S,A,D]), (E, path:[S,A,E]), (G, path:[S,B,G]), **(F, path:[S,C,F])**}  |
1006: 
1007: State Space Graph
1008: 
1009: ![img-104.jpeg](img-104.jpeg)
1010: 
1011: Graph Search
1012: 
1013: ![img-105.jpeg](img-105.jpeg)
1014: ## 2. Breadth-First Search Example
1015: 
1016: BFS_Search(problem, queue )
1017: 
1018: # of nodes tested: 5, expanded: 5
1019: 
1020: |  Explored node | node list  |
1021: | --- | --- |
1022: |   | {S}  |
1023: |  S not goal | {A, B, C}  |
1024: |  A not goal | {B, C, D, E}  |
1025: |  B not goal | {C, D, E, G}  |
1026: |  C not goal | {D, E, G, F}  |
1027: |  D not goal | {(E, path:[S,A,E]), (G, path:[S,B,G]), (F, path:[S,C,F]), (H, path:[S,A,D,H])}  |
1028: 
1029: State Space Graph
1030: 
1031: ![img-106.jpeg](img-106.jpeg)
1032: 
1033: Graph Search
1034: 
1035: ![img-107.jpeg](img-107.jpeg)
1036: ## 2. Breadth-First Search Example
1037: 
1038: BFS_Search(problem, queue )
1039: 
1040: # of nodes tested: 6, expanded: 6
1041: 
1042: |  Explored node | node list  |
1043: | --- | --- |
1044: |   | {S}  |
1045: |  S not goal | {A, B, C}  |
1046: |  A not goal | {B, C, D, E}  |
1047: |  B not goal | {C, D, E, G}  |
1048: |  C not goal | {D, E, G, F}  |
1049: |  D not goal | {E, G, F, H}  |
1050: |  E not goal | {(G, path:[S,B,G]), (F, path:[S,C,F]), (H, path:[S,A,D,H])}  |
1051: 
1052: State Space Graph
1053: 
1054: ![img-108.jpeg](img-108.jpeg)
1055: 
1056: Graph Search
1057: 
1058: ![img-109.jpeg](img-109.jpeg)
1059: ## 2. Breadth-First Search Example
1060: 
1061: BFS_Search(problem, queue )
1062: 
1063: # of nodes tested: 7, expanded: 6
1064: 
1065: |  Explored node | node list  |
1066: | --- | --- |
1067: |   | {S}  |
1068: |  S not goal | {A, B, C}  |
1069: |  A not goal | {B, C, D, E}  |
1070: |  B not goal | {C, D, E, G}  |
1071: |  C not goal | {D, E, G, F}  |
1072: |  D not goal | {E, G, F, H}  |
1073: |  E not goal | {G, F, H, G}  |
1074: |  **G is goal** | **Stop**  |
1075: 
1076: State Space Graph
1077: 
1078: ![img-110.jpeg](img-110.jpeg)
1079: 
1080: Path: S, B, G
1081: Cost: 8
1082: 
1083: Graph Search
1084: 
1085: ![img-111.jpeg](img-111.jpeg)
1086: 
1087: Expansion order:
1088: (S, A, B, C, D, E, G)
1089: ## 2. Breadth-First Search
1090: 
1091: **Breadth-first search:** In breadth-first search, the frontier acts like a first-in first-out (FIFO) queue. The element selected and removed from the frontier at any given time is the one that was added earliest.
1092: 
1093: ![img-112.jpeg](img-112.jpeg)
1094: 
1095: ![img-113.jpeg](img-113.jpeg)
1096: ## 2. BFS pseudo-code
1097: 
1098: ### Breadth-First Search algorithm
1099: 
1100: **function** BREADTH-FIRST-SEARCH( *problem* ) **returns** a solution, or failure
1101: 
1102: *node* ← a node with STATE = *problem*.INITIAL-STATE, PATH-COST = 0
1103: 
1104: **if** *problem*.GOAL-TEST( *node*.STATE) **then return** SOLUTION( *node* )
1105: 
1106: *frontier* ← a FIFO queue with *node* as the only element
1107: 
1108: *explored* ← an empty set
1109: 
1110: **loop do**
1111: 
1112: **if** EMPTY?( *frontier* ) **then return** failure
1113: 
1114: *node* ← POP( *frontier* ) /* chooses the shallowest node in *frontier* */
1115: 
1116: add *node*.STATE to *explored*
1117: 
1118: **for each** *action* **in** *problem*.ACTIONS( *node*.STATE) **do**
1119: 
1120: *child* ← CHILD-NODE( *problem*, *node*, *action* )
1121: 
1122: **if** *child*.STATE is not in *explored* or *frontier* **then**
1123: 
1124: **if** *problem*.GOAL-TEST(*child*.STATE) **then return** SOLUTION(*child* )
1125: 
1126: *frontier* ← INSERT( *child*, *frontier* )
1127: ## 2. BFS Properties
1128: 
1129: ■ What nodes does BFS expand?
1130: 
1131: - ■ Processes all nodes above shallowest solution
1132: - ■ Let depth of shallowest solution be $d$
1133: - ■ Search takes time $O(b^d)$
1134: 
1135: ■ How much space does the frontier take?
1136: 
1137: - ■ Has roughly the last tier, so $O(b^d)$
1138: 
1139: ■ Is it complete?
1140: 
1141: - ■ $d$ must be finite if a solution exists, so yes!
1142: 
1143: ■ Is it optimal?
1144: 
1145: - ■ Only if costs are all 1 (1 per step)
1146: 
1147: ![img-114.jpeg](img-114.jpeg)
1148: 
1149: ![img-115.jpeg](img-115.jpeg)
1150: # Quiz: DFS vs BFS
1151: 
1152: ![img-116.jpeg](img-116.jpeg)
1153: 
1154: - When will BFS outperform DFS?
1155: - When will DFS outperform BFS?
1156: 
1157: ![img-117.jpeg](img-117.jpeg)
1158: 
1159: ![img-118.jpeg](img-118.jpeg)
1160: 
1161: BFS, the closest elements to the starting location are searched first.
1162: 
1163: ![img-119.jpeg](img-119.jpeg)
1164: 
1165: DFS, the search proceeds along a continuously deeper path until it hits a barrier and must backtracks to the last decision point.
1166: # DFS vs. BFS
1167: 
1168: - If you know a solution is not far from the root of the tree, *a breadth first search (BFS) might be better*
1169: - If the tree is very deep and solutions are rare, *depth first search (DFS) might take an extremely long time, but BFS could be faster*
1170: - If the tree is very wide, *a BFS might need to much memory, so it might be completely impractical*
1171: - If solutions are frequent but located deep in the tree, *BFS could be completely impractical*
1172: - If the search tree is very deep *you will need to restrict the search depth for depth first search (DFS)*
1173: 
1174: |  Scenario | Depth first | Breadth first  |
1175: | --- | --- | --- |
1176: |  Some paths are extremely long, or even infinite | Performs badly | Performs well  |
1177: |  All paths are of similar length | Performs well | Performs well  |
1178: |  All paths are of similar length, and all paths lead to a goal state | Performs well | Wasteful of time and memory  |
1179: |  High branching factor | Performance depends on other factors | Performs poorly  |
1180: # DFS Limites
1181: 
1182: - Depth first search is incomplete if there is an infinite branch in the search tree.
1183:   - Infinite branches can happen if:
1184:     - paths contain loops
1185:     - infinite number of states and/or operators.
1186: - For problems with infinite (or just very large) state spaces, several variants of depth-first search have been developed:
1187:   - Depth limited search
1188:   - Iterative deepening search
1189: # Outline
1190: 
1191: ## Solving problems by searching
1192: 
1193: - Problem-solving agents
1194: - Search Problems
1195: - Uninformed Search Methods
1196:   1. Depth-First Search
1197:   2. Breadth-First Search
1198:   3. Iterative Deepening Search
1199:   4. Uniform-Cost Search
1200: 
1201: 
1202: ## 3.a. Depth Limited Search
1203: 
1204: - **Limited depth DFS:** just like DFS, except never go deeper than some depth $\ell$
1205: - The nodes at depth $\ell$ are treated as if they had no successors
1206: - If the search reaches a node at depth $\ell$ where the path is not a solution, we backtrack to the next choice point at depth $< \ell$
1207: - Depth-first search can be viewed as a special case of **Depth Limited Search** where $\ell = \infty$
1208: - The depth bound can sometimes be chosen based on knowledge of the problem
1209: # 3.a. Depth Limited Search
1210: 
1211: ![img-121.jpeg](img-121.jpeg)
1212: 
1213: ![img-122.jpeg](img-122.jpeg)
1214: 
1215: Example: route planning problem
1216: 
1217: ▶ Requires some knowledge of the solution:
1218: 
1219: - in the route planning problem, the longest route has length $s - 1$, where $s$ is the number of cities (states),
1220: - so we can set $\ell = s - 1$
1221: - 9 cities, depth limit of 8?
1222: 
1223: ▶ What if we choose a limit too small?
1224: 
1225: - Sacrifice completeness
1226: # 3. Iterative Deepening Search
1227: 
1228: For the most problems, $\ell$ is unknown.
1229: 
1230: Iterative Deepening Search (IDS) is a form of depth limited search which progressively increases the bound.
1231: 
1232: ![img-123.jpeg](img-123.jpeg)
1233: ### 3. Iterative Deepening Search
1234: 
1235: - Idea: get DFS's space advantage with BFS's time / shallow-solution advantages
1236: 
1237: - Run a DFS with depth limit 1. If no solution...
1238: - Run a DFS with depth limit 2. If no solution...
1239: - Run a DFS with depth limit 3 ...
1240: - Until a solution is found
1241: 
1242: - Solution will be found when $\ell = d$
1243: 
1244: - Isn't that wastefully redundant?
1245: 
1246: - Generally most work happens in the lowest level searched, so not so bad!
1247: 
1248: ![img-124.jpeg](img-124.jpeg)
1249: # 3. Iterative Deepening Search Example
1250: 
1251: IDS Search(problem, stack )
1252: 
1253: Depth : 1, # of nodes tested: 0, expanded: 0
1254: 
1255: |  expnd. node | node list  |
1256: | --- | --- |
1257: |  |   |
1258: 
1259: State Space Graph
1260: 
1261: ![img-125.jpeg](img-125.jpeg)
1262: 
1263: Graph Search
1264: # 3. Iterative Deepening Search Example
1265: 
1266: IDS Search(problem, stack )
1267: 
1268: Depth : 1, # of nodes tested: 0, expanded: 0
1269: 
1270: |  expnd. node | node list  |
1271: | --- | --- |
1272: |  |   |
1273: 
1274: State Space Graph
1275: 
1276: ![img-126.jpeg](img-126.jpeg)
1277: 
1278: Graph Search
1279: # 3. Iterative Deepening Search Example
1280: 
1281: IDS Search(problem, stack )
1282: 
1283: Depth : 1, # of nodes tested: 0, expanded: 0
1284: 
1285: |  expnd. node | node list  |
1286: | --- | --- |
1287: |   | {(S, path: [S])}  |
1288: 
1289: State Space Graph
1290: 
1291: ![img-127.jpeg](img-127.jpeg)
1292: 
1293: Graph Search
1294: # 3. Iterative Deepening Search Example
1295: 
1296: IDS Search(problem, stack )
1297: 
1298: Depth : 1, # of nodes tested: 1, expanded: 1
1299: 
1300: |  Explored node | Frontier  |
1301: | --- | --- |
1302: |   | {(S, path: [S])}  |
1303: |  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
1304: 
1305: State Space Graph
1306: 
1307: ![img-128.jpeg](img-128.jpeg)
1308: 
1309: Graph Search
1310: 
1311: ![img-129.jpeg](img-129.jpeg)
1312: # 3. Iterative Deepening Search Example
1313: 
1314: IDS Search(problem, stack )
1315: 
1316: Depth : 1, # of nodes tested: 2, expanded: 1
1317: 
1318: |  Explored node | Frontier  |
1319: | --- | --- |
1320: |   | {(S, path: [S])}  |
1321: |  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
1322: |  A not goal | {(C, path: [S, C]), (B, path: [S, B])} **no expand**  |
1323: 
1324: State Space Graph
1325: 
1326: ![img-130.jpeg](img-130.jpeg)
1327: 
1328: Graph Search
1329: 
1330: ![img-131.jpeg](img-131.jpeg)
1331: # 3. Iterative Deepening Search Example
1332: 
1333: IDS Search(problem, stack )
1334: 
1335: Depth : 1, # of nodes tested: 3, expanded: 1
1336: 
1337: |  Explored node | Frontier  |
1338: | --- | --- |
1339: |   | {(S, path: [S])}  |
1340: |  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
1341: |  A not goal | {(C, path: [S, C]), (B, path: [S, B])} **no expand**  |
1342: |  B not goal | {(C, path: [S, C]) **no expand**  |
1343: 
1344: State Space Graph
1345: 
1346: ![img-132.jpeg](img-132.jpeg)
1347: 
1348: Graph Search
1349: 
1350: ![img-133.jpeg](img-133.jpeg)
1351: # 3. Iterative Deepening Search Example
1352: 
1353: IDS Search(problem, stack )
1354: 
1355: Depth : 1, # of nodes tested: 4, expanded: 1
1356: 
1357: |  Explored node | Frontier  |
1358: | --- | --- |
1359: |   | {(S, path: [S])}  |
1360: |  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
1361: |  A not goal | {(C, path: [S, C]), (B, path: [S, B])} **no expand**  |
1362: |  B not goal | {(C, path: [S, C])} **no expand**  |
1363: |  C not goal | {} **no expand**  |
1364: 
1365: State Space Graph
1366: 
1367: ![img-134.jpeg](img-134.jpeg)
1368: 
1369: Graph Search
1370: 
1371: ![img-135.jpeg](img-135.jpeg)
1372: # 3. Iterative Deepening Search Example
1373: 
1374: IDS Search(problem, stack )
1375: 
1376: Depth : 1, # of nodes tested: 4, expanded: 1
1377: 
1378: |  Explored node | Frontier  |
1379: | --- | --- |
1380: |   | {(S, path: [S])}  |
1381: |  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
1382: |  A not goal | {(C, path: [S, C]), (B, path: [S, B])} **no expand**  |
1383: |  B not goal | {(C, path: [S, C])} **no expand**  |
1384: |  C not goal | {} **no expand**  |
1385: 
1386: Frontier is empty. Increasing depth
1387: 
1388: State Space Graph
1389: 
1390: ![img-136.jpeg](img-136.jpeg)
1391: 
1392: Graph Search
1393: 
1394: ![img-137.jpeg](img-137.jpeg)
1395: # 3. Iterative Deepening Search Example
1396: 
1397: IDS Search(problem, stack )
1398: 
1399: **Depth : 2**, # of nodes tested: 4, expanded: 2
1400: 
1401: |  expnd. node | node list  |
1402: | --- | --- |
1403: |   | {S}  |
1404: |  S not goal | {C,B,A}  |
1405: |  A not goal | {C,B} no expand  |
1406: |  B not goal | {C} no expand  |
1407: |  C not goal | {} no expand  |
1408: 
1409: State Space Graph
1410: 
1411: ![img-138.jpeg](img-138.jpeg)
1412: 
1413: Graph Search
1414: # 3. Iterative Deepening Search Example
1415: 
1416: IDS Search(problem, stack )
1417: 
1418: **Depth : 2**, # of nodes tested: 4, expanded: 2
1419: 
1420: |  expnd. node | node list  |
1421: | --- | --- |
1422: |   | {S}  |
1423: |  S not goal | {C,B,A}  |
1424: |  A not goal | {C,B} no expand  |
1425: |  B not goal | {C} no expand  |
1426: |  C not goal | {} no expand  |
1427: 
1428: State Space Graph
1429: 
1430: Graph Search
1431: 
1432: ![img-139.jpeg](img-139.jpeg)
1433: 
1434: ![img-140.jpeg](img-140.jpeg)
1435: # 3. Iterative Deepening Search Example
1436: 
1437: IDS Search(problem, stack )
1438: 
1439: Depth : 2, # of nodes tested: 4, expanded: 2
1440: 
1441: |  expnd. node | node list  |
1442: | --- | --- |
1443: |   | {S}  |
1444: |  S not goal | {C,B,A}  |
1445: |  A not goal | {C,B} no expand  |
1446: |  B not goal | {C} no expand  |
1447: |  C not goal | {} no expand  |
1448: |  S not goal | {C,B,A}  |
1449: 
1450: State Space Graph
1451: 
1452: ![img-141.jpeg](img-141.jpeg)
1453: 
1454: Graph Search
1455: 
1456: ![img-142.jpeg](img-142.jpeg)
1457: # 3. Iterative Deepening Search Example
1458: 
1459: IDS Search(problem, stack )
1460: 
1461: Depth : 2, # of nodes tested: 4, expanded: 3
1462: 
1463: |  expnd. node | node list  |
1464: | --- | --- |
1465: |   | {S}  |
1466: |  S not goal | {C,B,A}  |
1467: |  A not goal | {C,B} no expand  |
1468: |  B not goal | {C} no expand  |
1469: |  C not goal | {} no expand  |
1470: |  S not goal | {C,B,A}  |
1471: |  A not goal | {C,B,E, D}  |
1472: 
1473: State Space Graph
1474: 
1475: ![img-143.jpeg](img-143.jpeg)
1476: 
1477: Graph Search
1478: 
1479: ![img-144.jpeg](img-144.jpeg)
1480: # 3. Iterative Deepening Search Example
1481: 
1482: IDS Search(problem, stack )
1483: 
1484: Depth : 2, # of nodes tested: 5, expanded: 3
1485: 
1486: |  expnd. node | node list  |
1487: | --- | --- |
1488: |   | {S}  |
1489: |  S not goal | {C,B,A}  |
1490: |  A not goal | {C,B} no expand  |
1491: |  B not goal | {C} no expand  |
1492: |  C not goal | {} no expand  |
1493: |  S not goal | {C,B,A}  |
1494: |  A not goal | {C,B,E, D}  |
1495: |  D not goal | {C,B,E}  |
1496: 
1497: State Space Graph
1498: 
1499: ![img-145.jpeg](img-145.jpeg)
1500: 
1501: Graph Search
1502: 
1503: ![img-146.jpeg](img-146.jpeg)
1504: # 3. Iterative Deepening Search Example
1505: 
1506: IDS Search(problem, stack )
1507: 
1508: Depth : 2, # of nodes tested: 6, expanded: 3
1509: 
1510: |  expnd. node | node list  |
1511: | --- | --- |
1512: |   | {S}  |
1513: |  S not goal | {C,B,A}  |
1514: |  A not goal | {C,B} no expand  |
1515: |  B not goal | {C} no expand  |
1516: |  C not goal | {} no expand  |
1517: |  S not goal | {C, B, A}  |
1518: |  A not goal | {C, B, E, D}  |
1519: |  D not goal | {C, B, E}  |
1520: |  E not goal | {C, B}  |
1521: 
1522: State Space Graph
1523: 
1524: ![img-147.jpeg](img-147.jpeg)
1525: 
1526: Graph Search
1527: 
1528: ![img-148.jpeg](img-148.jpeg)
1529: # 3. Iterative Deepening Search Example
1530: 
1531: IDS Search(problem, stack )
1532: 
1533: Depth : 2, # of nodes tested: 6, expanded: 4
1534: 
1535: |  expnd. node | node list  |
1536: | --- | --- |
1537: |   | {S}  |
1538: |  S not goal | {C,B,A}  |
1539: |  A not goal | {C,B} no expand  |
1540: |  B not goal | {C} no expand  |
1541: |  C not goal | {} no expand  |
1542: |  S not goal | {C, B, A}  |
1543: |  A not goal | {C, B, E, D}  |
1544: |  D not goal | {C, B, E}  |
1545: |  E not goal | {C, B}  |
1546: |  B not goal | {C, G}  |
1547: 
1548: State Space Graph
1549: 
1550: ![img-149.jpeg](img-149.jpeg)
1551: 
1552: Graph Search
1553: 
1554: ![img-150.jpeg](img-150.jpeg)
1555: # 3. Iterative Deepening Search Example
1556: 
1557: IDS Search(problem, stack )
1558: 
1559: Depth : 2, # of nodes tested: 7, expanded: 4
1560: 
1561: |  expnd. node | node list  |
1562: | --- | --- |
1563: |   | {S}  |
1564: |  S not goal | {C,B,A}  |
1565: |  A not goal | {C,B} no expand  |
1566: |  B not goal | {C} no expand  |
1567: |  C not goal | {} no expand  |
1568: |  S not goal | {C, B, A}  |
1569: |  A not goal | {C, B, E, D}  |
1570: |  D not goal | {C, B, E}  |
1571: |  E not goal | {C, B}  |
1572: |  B not goal | {C, G}  |
1573: |  **G is goal** | **Stop**  |
1574: 
1575: State Space Graph
1576: 
1577: ![img-151.jpeg](img-151.jpeg)
1578: 
1579: Graph Search
1580: 
1581: ![img-152.jpeg](img-152.jpeg)
1582: # 3. Iterative Deepening Search Example
1583: 
1584: IDS Search(problem, stack )
1585: 
1586: Depth : 2, # of nodes tested: 7, expanded: 4
1587: 
1588: |  expnd. node | node list  |
1589: | --- | --- |
1590: |   | {S}  |
1591: |  S not goal | {C,B,A}  |
1592: |  A not goal | {C,B} no expand  |
1593: |  B not goal | {C} no expand  |
1594: |  C not goal | {} no expand  |
1595: |  S not goal | {C, B, A}  |
1596: |  A not goal | {C, B, E, D}  |
1597: |  D not goal | {C, B, E}  |
1598: |  E not goal | {C, B}  |
1599: |  B not goal | {C, G}  |
1600: |  **G is goal** | **Stop**  |
1601: 
1602: State Space Graph
1603: 
1604: ![img-153.jpeg](img-153.jpeg)
1605: 
1606: Graph Search
1607: 
1608: ![img-154.jpeg](img-154.jpeg)
1609: 
1610: Path: S, B, G
1611: Cost: 8
1612: # 3. Iterative deepening search Properties
1613: 
1614: # - ■ **Time?**
1615: 
1616: - ■ $O(b^d)$, where $b$ is the branching factor and $d$ is the depth of the shallowest solution.
1617: 
1618: # - ■ **Space?**
1619: 
1620: - ■ $O(bd)$
1621: 
1622: # - ■ **Is it complete?**
1623: 
1624: - ■ yes
1625: 
1626: # - ■ **Is it optimal?**
1627: 
1628: - ■ Yes, if step cost = 1
1629: 
1630: ![img-155.jpeg](img-155.jpeg)
1631: ### 3. Iterative deepening search Properties
1632: 
1633: - Has the advantages of BFS
1634:   - Complete
1635:   - Optimal (if the edges have identical costs)
1636: - Has the advantages of DFS
1637:   - Linear space complexity: $O(bd)$
1638: - Wasteful?
1639:   - because nodes near the top of the search tree are generated multiple times
1640: - It turns out this is NOT very costly
1641:   - For a tree with (nearly) the same branching factor at each level, most of the nodes are in the bottom level
1642: - Worst case time complexity: $O(b^d)$
1643: # 3. Iterative Deepening Search algorithm
1644: 
1645: Iterative Deepening Search pseudocode
1646: 
1647: function ITERATIVE-DEEPENING-SEARCH(problem) returns a solution node or failure
1648: 
1649: for depth = 0 to ∞ do
1650: 
1651: result ← DEPTH-LIMITED-SEARCH(problem, depth)
1652: 
1653: if result ≠ cutoff then return result
1654: 
1655: function DEPTH-LIMITED-SEARCH(problem, ℓ) returns a node or failure or cutoff
1656: 
1657: frontier ← a LIFO queue (stack) with NODE(problem.INITIAL) as an element
1658: 
1659: result ← failure
1660: 
1661: while not IS-EMPTY(frontier) do
1662: 
1663: node ← POP(frontier)
1664: 
1665: if problem.IS-GOAL(node.STATE) then return node
1666: 
1667: if DEPTH(node) > ℓ then
1668: 
1669: result ← cutoff
1670: 
1671: else if not IS-CYCLE(node) do
1672: 
1673: for each child in EXPAND(problem, node) do
1674: 
1675: add child to frontier
1676: 
1677: return result
1678: # Outline
1679: 
1680: ## Solving problems by searching
1681: 
1682: - Problem-solving agents
1683: - Search Problems
1684: - Uninformed Search Methods
1685:   1. Depth-First Search
1686:   2. Breadth-First Search
1687:   3. Iterative Deepening Search
1688:   4. Uniform-Cost Search
1689: 
1690: 
1691: # Search with varying step costs
1692: 
1693: ![img-157.jpeg](img-157.jpeg)
1694: 
1695: - BFS finds the path with the fewest steps, but **does not always find the cheapest path**
1696: # Outline
1697: 
1698: ## Solving problems by searching
1699: 
1700: - Problem-solving agents
1701: - Search Problems
1702: - Uninformed Search Methods
1703:   1. Depth-First Search
1704:   2. Breadth-First Search
1705:   3. Iterative Deepening Search
1706:   4. Uniform-Cost Search
1707: 
1708: 
1709: ## 4. Uniform Cost Search (UCS)
1710: 
1711: - For each frontier node, save the total cost of the path from the initial state to that node
1712: - Expand the frontier node with the **lowest path cost**
1713: - **Implementation:** *frontier* is a priority queue ordered by path cost
1714: - Equivalent to breadth-first if step costs all equal
1715: - Equivalent to Dijkstra’s algorithm in general
1716: 
1717: ![img-159.jpeg](img-159.jpeg)
1718: # 4. Uniform Cost Search Example
1719: 
1720: UCS Search(problem, priorityQueue )
1721: 
1722: # of nodes tested: 0, expanded: 0
1723: 
1724: |  expnd. node | node list  |
1725: | --- | --- |
1726: |   | {S}  |
1727: 
1728: **Strategy:** expand a cheapest node first
1729: 
1730: **Implementation:** Frontier is a priority queue (priority: cumulative cost)
1731: 
1732: State Space Graph
1733: 
1734: ![img-160.jpeg](img-160.jpeg)
1735: 
1736: Graph Search
1737: # 4. Uniform Cost Search Example
1738: 
1739: UCS Search(problem, priorityQueue )
1740: 
1741: # of nodes tested:1, expanded: 1
1742: 
1743: |  Explored node | Frontier  |
1744: | --- | --- |
1745: |   | {(S, path: [S], cost: 0}  |
1746: |  S not goal | {(B, [S,B], 2), (C, [S,C], 4), (A, [S,A], 5)}  |
1747: 
1748: State Space Graph
1749: 
1750: ![img-161.jpeg](img-161.jpeg)
1751: 
1752: Graph Search
1753: 
1754: ![img-162.jpeg](img-162.jpeg)
1755: # 4. Uniform Cost Search Example
1756: 
1757: UCS Search(problem, priorityQueue )
1758: 
1759: # of nodes tested: 2, expanded: 2
1760: 
1761: |  Explored node | Frontier  |
1762: | --- | --- |
1763: |   | {(S, path: [S], cost: 0}  |
1764: |  S not goal | {(B, [S,B], 2), (C, [S,C], 4), (A, [S,A], 5)}  |
1765: |  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
1766: 
1767: State Space Graph
1768: 
1769: ![img-163.jpeg](img-163.jpeg)
1770: 
1771: Graph Search
1772: 
1773: ![img-164.jpeg](img-164.jpeg)
1774: # 4. Uniform Cost Search Example
1775: 
1776: UCS Search(problem, priorityQueue )
1777: 
1778: # of nodes tested: 3, expanded: 3
1779: 
1780: |  Explored node | Frontier  |
1781: | --- | --- |
1782: |   | {(S, path: [S], cost: 0)}  |
1783: |  S not goal | {(B, [S,B], 2), (C, [S,C], 4), (A, [S,A], 5)}  |
1784: |  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
1785: |  C not goal | {(A, [S,A], 5), (G, [S, B, G], 8), (F, [S, C, F], 6)}  |
1786: 
1787: State Space Graph
1788: 
1789: ![img-165.jpeg](img-165.jpeg)
1790: 
1791: Graph Search
1792: 
1793: ![img-166.jpeg](img-166.jpeg)
1794: # 4. Uniform Cost Search Example
1795: 
1796: UCS Search(problem, priorityQueue )
1797: 
1798: # of nodes tested: 4, expanded: 4
1799: 
1800: |  Explored node | Frontier  |
1801: | --- | --- |
1802: |   | {(S, path: [S], cost: 0)}  |
1803: |  S not goal | {(B, [S,B], 2), (C, [S,C], 4), (A, [S,A], 5)}  |
1804: |  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
1805: |  C not goal | {(A, [S,A], 5), (G, [S, B, G], 8), (F, [S, C, F], 6)}  |
1806: |  A not goal | {(G, [S, B, G], 8), (F, [S, C, F], 6), (D, [S, A, D], 14), (E, [S, A, E], 9)}  |
1807: 
1808: State Space Graph
1809: 
1810: ![img-167.jpeg](img-167.jpeg)
1811: 
1812: Graph Search
1813: 
1814: ![img-168.jpeg](img-168.jpeg)
1815: ## 4. Uniform Cost Search Example
1816: 
1817: UCS Search(problem, priorityQueue)
1818: 
1819: # of nodes tested: 5, expanded: 5
1820: 
1821: |  Explored node | Frontier  |
1822: | --- | --- |
1823: |   | {(S, path: [S], cost: 0}  |
1824: |  S not goal | {(B, [S,B], 2),(C, [S,C], 4),(A, [S,A], 5)}  |
1825: |  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
1826: |  C not goal | {(A, [S,A], 5), (G, [S, B, G], 8), (F, [S, C, F], 6)}  |
1827: |  A not goal | {(G, [S, B, G], 8), (F, [S, C, F], 6), (D, [S, A, D], 14), (E, [S, A, E], 9)}  |
1828: |  F not goal | {(G, [S, B, G], 8), (D, [S, A, D], 14), (E, [S, A, E], 9), (G, [S, C, F, G], 7)}  |
1829: 
1830: State Space Graph
1831: 
1832: ![img-169.jpeg](img-169.jpeg)
1833: 
1834: Graph Search
1835: 
1836: ![img-170.jpeg](img-170.jpeg)
1837: 
1838: Remove the higher-cost of identical nodes on the queue and save memory. However, UCS is optimal even if this is not done, since lower-cost nodes sort to the front.
1839: ## 4. Uniform Cost Search Example
1840: 
1841: UCS Search(problem, priorityQueue)
1842: 
1843: # of nodes tested: 6, expanded: 5
1844: 
1845: |  Explored node | Frontier  |
1846: | --- | --- |
1847: |   | {(S, path: [S], cost: 0}  |
1848: |  S not goal | {(B, [S,B], 2),(C, [S,C], 4),(A, [S,A], 5)}  |
1849: |  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
1850: |  C not goal | {(A, [S,A], 5), (G, [S, B, G], 8), (F, [S, C, F], 6)}  |
1851: |  A not goal | {(G, [S, B, G], 8), (F, [S, C, F], 6), (D, [S, A, D], 14), (E, [S, A, E], 9)}  |
1852: |  F not goal | {(G, [S, B, G], 8), (D, [S, A, D], 14), (E, [S, A, E], 9), (G, [S, C, F, G], 7)}  |
1853: |  G is goal | Stop  |
1854: 
1855: State Space Graph
1856: 
1857: ![img-171.jpeg](img-171.jpeg)
1858: 
1859: Graph Search
1860: 
1861: ![img-172.jpeg](img-172.jpeg)
1862: # 4. UCS algorithm
1863: 
1864: # Best first search
1865: 
1866: function BEST-FIRST-SEARCH(problem, f) returns a solution node or failure
1867:     node ← NODE(STATE=problem.INITIAL)
1868:     frontier ← a priority queue ordered by f, with node as an element
1869:     reached ← a lookup table, with one entry with key problem.INITIAL and value node
1870:     while not IS-EMPTY(frontier) do
1871:         node ← POP(frontier)
1872:         if problem.IS-GOAL(node.STATE) then return node
1873:         for each child in EXPAND(problem, node) do
1874:             s ← child.STATE
1875:             if s is not in reached or child.PATH-COST < reached[s].PATH-COST then
1876:                 reached[s] ← child
1877:                 add child to frontier
1878:     return failure
1879: 
1880: function EXPAND(problem, node) yields nodes
1881:     s ← node.STATE
1882: 
1883:     for each action in problem.ACTIONS(s) do
1884:         s' ← problem.RESULT(s, action)
1885:         cost ← node.PATH-COST + problem.ACTION-COST(s, action, s')
1886:     yield NODE(STATE=s', PARENT=node, ACTION=action, PATH-COST=cost)
1887: 
1888: # Uniform Cost Search
1889: 
1890: function UNIFORM-COST-SEARCH(problem) returns a solution node, or failure
1891: return BEST-FIRST-SEARCH(problem, PATH-COST)
1892: # 4. UCS Properties
1893: 
1894: What nodes does UCS expand?
1895: 
1896: - Processes all nodes with cost less than cheapest solution!
1897: - If that solution costs $C^*$ and arcs cost at least $\varepsilon$, then the “effective depth” is roughly $C^*/\varepsilon$
1898: - Takes time $O(b^{C*/\varepsilon})$ (exponential in effective depth)
1899: - This can be greater than $O(b^d)$: the search can explore long paths consisting of small steps before exploring shorter paths consisting of larger steps
1900: 
1901: How much space does the frontier take?
1902: 
1903: - Has roughly the last tier, so $O(b^{C*/\varepsilon})$
1904: 
1905: Is it complete?
1906: 
1907: - Assuming best solution has a finite cost and minimum arc cost is positive, yes!
1908: 
1909: Is it optimal?
1910: 
1911: - Yes! (Proof next lecture via A*)
1912: 
1913: ![img-173.jpeg](img-173.jpeg)
1914: # 4. Uniform Cost Issues
1915: 
1916: - ■ **Strategy:** expand lowest path cost
1917: - ■ **The good:** UCS is complete and optimal!
1918: - ■ **The bad:**
1919:   - ■ Explores options in every “direction”
1920:   - ■ No information about goal location
1921: 
1922: ![img-174.jpeg](img-174.jpeg)
1923: 
1924: ![img-175.jpeg](img-175.jpeg)
1925: # Review: Uninformed search strategies
1926: 
1927: - A **search strategy** is defined by picking the order of node expansion
1928: - **Uninformed** search strategies use only the information available in the problem definition
1929:   - Breadth-first search
1930:   - Depth-first search
1931:   - Iterative deepening search
1932:   - Uniform-cost search
1933:   - Bidirectional Search
1934: # BFS/DFS/IDS/UCS
1935: 
1936: • Breadth-first search
1937: 
1938: - • **Good**: optimal, works well when many options, but not many actions required
1939: - • **Bad**: assumes all actions have equal cost
1940: 
1941: • Depth-first search
1942: 
1943: - • **Good**: memory-efficient, works well when few options, but lots of actions required
1944: - • **Bad**: not optimal, can run infinitely, assumes all actions have equal cost
1945: 
1946: • Iterative deepening search
1947: 
1948: - • **Good**: optimal, memory-efficient, and adaptable to different situations
1949: - • **Bad**: redundant work, assume all actions have equal cost,
1950: 
1951: • Uniform-cost search
1952: 
1953: - • **Good**: optimal, handles variable-cost actions
1954: - • **Bad**: explores all options, no information about goal location
1955: 
1956: **Basically Dijkstra's Algorithm!**
1957: # Evaluation of search algorithms
1958: 
1959: |  Criterion | Breadth-First | Uniform-Cost | Depth-First | Depth-Limited | Iterative Deepening  |
1960: | --- | --- | --- | --- | --- | --- |
1961: |  Complete? | Yes^{1} | Yes^{1,2} | No | No | Yes^{1}  |
1962: |  Optimal cost? | Yes^{3} | Yes | No | No | Yes^{3}  |
1963: |  Time | $$O(b^d)$$ | $$O(b^{1+\lfloor C^*/\epsilon \rfloor})$$ | $$O(b^m)$$ | $$O(b^\ell)$$ | $$O(b^d)$$  |
1964: |  Space | $$O(b^d)$$ | $$O(b^{1+\lfloor C^*/\epsilon \rfloor})$$ | $$O(bm)$$ | $$O(b\ell)$$ | $$O(bd)$$  |
1965: 
1966: - b is the branching factor; m is the maximum depth of the search tree; d is the depth of the shallowest solution, or is m when there is no solution; ℓ is the depth limit.
1967: - Superscript caveats are as follows: ¹ complete if b is finite, and the state space either has a solution or is finite. ² complete if all action costs are ≥ ε > 0; ³ cost-optimal if action costs are all identical.
1968: # Search Gone Wrong?
1969: 
1970: Still not as smart as it could be...
1971: 
1972: Can we do better?
1973: 
1974: 
1975: # Incorporating goal information
1976: 
1977: **How to efficiently solve search problems with variable-cost actions, using information about the goal state?**
1978: 
1979: This is the motivation behind **informed search**, which uses problem-specific knowledge to try and find solutions more efficiently
