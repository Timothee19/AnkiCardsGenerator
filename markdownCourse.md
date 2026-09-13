# Artificial Intelligence Algorithms

## Basic Search

![img-0.jpeg](img-0.jpeg)

Instructor: Farah AIT SALAHT

ESILV- Leonard de Vinci Graduated School of Engineering
# Previous session

## What did we learn:

- Introduction to Artificial Intelligence for problem solving and decision-making and intelligent agents
- What makes an Agents?

![img-1.jpeg](img-1.jpeg)
# What makes an Agents?

- Example: Vacuum-cleaner world – Roomba!

![img-2.jpeg](img-2.jpeg)

(dirt)

- Percepts: location and contents, e.g., [A,Dirty]
- Actions: Left, Right, Suck

- Example of an agent function:

|  Percept sequence | Action  |
| --- | --- |
|  [A, Clean] | Right  |
|  [A, Dirty] | Suck  |
|  [B, Clean] | Left  |
|  [B, Dirty] | Suck  |
|  [A, Clean], [A, Clean] | Right  |
|  [A, Clean], [A, Dirty] | Suck  |
|  ⋮ | ⋮  |
# What makes one rational?

A rational agent always acts to **maximize the utility function**, given current state/percept

![img-3.jpeg](img-3.jpeg)
# What makes one rational?

How do we choose the best sequence of actions?

This involves defining the
« search problems »
# Search process?

![img-4.jpeg](img-4.jpeg)
# Information Retrieval vs. Search

![img-5.jpeg](img-5.jpeg)

![img-6.jpeg](img-6.jpeg)

![img-7.jpeg](img-7.jpeg)

![img-8.jpeg](img-8.jpeg)
# Definition of Search

## Finding a (best) sequence of actions to solve a problem

- We will consider the problem of designing goal-based agents in
  - Deterministic
  - Fully observable
  - Discret
  - Known environments.
# Today

## Solving problems by searching

- Problem-solving agents
- Search Problems
- Uninformed Search Methods
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening Search
  4. Uniform-Cost Search

![img-9.jpeg](img-9.jpeg)
# Agents that Plan ahead

- An agent enjoying a touring vacation in United States.
- He is in the city of Boston and must find his friend in San Francisco.
- Which route to follow?
- We assume that our agent always have access to information about the world (the map).

![img-10.jpeg](img-10.jpeg)
# Building a Problem-Solving Agent

- What goal / problem does the agent try to achieve / solve?
- What knowledge does the agent need?
- What actions does the agent need to do?
# Agents that Plan ahead

To find a way to reach the destination (goal), the agent can follow this four-phase problem-solving process:

## 1. Goal formulation:

- How do you describe the goal?
  - as a problem to be solved
  - as a situation to be reached
  - as a set of properties to be acquired.
- **Our example:** The agent adopts the **goal** of reaching San Francisco.
- Goals organize behavior by limiting the objectives and hence the actions to be considered.

![img-11.jpeg](img-11.jpeg)
# Agents that Plan ahead

To find a way to reach the destination (goal), the agent can follow this four-phase problem-solving process:

## 2. Problem formulation:

- The agent devises a description of the states and actions necessary to reach the goal
- Define an abstract model of the relevant part of the world.
  - Removing detail from a representation while retaining relevant information for solving the problem.
- **Example:**
  - consider the actions of traveling from one city to an adjacent city
  - the state of the world that will change due to an action is the current city.

![img-12.jpeg](img-12.jpeg)

Key West
# Agents that Plan ahead

To find a way to reach the destination (goal), the agent can follow this four-phase problem-solving process:

## 3. Search:

- Before taking any action in the real world, the agent simulates sequences of actions in its model, searching until it finds a sequence of actions that reaches the goal. Such a sequence is called a **solution**.

## 4. Execution:

The agent can now execute the actions in the solution, one at a time.

![img-13.jpeg](img-13.jpeg)
# Today

## Solving problems by searching

- Problem-solving agents
- Search Problems
- Uninformed Search Methods
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening Search
  4. Uniform-Cost Search

![img-14.jpeg](img-14.jpeg)
# Search problems

## Search: sequence of actions to achieve goal.

- Search algorithm takes a problem as input and returns a solution in the form of a sequence of actions.
- Once solution is found, actions it recommends are executed.

Formulate -> Search -> Actions

- When executing, the agent is running open loop, i.e., it ignores percepts since it already knows in advance what they will be.
# Problem formulation

A search problem can be defined formally as follows:

a) **State space** — The set of all possible states in the environment.

b) **Initial state** — The starting state of the agent. Example: *Boston*.

c) **Goal States (Goal Test)** — Desired end states the agent aims to reach. **Example:** San Francisco.

d) **Actions Available to the Agent** — Possible moves or decisions the agent can make. Given a state $s$, $ACTIONS(s)$ returns a finite set of actions that can be executed in $s$. Each of these actions is considered applicable in $s$.

**Example:** $ACTIONS(Boston) = \{To\_KeyWest, To\_NewYork, To\_Chicago\}$
# Problem formulation

A search problem can be defined formally as follows:

e) A **transition model** — describes what each action does. $RESULT(s, a)$ returns the state that results from doing action $a$ in state $s$.

For example, $RESULT(Boston, To\_Chicago) = Chicago$.

f) **Action cost function** — denoted by $ACTION-COST(s, a, s')$, gives a numeric cost of applying action $a$ in state $s$ to reach state $s'$.

- A problem-solving agent should use a cost function that reflects its own performance measure;
- For example, for route-finding agents, the cost of an action might be the length in kilometers, or it might be the time it takes to complete the action, etc.
# Problem formulation

- The state space can be represented as a **graph** in which the vertices are states and the directed edges between them are actions.

- In a **state space graph**, each state occurs only once!
- In case of an undirected graph, each edge indicates two actions, one in each direction.

- A sequence of actions forms a **path**
- A **solution** is a path from the initial state to a goal state.
- We assume that action costs are additive; that is, the total cost of a path is the sum of the individual action costs.
- An **optimal solution** has the lowest path cost among all solutions.
- In this course, we assume that all action costs will be positive, to avoid certain complications.

![img-15.jpeg](img-15.jpeg)
# Problem formulation

![img-16.jpeg](img-16.jpeg)

![img-17.jpeg](img-17.jpeg)

- State space: Cities
- Initial state: Boston
- Goal test: is state == San Francisco?
- Actions: Go to adjacent city
- Action cost: e.g., cost = distance
- Transition model: RESULT(Boston, To_Chicago) = Chicago
  RESULT(Boston, To_New York) = New York
  RESULT(Chicago, To_Danver) = Denver
  ...
- Example of path: {NewYork, Nashville, Austin}
- Solutions:
  - {Boston, NewYork, Nashville, Austin, Phoenix, SanFrancisco}
  - {Boston, Chicago, SanFrancisco}
  - ...
- Optimal solution?? Depends on the objective
# Problem formulation

## Other example

![img-18.jpeg](img-18.jpeg)

A vacuum-cleaner world with just two locations.

![img-19.jpeg](img-19.jpeg)

![img-20.jpeg](img-20.jpeg)

## State space

![img-21.jpeg](img-21.jpeg)

![img-22.jpeg](img-22.jpeg)

![img-23.jpeg](img-23.jpeg)

![img-24.jpeg](img-24.jpeg)

![img-25.jpeg](img-25.jpeg)

![img-26.jpeg](img-26.jpeg)

## Goal State

![img-27.jpeg](img-27.jpeg)

![img-28.jpeg](img-28.jpeg)

![img-29.jpeg](img-29.jpeg)

![img-30.jpeg](img-30.jpeg)

![img-31.jpeg](img-31.jpeg)

![img-32.jpeg](img-32.jpeg)

![img-33.jpeg](img-33.jpeg)

![img-34.jpeg](img-34.jpeg)

The eight possible states of the vacuum world

States 7 and 8 are goal states.
# Problem formulation

Example

![img-35.jpeg](img-35.jpeg)

A vacuum-cleaner world with just two locations.

Initial state

![img-36.jpeg](img-36.jpeg)

![img-37.jpeg](img-37.jpeg)

![img-38.jpeg](img-38.jpeg)

![img-39.jpeg](img-39.jpeg)

![img-40.jpeg](img-40.jpeg)

![img-41.jpeg](img-41.jpeg)

![img-42.jpeg](img-42.jpeg)

![img-43.jpeg](img-43.jpeg)

Actions

- Right (R)
- Left (L)
- Suck (S)

Any state can be designated as the initial state.
# Problem formulation

## Example

![img-44.jpeg](img-44.jpeg)

A vacuum-cleaner world with just two locations.

## Transition model

- **Suck** removes any dirt from the agent's cell;
- **Right** moves the agent one cell in the right direction, unless it hits a wall, in which case the action has no effect.
- **Left** moves the agent one cell in the left direction, unless it hits a wall, in which case the action has no effect.

## Action cost

- Each action costs 1.
# Problem formulation

Example

![img-45.jpeg](img-45.jpeg)

A vacuum-cleaner world with just two locations.

State space graph

![img-46.jpeg](img-46.jpeg)

- Example of path:
{R, S, R, S, L}, From initial state 1
- Example of solution:
{S, L, S, R, S}, From initial state 1
- Example of optimal solution:
{S, R, S}, From initial state 1
# Problem Formulation involves Abstraction

## Example: Missionaries and Cannibals

![img-47.jpeg](img-47.jpeg)

- 3 missionaries and 3 cannibals on left side
- Boat holds 1 or 2 people
- Never leave missionaries outnumbered by cannibals
- **States:**
  (# cannibals, # missionaries, # boats) on left side of river
- **Starting state / Goal state:**
  - (3,3,1) / (0,0,0)
- **Actions:**
  - Remove up to 2 people to other side and the resulting state is safe
- **Path cost:** number of crossing
# Problem formulation

- The process of removing detail from a representation is called *abstraction*.
- A good problem formulation has the right level of detail.
- The abstraction is *valid* if we can elaborate any abstract solution into a solution in the more detailed world;
  - a sufficient condition is that for every detailed state that is “in Boston,” there is a detailed path to some state that is “in Key west,” and so on.
- The abstraction is *useful* if carrying out each of the actions in the solution is easier than the original problem; in our case, the action “drive from Boston to Key West” can be carried out without further search or planning by a driver with average skill.
# How to Search

Given:

- Initial state
- Actions
- Transition model
- Goal state
- Path cost

![img-48.jpeg](img-48.jpeg)

How do we find a solution (best solution)?
# How to Search

## Generating action sequences

![img-49.jpeg](img-49.jpeg)

![img-50.jpeg](img-50.jpeg)

The search strategy determines which state to expand next.
# Search Tree

- A sequences of actions and their outcomes
- The root node corresponds to the starting state
- The children of a node correspond to the successor states of that node's state
- A path through the tree corresponds to a sequence of actions
  - A solution is a path ending in the goal state
- **Nodes vs. states**
  - A state is a representation of the world, while a **node** is a data structure that is part of the search tree
    - Node keeps track of a **state description**, a **parent node** (the node that generated this node), an **action** (the action that was applied to the parent to generate this node), a **path cost** (the cost of the path from the start state to this state), **depth** (number of steps in the path from the start state), and possibly other info.
- For most problems, we can never actually build the whole tree

![img-51.jpeg](img-51.jpeg)
# State Space Graphs vs. Search Trees

## State Space Graph

![img-52.jpeg](img-52.jpeg)

State : e

Each NODE in the
search tree is an
entire PATH in the
state space graph.

## Search Tree

![img-53.jpeg](img-53.jpeg)

Node: (e, [S,d,e], 2,...)

Node: (e, [S,e], 1,...)

Node: (Current state, path from initial state, cost, depth...)
# Search tree process

- Begin at the start state and **expand** it by making a list of all possible successor states
- Maintain a **frontier** or a list of unexpanded states
- At each step, pick a state from the frontier to expand
- Keep going until you reach a goal state
- **Objective:** *Try to expand as few states as possible*

![img-54.jpeg](img-54.jpeg)
# Tree Search example

![img-55.jpeg](img-55.jpeg)

|  expended node | Frontier  |
| --- | --- |
|   | {S}  |
|  S not goal | {d,e,p}  |
|  d not goal | {e,p,b,c,e}  |
|  e not goal | {e,p,b,c,h,r}  |
|  r not goal | {e,p,b,c,h,f}  |
|  f not goal | {e,p,b,c,h,c,G}  |
|  G is goal | {e,p,b,c,h,c}  |

![img-56.jpeg](img-56.jpeg)
# Quiz: State Space Graphs vs. Search Trees

Consider this 4-state graph:

![img-57.jpeg](img-57.jpeg)

How big is its search tree (from $s$)?

![img-58.jpeg](img-58.jpeg)

![img-59.jpeg](img-59.jpeg)

Important: Lots of repeated structure in the search tree!
# Tree search algorithm

## Remark — Handle repeated states

- Every time you **expand a node**, add that state to the **explored set**; do not put explored states on the frontier again
- Every time you add a node to the frontier, check whether it already exists in the frontier with a higher path cost, and if yes, replace that node with the new one
- This approach is called **Graph search**
# General Graph Search

Consider this 4-state graph:

![img-60.jpeg](img-60.jpeg)

How big is its graph search (from s)?

![img-61.jpeg](img-61.jpeg)
# Tree search vs. Graph search

## General Tree Search

**function TREE-SEARCH(problem) returns** a solution, or failure

initialize the **frontier** using the initial state of **problem**

**loop do**

if the **frontier** is empty **then return** failure

choose a leaf **node** and remove it from the **frontier**

if the **node** contains a goal state **then return** the corresponding solution

**expand** the chosen **node**, adding the resulting **nodes** to the **frontier**

**VS.**

## General Graph Search

**function GRAPH-SEARCH(problem) returns** a solution, or failure

initialize the **frontier** using the initial state of **problem**

initialize the **explored set** to be empty

**loop do**

if the **frontier** is empty **then return** failure

choose a leaf **node** and remove it from the **frontier**

if the **node** contains a goal state **then return** the corresponding solution

add the **node** to the **explored set**

**expand** the chosen **node**, adding the resulting **nodes** to the **frontier**

but only if the **node** is not already in the **frontier** or **explored set**
# Search algorithm

**Main question:** which frontier nodes to explore? How to expand as few nodes as possible, while achieving the goal?

- **Search Strategy**
  - A search strategy determines the order in which nodes are expanded.

![img-62.jpeg](img-62.jpeg)
# Properties of Search Methods

Strategies are evaluated along the following criteria:

- ▶ **Completeness:** is the strategy guaranteed to find a solution when there is one?
- ▶ **Time Complexity:** how long does it take to find a solution?
- ▶ **Space Complexity:** how much memory does it require to perform the search?
- ▶ **Optimality:** Does the strategy find the best-quality solution when more than one solution exists?

• Time and space complexity are measured in terms of :

- • $b$ is the branching factor
- • $m$ is the maximum depth
- • solutions at various depths

• Number of nodes in entire tree?

• $1 + b + b^2 + \dots b^m = O(b^m)$

![img-63.jpeg](img-63.jpeg)
# Search Strategies

???

![img-64.jpeg](img-64.jpeg)

What kinds of search algorithms are there?
# Search Algorithms

• Uninformed search algorithms

- Have no knowledge other the problem definition
- Has a start state
- Will recognize the goal state

• Informed search algorithms:

- Finds the solution efficiently
- Leverage information about the environment
- Use a heuristics - An under-estimate of cost to reach the goal
- Or path cost - Distance traveled to current state

![img-65.jpeg](img-65.jpeg)
# Today

## Solving problems by searching

- Problem-solving agents
- Search Problems
- **Uninformed Search Methods**
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening Search
  4. Uniform-Cost Search

![img-66.jpeg](img-66.jpeg)
# Uninformed search strategies

- **Uninformed search** also known as unguided search, blind search, or brute-force search is a search methodology that has no additional information about the domain of the problem apart from the representation of the problem which is usually a tree.
  - Can only traverse state space blindly in hope of somehow hitting a goal state at some point
- **Uninformed search algorithms:**
  - Depth-first Search
  - Breadth-first Search
  - Iterative deepening search
  - Uniform Cost Search
# Today

## Solving problems by searching

- Problem-solving agents
- Search Problems
- Uninformed Search Methods
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening Search
  4. Uniform-Cost Search

![img-67.jpeg](img-67.jpeg)
# 1. Depth-First Search

Depth-First Search (DFS):

- Always expand node at the deepest level of the tree, e.g., one of the most recently generated nodes
- When hit a dead-end, backtrack to last choice
- Frontier can be maintained as a last-in first-out (LIFO) queue (aka. a stack).
- The elements are added to the stack one at a time.
- The one selected and taken off the frontier at any time is the last element that was added.

![img-68.jpeg](img-68.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 0, expanded: 0

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path:[S])}  |

**Strategy:** expand a deepest node first

**Implementation:** Frontier is a LIFO stack

State Space Graph

![img-69.jpeg](img-69.jpeg)

Graph Search
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 0, expanded: 0

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path:[S])}  |
|  S not goal |   |

State Space Graph

![img-70.jpeg](img-70.jpeg)

Graph Search

![img-71.jpeg](img-71.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 1, expanded: 1

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path:[S])}  |
|  S not goal | {(C, path: [S,C]), (B, path: [S,B]), (A, path: [S,A])}  |

State Space Graph

![img-72.jpeg](img-72.jpeg)

Graph Search

![img-73.jpeg](img-73.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 2, expanded: 2

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path:[S])}  |
|  S not goal | {(C, path: [S,C]), (B, path: [S,B]), (A, path: [S,A])}  |
|  A not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (D, path: [S,A,E])}  |

State Space Graph

![img-74.jpeg](img-74.jpeg)

Graph Search

![img-75.jpeg](img-75.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 3, expanded: 3

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path:[S])}  |
|  S not goal | {(C, path: [S,C]), (B, path: [S,B]), (A, path: [S,A])}  |
|  A not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (D, path: [S,A,E])}  |
|  D not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (H, path: [S,A,D,H])}  |

State Space Graph

![img-76.jpeg](img-76.jpeg)

Graph Search

![img-77.jpeg](img-77.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 4, expanded: 3

|  Explored node | Frontier  |
| --- | --- |
|   | {S}  |
|  S not goal | {C, B, A}  |
|  A not goal | {C,B, E, D}  |
|  D not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (H, path: [S,A,D,H])}  |
|  H not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E])} **no expand**  |

State Space Graph

![img-78.jpeg](img-78.jpeg)

Graph Search

![img-79.jpeg](img-79.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 4, expanded: 3

|  Explored node | Frontier  |
| --- | --- |
|   | {S}  |
|  S not goal | {C, B, A}  |
|  A not goal | {C,B, E, D}  |
|  D not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (H, path: [S,A,D,H])}  |
|  H not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E])}  |

State Space Graph

![img-80.jpeg](img-80.jpeg)

Graph Search

![img-81.jpeg](img-81.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 4, expanded: 3

|  Explored node | Frontier  |
| --- | --- |
|   | {S}  |
|  S not goal | {C, B, A}  |
|  A not goal | {C,B, E, D}  |
|  D not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E]), (H, path: [S,A,D,H])}  |
|  H not goal | {(C, path: [S,C]), (B, path: [S,B]), (E, path: [S,A,E])}  |

State Space Graph

![img-82.jpeg](img-82.jpeg)

Graph Search

![img-83.jpeg](img-83.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 5, expanded: 4

|  Explored node | Frontier  |
| --- | --- |
|   | {S}  |
|  S not goal | {C, B, A}  |
|  A not goal | {C,B, E, D}  |
|  D not goal | {C, B, E, H}  |
|  H not goal | {C, B, E}  |
|  E not goal | {(C, path: [S,C]), (B, path: [S,B]), (G, path: [S,A,E, G])}  |

State Space Graph

![img-84.jpeg](img-84.jpeg)

Graph Search

![img-85.jpeg](img-85.jpeg)
# 1. Depth-First Search Example

DFS Search(problem, stack )

# of nodes tested: 6, expanded: 4

|  Explored node | Frontier  |
| --- | --- |
|   | {S}  |
|  S not goal | {C, B, A}  |
|  A not goal | {C,B, E, D}  |
|  D not goal | {C, B, E, H}  |
|  H not goal | {C, B, E}  |
|  E not goal | {C, B, G}  |
|  **G is goal** | **Stop**  |

Expansion order: (S, A, D, H, E, G)

State Space Graph

![img-86.jpeg](img-86.jpeg)

Path: S, A, E, G
Cost: 15

Graph Search

![img-87.jpeg](img-87.jpeg)
# 1. Depth-First Search

**Depth-first search:** In depth-first search, the frontier acts like a last-in first-out queue (a stack). The elements are added to the stack one at a time. The one selected and taken off the frontier at any time is the last element that was added.

![img-88.jpeg](img-88.jpeg)

![img-89.jpeg](img-89.jpeg)

![img-90.jpeg](img-90.jpeg)
# 1. Depth-First Search Example

## Depth-First Search algorithm

**function** DEPTH-FIRST-SEARCH( *problem* ) **returns** a solution, or failure

*node* ← a node with STATE = *problem*.INITIAL-STATE, PATH-COST = 0

**if** *problem*.GOAL-TEST( *node*.STATE) **then return** SOLUTION( *node* )

*frontier* ← a LIFO queue with *node* as the only element

*explored* ← an empty set

**loop do**

**if** EMPTY?( *frontier* ) **then return** failure

*node* ← POP( *frontier* ) /* chooses the deepest node in *frontier* */

add *node*.STATE to *explored*

**for each** *action* **in** *problem*.ACTIONS( *node*.STATE) **do**

*child* ← CHILD-NODE( *problem*, *node*, *action* )

**if** *child*.STATE is not in *explored* or *frontier* **then**

**if** *problem*.GOAL-TEST( *child*.STATE) **then return** SOLUTION( *child* )

*frontier* ← INSERT( *child*, *frontier* )
# 1. DFS Properties

- What nodes DFS expand?

- Some left prefix of the tree.
- Could process the whole tree!
- If $m$ is finite, takes time $O(b^m)$

- How much space does the fringe take?

- Only has siblings on path to root, so $O(bm)$, i.e., linear space!

- Is it complete?

- $m$ could be infinite, so only if we prevent cycles (more later)
- Complete in finite spaces

- Is it optimal?

- No, it finds the “leftmost” solution, regardless of depth or cost

![img-91.jpeg](img-91.jpeg)

![img-92.jpeg](img-92.jpeg)
# Today

## Solving problems by searching

- Problem-solving agents
- Search Problems
- Uninformed Search Methods
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening Search
  4. Uniform-Cost Search

![img-93.jpeg](img-93.jpeg)
## 2. Breadth-First Search

Breadth-First Search (BFS):

- Nodes are expanded in the same order in which they are generated.
- Frontier can be maintained as a First-In, First-Out (FIFO) queue. Thus, the path that is selected from the frontier is the one that was added earliest.
- This approach implies that the paths from the start node are generated in order of the number of arcs in the path.
- One of the paths with the fewest arcs is selected at each stage.

BFS
Looking wide before looking deep

![img-94.jpeg](img-94.jpeg)

![img-95.jpeg](img-95.jpeg)

Queue:

![img-96.jpeg](img-96.jpeg)
## 2. Breadth-First Search Example

BFS_Search(problem, queue )

# of nodes tested: 0, expanded: 0

|  expnd. node | node list  |
| --- | --- |
|   | {(S, path:[S])}  |

Strategy: expand a shallowest node first

Implementation: Fringe/Frontier is a FIFO queue

State Space Graph

![img-97.jpeg](img-97.jpeg)

Graph Search
## 2. Breadth-First Search Example

BFS_Search(problem, queue )

# of nodes tested: 1, expanded: 1

|  Explored node | node list  |
| --- | --- |
|   | {(S, path:[S])}  |
|  S not goal | {(A, path:[S,A]), (B, path:[S,B]), (C, path:[S,C])}  |

State Space Graph

![img-98.jpeg](img-98.jpeg)

Graph Search

![img-99.jpeg](img-99.jpeg)
## 2. Breadth-First Search Example

BFS_Search(problem, queue )

# of nodes tested: 2, expanded: 2

|  Explored node | node list  |
| --- | --- |
|   | {(S, path:[S])}  |
|  S not goal | {(A, path:[S,A]), (B, path:[S,B]), (C, path:[S,C])}  |
|  A not goal | {(B, path:[S,B]), (C, path:[S,C]), (D, path:[S,A,D]), (E, path:[S,A,E])}  |

State Space Graph

![img-100.jpeg](img-100.jpeg)

Graph Search

![img-101.jpeg](img-101.jpeg)
## 2. Breadth-First Search Example

BFS_Search(problem, queue )

# of nodes tested: 3, expanded: 3

|  Explored node | node list  |
| --- | --- |
|   | {(S, path:[S])}  |
|  S not goal | {(A, path:[S,A]), (B, path:[S,B]), (C, path:[S,C])}  |
|  A not goal | {(B, path:[S,B]), (C, path:[S,C]), (D, path:[S,A,D]), (E, path:[S,A,E])}  |
|  B not goal | {(C, path:[S,C]), (D, path:[S,A,D]), (E, path:[S,A,E]), (G, path:[S,B,G])}  |

State Space Graph

![img-102.jpeg](img-102.jpeg)

Graph Search

![img-103.jpeg](img-103.jpeg)
## 2. Breadth-First Search Example

BFS_Search(problem, queue )

# of nodes tested: 4, expanded: 4

|  Explored node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {A, B, C}  |
|  A not goal | {B, C, D, E}  |
|  B not goal | {C, D, E, G}  |
|  C not goal | {(D, path:[S,A,D]), (E, path:[S,A,E]), (G, path:[S,B,G]), **(F, path:[S,C,F])**}  |

State Space Graph

![img-104.jpeg](img-104.jpeg)

Graph Search

![img-105.jpeg](img-105.jpeg)
## 2. Breadth-First Search Example

BFS_Search(problem, queue )

# of nodes tested: 5, expanded: 5

|  Explored node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {A, B, C}  |
|  A not goal | {B, C, D, E}  |
|  B not goal | {C, D, E, G}  |
|  C not goal | {D, E, G, F}  |
|  D not goal | {(E, path:[S,A,E]), (G, path:[S,B,G]), (F, path:[S,C,F]), (H, path:[S,A,D,H])}  |

State Space Graph

![img-106.jpeg](img-106.jpeg)

Graph Search

![img-107.jpeg](img-107.jpeg)
## 2. Breadth-First Search Example

BFS_Search(problem, queue )

# of nodes tested: 6, expanded: 6

|  Explored node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {A, B, C}  |
|  A not goal | {B, C, D, E}  |
|  B not goal | {C, D, E, G}  |
|  C not goal | {D, E, G, F}  |
|  D not goal | {E, G, F, H}  |
|  E not goal | {(G, path:[S,B,G]), (F, path:[S,C,F]), (H, path:[S,A,D,H])}  |

State Space Graph

![img-108.jpeg](img-108.jpeg)

Graph Search

![img-109.jpeg](img-109.jpeg)
## 2. Breadth-First Search Example

BFS_Search(problem, queue )

# of nodes tested: 7, expanded: 6

|  Explored node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {A, B, C}  |
|  A not goal | {B, C, D, E}  |
|  B not goal | {C, D, E, G}  |
|  C not goal | {D, E, G, F}  |
|  D not goal | {E, G, F, H}  |
|  E not goal | {G, F, H, G}  |
|  **G is goal** | **Stop**  |

State Space Graph

![img-110.jpeg](img-110.jpeg)

Path: S, B, G
Cost: 8

Graph Search

![img-111.jpeg](img-111.jpeg)

Expansion order:
(S, A, B, C, D, E, G)
## 2. Breadth-First Search

**Breadth-first search:** In breadth-first search, the frontier acts like a first-in first-out (FIFO) queue. The element selected and removed from the frontier at any given time is the one that was added earliest.

![img-112.jpeg](img-112.jpeg)

![img-113.jpeg](img-113.jpeg)
## 2. BFS pseudo-code

### Breadth-First Search algorithm

**function** BREADTH-FIRST-SEARCH( *problem* ) **returns** a solution, or failure

*node* ← a node with STATE = *problem*.INITIAL-STATE, PATH-COST = 0

**if** *problem*.GOAL-TEST( *node*.STATE) **then return** SOLUTION( *node* )

*frontier* ← a FIFO queue with *node* as the only element

*explored* ← an empty set

**loop do**

**if** EMPTY?( *frontier* ) **then return** failure

*node* ← POP( *frontier* ) /* chooses the shallowest node in *frontier* */

add *node*.STATE to *explored*

**for each** *action* **in** *problem*.ACTIONS( *node*.STATE) **do**

*child* ← CHILD-NODE( *problem*, *node*, *action* )

**if** *child*.STATE is not in *explored* or *frontier* **then**

**if** *problem*.GOAL-TEST(*child*.STATE) **then return** SOLUTION(*child* )

*frontier* ← INSERT( *child*, *frontier* )
## 2. BFS Properties

■ What nodes does BFS expand?

- ■ Processes all nodes above shallowest solution
- ■ Let depth of shallowest solution be $d$
- ■ Search takes time $O(b^d)$

■ How much space does the frontier take?

- ■ Has roughly the last tier, so $O(b^d)$

■ Is it complete?

- ■ $d$ must be finite if a solution exists, so yes!

■ Is it optimal?

- ■ Only if costs are all 1 (1 per step)

![img-114.jpeg](img-114.jpeg)

![img-115.jpeg](img-115.jpeg)
# Quiz: DFS vs BFS

![img-116.jpeg](img-116.jpeg)

- When will BFS outperform DFS?
- When will DFS outperform BFS?

![img-117.jpeg](img-117.jpeg)

![img-118.jpeg](img-118.jpeg)

BFS, the closest elements to the starting location are searched first.

![img-119.jpeg](img-119.jpeg)

DFS, the search proceeds along a continuously deeper path until it hits a barrier and must backtracks to the last decision point.
# DFS vs. BFS

- If you know a solution is not far from the root of the tree, *a breadth first search (BFS) might be better*
- If the tree is very deep and solutions are rare, *depth first search (DFS) might take an extremely long time, but BFS could be faster*
- If the tree is very wide, *a BFS might need to much memory, so it might be completely impractical*
- If solutions are frequent but located deep in the tree, *BFS could be completely impractical*
- If the search tree is very deep *you will need to restrict the search depth for depth first search (DFS)*

|  Scenario | Depth first | Breadth first  |
| --- | --- | --- |
|  Some paths are extremely long, or even infinite | Performs badly | Performs well  |
|  All paths are of similar length | Performs well | Performs well  |
|  All paths are of similar length, and all paths lead to a goal state | Performs well | Wasteful of time and memory  |
|  High branching factor | Performance depends on other factors | Performs poorly  |
# DFS Limites

- Depth first search is incomplete if there is an infinite branch in the search tree.
  - Infinite branches can happen if:
    - paths contain loops
    - infinite number of states and/or operators.
- For problems with infinite (or just very large) state spaces, several variants of depth-first search have been developed:
  - Depth limited search
  - Iterative deepening search
# Outline

## Solving problems by searching

- Problem-solving agents
- Search Problems
- Uninformed Search Methods
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening Search
  4. Uniform-Cost Search

![img-120.jpeg](img-120.jpeg)
## 3.a. Depth Limited Search

- **Limited depth DFS:** just like DFS, except never go deeper than some depth $\ell$
- The nodes at depth $\ell$ are treated as if they had no successors
- If the search reaches a node at depth $\ell$ where the path is not a solution, we backtrack to the next choice point at depth $< \ell$
- Depth-first search can be viewed as a special case of **Depth Limited Search** where $\ell = \infty$
- The depth bound can sometimes be chosen based on knowledge of the problem
# 3.a. Depth Limited Search

![img-121.jpeg](img-121.jpeg)

![img-122.jpeg](img-122.jpeg)

Example: route planning problem

▶ Requires some knowledge of the solution:

- in the route planning problem, the longest route has length $s - 1$, where $s$ is the number of cities (states),
- so we can set $\ell = s - 1$
- 9 cities, depth limit of 8?

▶ What if we choose a limit too small?

- Sacrifice completeness
# 3. Iterative Deepening Search

For the most problems, $\ell$ is unknown.

Iterative Deepening Search (IDS) is a form of depth limited search which progressively increases the bound.

![img-123.jpeg](img-123.jpeg)
### 3. Iterative Deepening Search

- Idea: get DFS's space advantage with BFS's time / shallow-solution advantages

- Run a DFS with depth limit 1. If no solution...
- Run a DFS with depth limit 2. If no solution...
- Run a DFS with depth limit 3 ...
- Until a solution is found

- Solution will be found when $\ell = d$

- Isn't that wastefully redundant?

- Generally most work happens in the lowest level searched, so not so bad!

![img-124.jpeg](img-124.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 1, # of nodes tested: 0, expanded: 0

|  expnd. node | node list  |
| --- | --- |
|  |   |

State Space Graph

![img-125.jpeg](img-125.jpeg)

Graph Search
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 1, # of nodes tested: 0, expanded: 0

|  expnd. node | node list  |
| --- | --- |
|  |   |

State Space Graph

![img-126.jpeg](img-126.jpeg)

Graph Search
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 1, # of nodes tested: 0, expanded: 0

|  expnd. node | node list  |
| --- | --- |
|   | {(S, path: [S])}  |

State Space Graph

![img-127.jpeg](img-127.jpeg)

Graph Search
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 1, # of nodes tested: 1, expanded: 1

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S])}  |
|  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |

State Space Graph

![img-128.jpeg](img-128.jpeg)

Graph Search

![img-129.jpeg](img-129.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 1, # of nodes tested: 2, expanded: 1

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S])}  |
|  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
|  A not goal | {(C, path: [S, C]), (B, path: [S, B])} **no expand**  |

State Space Graph

![img-130.jpeg](img-130.jpeg)

Graph Search

![img-131.jpeg](img-131.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 1, # of nodes tested: 3, expanded: 1

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S])}  |
|  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
|  A not goal | {(C, path: [S, C]), (B, path: [S, B])} **no expand**  |
|  B not goal | {(C, path: [S, C]) **no expand**  |

State Space Graph

![img-132.jpeg](img-132.jpeg)

Graph Search

![img-133.jpeg](img-133.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 1, # of nodes tested: 4, expanded: 1

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S])}  |
|  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
|  A not goal | {(C, path: [S, C]), (B, path: [S, B])} **no expand**  |
|  B not goal | {(C, path: [S, C])} **no expand**  |
|  C not goal | {} **no expand**  |

State Space Graph

![img-134.jpeg](img-134.jpeg)

Graph Search

![img-135.jpeg](img-135.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 1, # of nodes tested: 4, expanded: 1

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S])}  |
|  S not goal | {(C, path: [S, C]), (B, path: [S, B]), (A, path: [S, A])}  |
|  A not goal | {(C, path: [S, C]), (B, path: [S, B])} **no expand**  |
|  B not goal | {(C, path: [S, C])} **no expand**  |
|  C not goal | {} **no expand**  |

Frontier is empty. Increasing depth

State Space Graph

![img-136.jpeg](img-136.jpeg)

Graph Search

![img-137.jpeg](img-137.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

**Depth : 2**, # of nodes tested: 4, expanded: 2

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |

State Space Graph

![img-138.jpeg](img-138.jpeg)

Graph Search
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 2, # of nodes tested: 4, expanded: 2

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |

![img-139.jpeg](img-139.jpeg)

State Space Graph

![img-140.jpeg](img-140.jpeg)

Graph Search
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 2, # of nodes tested: 4, expanded: 2

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |
|  S not goal | {C,B,A}  |

State Space Graph

![img-141.jpeg](img-141.jpeg)

Graph Search

![img-142.jpeg](img-142.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 2, # of nodes tested: 4, expanded: 3

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B,E, D}  |

State Space Graph

![img-143.jpeg](img-143.jpeg)

Graph Search

![img-144.jpeg](img-144.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 2, # of nodes tested: 5, expanded: 3

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B,E, D}  |
|  D not goal | {C,B,E}  |

State Space Graph

![img-145.jpeg](img-145.jpeg)

Graph Search

![img-146.jpeg](img-146.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 2, # of nodes tested: 6, expanded: 3

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |
|  S not goal | {C, B, A}  |
|  A not goal | {C, B, E, D}  |
|  D not goal | {C, B, E}  |
|  E not goal | {C, B}  |

State Space Graph

![img-147.jpeg](img-147.jpeg)

Graph Search

![img-148.jpeg](img-148.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 2, # of nodes tested: 6, expanded: 4

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |
|  S not goal | {C, B, A}  |
|  A not goal | {C, B, E, D}  |
|  D not goal | {C, B, E}  |
|  E not goal | {C, B}  |
|  B not goal | {C, G}  |

State Space Graph

![img-149.jpeg](img-149.jpeg)

Graph Search

![img-150.jpeg](img-150.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 2, # of nodes tested: 7, expanded: 4

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |
|  S not goal | {C, B, A}  |
|  A not goal | {C, B, E, D}  |
|  D not goal | {C, B, E}  |
|  E not goal | {C, B}  |
|  B not goal | {C, G}  |
|  **G is goal** | **Stop**  |

State Space Graph

![img-151.jpeg](img-151.jpeg)

Graph Search

![img-152.jpeg](img-152.jpeg)
# 3. Iterative Deepening Search Example

IDS Search(problem, stack )

Depth : 2, # of nodes tested: 7, expanded: 4

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |
|  S not goal | {C,B,A}  |
|  A not goal | {C,B} no expand  |
|  B not goal | {C} no expand  |
|  C not goal | {} no expand  |
|  S not goal | {C, B, A}  |
|  A not goal | {C, B, E, D}  |
|  D not goal | {C, B, E}  |
|  E not goal | {C, B}  |
|  B not goal | {C, G}  |
|  **G is goal** | **Stop**  |

State Space Graph

![img-153.jpeg](img-153.jpeg)

Graph Search

![img-154.jpeg](img-154.jpeg)

Path: S, B, G
Cost: 8
# 3. Iterative deepening search Properties

# - ■ **Time?**

- ■ $O(b^d)$, where $b$ is the branching factor and $d$ is the depth of the shallowest solution.

# - ■ **Space?**

- ■ $O(bd)$

# - ■ **Is it complete?**

- ■ yes

# - ■ **Is it optimal?**

- ■ Yes, if step cost = 1

![img-155.jpeg](img-155.jpeg)
### 3. Iterative deepening search Properties

- Has the advantages of BFS
  - Complete
  - Optimal (if the edges have identical costs)
- Has the advantages of DFS
  - Linear space complexity: $O(bd)$
- Wasteful?
  - because nodes near the top of the search tree are generated multiple times
- It turns out this is NOT very costly
  - For a tree with (nearly) the same branching factor at each level, most of the nodes are in the bottom level
- Worst case time complexity: $O(b^d)$
# 3. Iterative Deepening Search algorithm

# Iterative Deepening Search pseudocode

function ITERATIVE-DEEPENING-SEARCH(problem) returns a solution node or failure

for depth = 0 to ∞ do

result ← DEPTH-LIMITED-SEARCH(problem, depth)

if result ≠ cutoff then return result

function DEPTH-LIMITED-SEARCH(problem, ℓ) returns a node or failure or cutoff

frontier ← a LIFO queue (stack) with NODE(problem.INITIAL) as an element

result ← failure

while not IS-EMPTY(frontier) do

node ← POP(frontier)

if problem.IS-GOAL(node.STATE) then return node

if DEPTH(node) > ℓ then

result ← cutoff

else if not IS-CYCLE(node) do

for each child in EXPAND(problem, node) do

add child to frontier

return result
# Outline

## Solving problems by searching

- Problem-solving agents
- Search Problems
- Uninformed Search Methods
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening Search
  4. Uniform-Cost Search

![img-156.jpeg](img-156.jpeg)
# Search with varying step costs

![img-157.jpeg](img-157.jpeg)

- BFS finds the path with the fewest steps, but **does not always find the cheapest path**
# Outline

## Solving problems by searching

- Problem-solving agents
- Search Problems
- Uninformed Search Methods
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening Search
  4. Uniform-Cost Search

![img-158.jpeg](img-158.jpeg)
## 4. Uniform Cost Search (UCS)

- For each frontier node, save the total cost of the path from the initial state to that node
- Expand the frontier node with the lowest path cost
- **Implementation:** *frontier* is a priority queue ordered by path cost
- Equivalent to breadth-first if step costs all equal
- Equivalent to Dijkstra's algorithm in general

![img-159.jpeg](img-159.jpeg)
# 4. Uniform Cost Search Example

UCS Search(problem, priorityQueue )

# of nodes tested: 0, expanded: 0

|  expnd. node | node list  |
| --- | --- |
|   | {S}  |

**Strategy:** expand a cheapest node first

**Implementation:** Frontier is a priority queue (priority: cumulative cost)

State Space Graph

![img-160.jpeg](img-160.jpeg)

Graph Search
# 4. Uniform Cost Search Example

UCS Search(problem, priorityQueue )

# of nodes tested:1, expanded: 1

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S], cost: 0}  |
|  S not goal | {(B, [S,B], 2), (C, [S,C], 4), (A, [S,A], 5)}  |

State Space Graph

![img-161.jpeg](img-161.jpeg)

Graph Search

![img-162.jpeg](img-162.jpeg)
# 4. Uniform Cost Search Example

UCS Search(problem, priorityQueue )

# of nodes tested: 2, expanded: 2

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S], cost: 0}  |
|  S not goal | {(B, [S,B], 2), (C, [S,C], 4), (A, [S,A], 5)}  |
|  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |

State Space Graph

![img-163.jpeg](img-163.jpeg)

Graph Search

![img-164.jpeg](img-164.jpeg)
# 4. Uniform Cost Search Example

UCS Search(problem, priorityQueue )

# of nodes tested: 3, expanded: 3

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S], cost: 0)}  |
|  S not goal | {(B, [S,B], 2), (C, [S,C], 4), (A, [S,A], 5)}  |
|  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
|  C not goal | {(A, [S,A], 5), (G, [S, B, G], 8), (F, [S, C, F], 6)}  |

State Space Graph

![img-165.jpeg](img-165.jpeg)

Graph Search

![img-166.jpeg](img-166.jpeg)
# 4. Uniform Cost Search Example

UCS Search(problem, priorityQueue )

# of nodes tested: 4, expanded: 4

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S], cost: 0)}  |
|  S not goal | {(B, [S,B], 2), (C, [S,C], 4), (A, [S,A], 5)}  |
|  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
|  C not goal | {(A, [S,A], 5), (G, [S, B, G], 8), (F, [S, C, F], 6)}  |
|  A not goal | {(G, [S, B, G], 8), (F, [S, C, F], 6), (D, [S, A, D], 14), (E, [S, A, E], 9)}  |

State Space Graph

![img-167.jpeg](img-167.jpeg)

Graph Search

![img-168.jpeg](img-168.jpeg)
# 4. Uniform Cost Search Example

UCS Search(problem, priorityQueue )

# of nodes tested: 5, expanded: 5

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S], cost: 0}  |
|  S not goal | {(B, [S,B], 2),(C, [S,C], 4),(A, [S,A], 5)}  |
|  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
|  C not goal | {(A, [S,A], 5), (G, [S, B, G], 8), (F, [S, C, F], 6)}  |
|  A not goal | {(G, [S, B, G], 8), (F, [S, C, F], 6), (D, [S, A, D], 14), (E, [S, A, E], 9)}  |
|  F not goal | {(G, [S, B, G], 8), (D, [S, A, D], 14), (E, [S, A, E], 9), (G, [S, C, F, G], 7)}  |

State Space Graph

![img-169.jpeg](img-169.jpeg)

Graph Search

![img-170.jpeg](img-170.jpeg)

Remove the higher-cost of identical nodes on the queue and save memory. However, UCS is optimal even if this is not done, since lower-cost nodes sort to the front.
## 4. Uniform Cost Search Example

UCS Search(problem, priorityQueue)

# of nodes tested: 6, expanded: 5

|  Explored node | Frontier  |
| --- | --- |
|   | {(S, path: [S], cost: 0}  |
|  S not goal | {(B, [S,B], 2),(C, [S,C], 4),(A, [S,A], 5)}  |
|  B not goal | {(C, [S,C], 4), (A, [S,A], 5), (G, [S, B, G], 8)}  |
|  C not goal | {(A, [S,A], 5), (G, [S, B, G], 8), (F, [S, C, F], 6)}  |
|  A not goal | {(G, [S, B, G], 8), (F, [S, C, F], 6), (D, [S, A, D], 14), (E, [S, A, E], 9)}  |
|  F not goal | {(G, [S, B, G], 8), (D, [S, A, D], 14), (E, [S, A, E], 9), (G, [S, C, F, G], 7)}  |
|  G is goal | Stop  |

State Space Graph

![img-171.jpeg](img-171.jpeg)

Graph Search

![img-172.jpeg](img-172.jpeg)
# 4. UCS algorithm

# Best first search

function BEST-FIRST-SEARCH(problem, f) returns a solution node or failure
    node ← NODE(STATE=problem.INITIAL)
    frontier ← a priority queue ordered by f, with node as an element
    reached ← a lookup table, with one entry with key problem.INITIAL and value node
    while not IS-EMPTY(frontier) do
        node ← POP(frontier)
        if problem.IS-GOAL(node.STATE) then return node
        for each child in EXPAND(problem, node) do
            s ← child.STATE
            if s is not in reached or child.PATH-COST < reached[s].PATH-COST then
                reached[s] ← child
                add child to frontier
    return failure

function EXPAND(problem, node) yields nodes
    s ← node.STATE

    for each action in problem.ACTIONS(s) do
        s' ← problem.RESULT(s, action)
        cost ← node.PATH-COST + problem.ACTION-COST(s, action, s')
    yield NODE(STATE=s', PARENT=node, ACTION=action, PATH-COST=cost)

# Uniform Cost Search

function UNIFORM-COST-SEARCH(problem) returns a solution node, or failure
return BEST-FIRST-SEARCH(problem, PATH-COST)
# 4. UCS Properties

What nodes does UCS expand?

- Processes all nodes with cost less than cheapest solution!
- If that solution costs $C^*$ and arcs cost at least $\varepsilon$, then the “effective depth” is roughly $C^*/\varepsilon$
- Takes time $O(b^{C*/\varepsilon})$ (exponential in effective depth)
- This can be greater than $O(b^d)$: the search can explore long paths consisting of small steps before exploring shorter paths consisting of larger steps

How much space does the frontier take?

- Has roughly the last tier, so $O(b^{C*/\varepsilon})$

Is it complete?

- Assuming best solution has a finite cost and minimum arc cost is positive, yes!

Is it optimal?

- Yes! (Proof next lecture via A*)

![img-173.jpeg](img-173.jpeg)
# 4. Uniform Cost Issues

- ■ **Strategy:** expand lowest path cost
- ■ **The good:** UCS is complete and optimal!
- ■ **The bad:**
  - ■ Explores options in every “direction”
  - ■ No information about goal location

![img-174.jpeg](img-174.jpeg)

![img-175.jpeg](img-175.jpeg)
# Review: Uninformed search strategies

- A **search strategy** is defined by picking the order of node expansion
- **Uninformed** search strategies use only the information available in the problem definition
  - Breadth-first search
  - Depth-first search
  - Iterative deepening search
  - Uniform-cost search
  - Bidirectional Search
# BFS/DFS/IDS/UCS

• Breadth-first search

- • **Good**: optimal, works well when many options, but not many actions required
- • **Bad**: assumes all actions have equal cost

• Depth-first search

- • **Good**: memory-efficient, works well when few options, but lots of actions required
- • **Bad**: not optimal, can run infinitely, assumes all actions have equal cost

• Iterative deepening search

- • **Good**: optimal, memory-efficient, and adaptable to different situations
- • **Bad**: redundant work, assume all actions have equal cost,

• Uniform-cost search

- • **Good**: optimal, handles variable-cost actions
- • **Bad**: explores all options, no information about goal location

**Basically Dijkstra's Algorithm!**
# Evaluation of search algorithms

|  Criterion | Breadth-First | Uniform-Cost | Depth-First | Depth-Limited | Iterative Deepening  |
| --- | --- | --- | --- | --- | --- |
|  Complete? | Yes^{1} | Yes^{1,2} | No | No | Yes^{1}  |
|  Optimal cost? | Yes^{3} | Yes | No | No | Yes^{3}  |
|  Time | $$O(b^d)$$ | $$O(b^{1+\lfloor C^*/\epsilon \rfloor})$$ | $$O(b^m)$$ | $$O(b^\ell)$$ | $$O(b^d)$$  |
|  Space | $$O(b^d)$$ | $$O(b^{1+\lfloor C^*/\epsilon \rfloor})$$ | $$O(bm)$$ | $$O(b\ell)$$ | $$O(bd)$$  |

- b is the branching factor; m is the maximum depth of the search tree; d is the depth of the shallowest solution, or is m when there is no solution; ℓ is the depth limit.
- Superscript caveats are as follows: ¹ complete if b is finite, and the state space either has a solution or is finite. ² complete if all action costs are ≥ ε > 0; ³ cost-optimal if action costs are all identical.
# Search Gone Wrong?

Still not as smart as it could be...

Can we do better?

![img-176.jpeg](img-176.jpeg)
# Incorporating goal information

**How to efficiently solve search problems with variable-cost actions, using information about the goal state?**

This is the motivation behind **informed search**, which uses problem-specific knowledge to try and find solutions more efficiently
