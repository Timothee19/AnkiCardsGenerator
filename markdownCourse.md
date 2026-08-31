![img-0.jpeg](img-0.jpeg)

Raafat Talhouk

2025-2026

## Chapitre 2 : Lebesgue Integral

### Contents

|  **1** | **Introduction** | **4**  |
| --- | --- | --- |
|  **2** | **Motivations and limitations of the Riemann integral** | **4**  |
|  2.1 | Recall of the Riemann integral . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 4  |
|  2.2 | A famous limitation: the indicator function of rationals . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 5  |
|  2.3 | Another limitation: passing to the limit in a sequence of functions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 5  |
|  2.4 | Towards a new approach . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 6  |
|  **3** | **Measure and σ-Algebras** | **6**  |
|  3.1 | σ-Algebras . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 6  |
|  3.2 | Measures . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 7  |
|  3.3 | Measured Spaces . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 9  |
|  3.4 | Key ideas to remember . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 9  |
|  **4** | **Measurable Functions** | **9**  |
|  4.1 | Definition . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 9  |
|  4.2 | Examples of measurable functions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 10  |
|  4.3 | Stability of measurable functions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 10  |
|  4.4 | Negligible sets and "almost everywhere" property . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 13  |
|  4.5 | Why is measurability important? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 14  |
|  **5** | **Integral for the Dirac and counting measures** | **14**  |
|  **6** | **Integral of simple functions** | **15**  |
|  6.1 | Definition . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 15  |
|  6.2 | Definition of the integral of a simple function . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 16  |
|  6.3 | Simple example . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 16  |
|  6.4 | Properties of the integral of simple functions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 16  |
|  6.5 | Why start with simple functions? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 18  |
|  **7** | **Definition of the Lebesgue integral for a non-negative measurable function** | **18**  |
| --- | --- | --- |
|  7.1 | Non-negative measurable functions | 18  |
|  7.2 | Approximation by simple functions | 18  |
|  7.3 | Definition of the integral | 20  |
|  7.4 | Example | 20  |
|  7.5 | Fundamental properties | 21  |
|  7.6 | Summary | 22  |
|  **8** | **Integral of General Functions** | **22**  |
|  8.1 | Positive Part and Negative Part | 22  |
|  8.2 | Definition of the Integral | 23  |
|  8.3 | Examples | 23  |
|  8.4 | Summary to Remember | 23  |
|  **9** | **Fundamental Properties of the Lebesgue Integral** | **23**  |
|  9.1 | Linearity | 24  |
|  9.2 | Monotonicity | 24  |
|  9.3 | Fatou's Lemma | 25  |
|  9.4 | Lebesgue's Dominated Convergence Theorem | 26  |
|  **10** | **Examples and Counter examples** | **28**  |
|  10.1 | Continuous function: $f(x)\; =\; x$ | 28  |
|  10.2 | Indicator function of the rationals | 28  |
|  10.3 | Unbounded function: $f(x)\; =\; \backslash frac\{1\}\{\backslash sqrt\{x\}\}$ | 28  |
|  10.4 | Non-integrable function: $f(x)\; =\; \backslash frac\{1\}\{x\}$ on $(0,1]$ | 28  |
|  10.5 | Sequence of functions: $f_n(x)\; =\; n\cdot\; \backslash left[\; 0,\; \backslash frac\{1\}\{n\}\;](x)$ | 29  |
|  **11** | **$L^p(\Omega)$ Space** | **29**  |
|  11.1 | Definition and First Properties | 29  |
|  11.2 | Fundamental Inequalities | 30  |
|  11.3 | Density Results | 32  |
|  11.4 | $L^p$ on a Measured Space $(X,\; \mathscr{A},\; \mu)$ | 32  |
|  11.5 | Summary to Remember | 32  |
|  **12** | **Applications of the Lebesgue Integral** | **33**  |
|  12.1 | Probability and Random Variables | 33  |
|  12.2 | Other Application Areas | 33  |
|  12.3 | Summary | 33  |
|  **13** | **Product Measures and Tonelli and Fubini Theorems** | **34**  |
|  13.1 | Product Measures | 34  |
|  13.2 | Tonelli's Theorem (case of positive functions) | 35  |
|  13.3 | Fubini's Theorem (case of integrable functions) | 36  |
|  13.4 | Counterexample to Fubini: non-integrable function | 36  |
|  13.5 | Summary to remember | 37  |
# 14 Change of Variables Theorem 37

14.1 Statement of the theorem in \(\mathbb{R}^n\) 37
14.2 Example 1: Polar coordinates in \(\mathbb{R}^2\) 37
14.3 Example 2: Cylindrical coordinates in \(\mathbb{R}^3\) 38
14.4 Example 3: Spherical coordinates in \(\mathbb{R}^3\) 38
14.5 Example 4: Affine change in \(\mathbb{R}^n\) 39
14.6 Summary to remember 39

# A Appendix: Comparison between the Riemann and Lebesgue Integrals 40

A.1 Philosophy of the two approaches 40
A.2 Compatibility case 41
A.3 Functions integrable in the Lebesgue sense but not Riemann . 41

# B Appendix: Support of a measurable function 41

# C Appendix: Pushforward measure 42

# D Appendix: Duality in the spaces \(L^p (\Omega)\) 42
# 1 Introduction

The Lebesgue integral is a generalization of the Riemann integral, which students usually encounter in high school and during the first years of undergraduate studies. While the Riemann integral gives a meaning to the area under a curve, it quickly shows its limitations when we want to integrate more general functions, such as those with too many discontinuities.

At the beginning of the 20th century, Henri Lebesgue developed a new way of approaching integration, based not on subdivisions of the x-axis (as in Riemann's method), but on the measure of the sets of values taken by a function. This new approach allows the integration of a much larger class of functions and possesses powerful convergence properties.

The goal of this chapter is to introduce this new integral step-by-step, relying on intuition, simple examples, and the main ideas that form the foundation of modern analysis.

# 2 Motivations and limitations of the Riemann integral

## 2.1 Recall of the Riemann integral

The Riemann integral is based on the following idea: to compute the area under a curve f defined on an interval [a, b], we divide this interval into small subintervals, then sum the areas of rectangles approximating the curve. If this sum converges as the subdivisions get finer, we say that f is Riemann integrable.

![img-1.jpeg](img-1.jpeg)

Figure 1: Example of a function to integrate over [a, b].
![img-2.jpeg](img-2.jpeg)

Figure 2: Left Riemann sums $$\sum_{k=0}^{n-1} f(a + k\Delta x)\Delta x$$: as the subdivision is refined ($$\Delta x \to 0$$), the sum of the rectangle areas converges to $$\int_{a}^{b} f(x) \, dx$$, if $$f$$ is Riemann integrable.

However, this method relies heavily on the continuity of the function or, at least, on the “smallness” of its discontinuities.

## 2.2 A famous limitation: the indicator function of rationals

Consider the function defined on $$[0, 1]$$:

$$f(x) = \mathbf{1}_{\mathbb{Q} \cap [0, 1]}(x) = \begin{cases} 1 & \text{if } x \in \mathbb{Q} \cap [0, 1], \\ 0 & \text{otherwise}. \end{cases}$$

It is the indicator function of the rational numbers in $$[0, 1]$$. It takes the value 1 on rationals, and 0 on irrationals.

- It is discontinuous everywhere.
- Every interval contains infinitely many rationals and irrationals.

This function is not Riemann integrable, because its lower and upper integrals are:

$$\int_{0}^{1} f(x) \, dx = 0 \quad \text{and} \quad \overline{\int_{0}^{1}} f(x) \, dx = 1.$$

Thus, the Riemann integral cannot exist in this case.

## 2.3 Another limitation: passing to the limit in a sequence of functions

Consider the sequence $$(f_n)$$ defined by:

$$f_n(x) = \begin{cases} n & \text{if } 0 \le x \le \frac{1}{n}, \\ 0 & \text{otherwise}. \end{cases}$$
Each $f_n$ is Riemann integrable on $[0, 1]$, and we have:

$$\int_0^1 f_n(x) \, dx = 1 \quad \text{for all } n.$$

But when $n \to \infty$, $f_n(x) \to 0$ for all $x > 0$, and $f_n(0) = n \to \infty$, so:

$$f_n(x) \longrightarrow 0 \quad \text{for all } x \in (0, 1].$$

We might expect that the limit of the integral equals the integral of the limit, i.e., 0. But here, this is not the case: the interchange of limit and integral fails.

The Lebesgue integral allows, under simple conditions, to justify this type of interchange.

## 2.4 Towards a new approach

These examples show that the Riemann integral, while very intuitive, has limitations. It is not suited for highly discontinuous functions, nor for certain limit operations (like sequences of functions).

The Lebesgue integral will allow us:

to integrate very "irregular" functions;
to easily interchange limits and integrals (under certain conditions);
to handle cases impossible for Riemann's method.

We will therefore start with some fundamental tools: measure theory and measurable functions.

## 3 Measure and $\sigma$-Algebras

Before defining the Lebesgue integral, we need to understand how to “measure” sets in a rigorous way. This is the purpose of measure theory.

### 3.1 $\sigma$-Algebras

Definition 3.1. Let $X$ be a non-empty set. A $\sigma$-algebra $\mathscr{A}$ on $X$ is a collection of subsets of $X$ such that:

1. \(X\in \mathcal{A}\)
2. If \(A \in \mathcal{A}\), then \(A^c = X \setminus A \in \mathcal{A}\);
3. If \((A_{n})_{n\in \mathbb{N}}\subset \mathcal{A}\), then \(\bigcup_{n = 0}^{\infty}A_n\in \mathcal{A}\)

In other words, a $\sigma$-algebra is closed under complements and countable unions. It is therefore also closed under countable intersections.
Example 3.2. On $X = \{1, 2\}$, the following collection is a $\sigma$-algebra:

$$\mathscr{A} = \{\emptyset, \{1\}, \{2\}, \{1, 2\}\}.$$

On $\mathbb{R}$, the most important example is the Borel $\sigma$-algebra, generated by open intervals $(a, b)$. It contains all standard intervals, countable sets, etc.

Definition 3.3 (Borel $\sigma$-algebra on $\mathbb{R}^n$). The Borel $\sigma$-algebra on $\mathbb{R}^n$, denoted $\mathscr{B}(\mathbb{R}^n)$, is the $\sigma$-algebra generated by the open sets of $\mathbb{R}^n$ (for the usual topology). It contains all open and closed sets, intervals, and is stable under countable unions, countable intersections, and complements.

Definition 3.4 (Borel $\sigma$-algebra on an open set $\Omega \subset \mathbb{R}^n$). Let $\Omega$ be an open set in $\mathbb{R}^n$. The Borel $\sigma$-algebra of $\Omega$, denoted $\mathscr{B}(\Omega)$, is the $\sigma$-algebra induced by $\mathscr{B}(\mathbb{R}^n)$ on $\Omega$, that is:

$$\mathscr{B}(\Omega) = \{A \cap \Omega \mid A \in \mathscr{B}(\mathbb{R}^n)\}.$$

In other words, it contains intersections of Borel sets of $\mathbb{R}^n$ with $\Omega$.

## 3.2 Measures

Definition 3.5. Let $\mathscr{A}$ be a $\sigma$-algebra on a set $X$. A mapping $\mu : \mathscr{A} \to [0, +\infty]$ is called a measure if:

1. $\mu(\emptyset) = 0$;

2. $\mu$ is $\sigma$-additive: for every sequence $(A_n)_{n \in \mathbb{N}}$ of disjoint sets in $\mathscr{A}$, we have:

$$\mu \left( \bigcup_{n=0}^{\infty} A_n \right) = \sum_{n=0}^{\infty} \mu(A_n).$$

Example 3.6 (Dirac Measure). Let $X$ be a set and $x_0 \in X$ a fixed point. The Dirac measure at $x_0$, denoted $\delta_{x_0}$, on $(X, \mathscr{P}(X))$ is defined by:

$$\delta_{x_0}(A) = \begin{cases} 1 & \text{if } x_0 \in A, \\ 0 & \text{if } x_0 \notin A, \end{cases} \quad \text{for all } A \subset X \text{ (i.e., for all } A \in \mathscr{P}(X)).$$

Why $\delta_{x_0}$ is a positive measure.

- \(\delta_{x_0}(\emptyset) = 0\) since \(x_0 \notin \emptyset\).
- Let \((A_{n})_{n\in \mathbb{N}}\) be a sequence of pairwise disjoint sets. Then:

$$\delta_{x_0} \left( \bigcup_{n=0}^{\infty} A_n \right) = \begin{cases} 1 & \text{if } x_0 \in \bigcup_{n=0}^{\infty} A_n, \\ 0 & \text{otherwise.} \end{cases}$$

But $x_0 \in \bigcup_{n=0}^{\infty} A_n$ if and only if there exists a unique $n_0$ such that $x_0 \in A_{n_0}$ (since the $A_n$ are disjoint). Therefore:

$$\sum_{n=0}^{\infty} \delta_{x_0}(A_n) = \begin{cases} 1 & \text{if } x_0 \in A_{n_0} \text{ for a unique } n_0, \\ 0 & \text{otherwise.} \end{cases}$$

Hence:

$$\delta_{x_0} \left( \bigcup_{n=0}^{\infty} A_n \right) = \sum_{n=0}^{\infty} \delta_{x_0}(A_n).$$
Thus, $\delta_{x_0}$ is a positive measure.

Example 3.7 (Counting Measure). Let $X$ be any set. The counting measure $\mu$ on $(X, \mathscr{P}(X))$ is defined by:

$$\mu(A) = \begin{cases} \text{the number of elements of } A & \text{if } A \text{ is finite,} \\ +\infty & \text{if } A \text{ is infinite,} \end{cases} \quad \text{for all } A \in \mathscr{P}(X).$$

Why $\mu$ is a positive measure.

- $\mu(\emptyset) = 0$.
- Let $(A_n)_{n \in \mathbb{N}}$ be a family of pairwise disjoint sets. Then:

$$\mu \left( \bigcup_{n=0}^{\infty} A_n \right) = \sum_{n=0}^{\infty} \mu(A_n),$$

because the elements of $\bigcup A_n$ are all distinct and each belongs to exactly one $A_n$. Thus, we simply count the elements in each $A_n$ and sum them.

Therefore, $\mu$ is indeed a positive measure on $(X, \mathscr{P}(X))$.

Example 3.8 (Intuitive approach to length: Lebesgue measure on $\mathbb{R}$). The Lebesgue measure on $\mathbb{R}$, denoted $\lambda$, is the unique measure such that:

- It assigns to each interval $[a, b] \subset \mathbb{R}$ its length:

$$\lambda([a, b]) = b - a.$$

- It is translation-invariant: for all $x \in \mathbb{R}$, $\lambda(A + x) = \lambda(A)$.

It extends to a well-defined measure on the Borel $\sigma$-algebra of $\mathbb{R}$ (and then to a larger $\sigma$-algebra called the Lebesgue $\sigma$-algebra).

More generally: Lebesgue measure on $\mathbb{R}^N$.

Example 3.9 (Lebesgue measure on $\mathbb{R}^N$ – intuitive approach). The Lebesgue measure on $\mathbb{R}^N$ generalizes the notions of length (in 1D, see Example 3.8), area (in 2D), or volume (in 3D and higher) to much more general sets than just boxes or regular domains.

Intuitively, the Lebesgue measure $\lambda^N$ of a set $A \subset \mathbb{R}^N$ represents its geometric “size,” even if $A$ is highly irregular.

It is constructed so that:

- The measure of a box $I = \prod_{i=1}^N [a_i, b_i]$ is the product of its side lengths: $\lambda^N(I) = \prod_{i=1}^N (b_i - a_i)$.
- It is additive on disjoint sets: the measure of a disjoint union is the sum of the measures.
- It is translation-invariant: for all $x \in \mathbb{R}^N$, $\lambda^N(A + x) = \lambda^N(A)$.

Definition 3.10. A measurable space is a pair $(X, \mathscr{A})$ where:

- $X$ is a set,
- $\mathscr{A}$ is a $\sigma$-algebra on $X$.
### 3.3 Measured Spaces

Definition 3.11. A measured space is a triple $(X, \mathscr{A}, \mu)$ where:

- $X$ is a set,
- $\mathscr{A}$ is a $\sigma$-algebra on $X$,
- $\mu$ is a measure on $\mathscr{A}$.

This is the framework in which we can define measurable functions and then integrate them.

Remark 3.12. The set of functions we can integrate depends on the chosen measure. The Lebesgue integral is therefore defined with respect to a measure.

### 3.4 Key ideas to remember

- A $\sigma$-algebra specifies the “measurable” sets (compatible with the measure).
- A measure gives meaning to the “size” or “volume” of these sets.
- Lebesgue measure is the most common in real analysis.

We will now define what a measurable function is: in other words, a function well adapted to the measure, which we can integrate.

## 4 Measurable Functions

The Lebesgue integral does not apply to all functions, but only to those that are well adapted to the measure defined on the domain. These functions are called measurable functions.

### 4.1 Definition

Definition 4.1. Let $(X, \mathscr{A})$ be a measurable space (i.e., $X$ equipped with a $\sigma$-algebra $\mathscr{A}$), and let $f: X \to \mathbb{R} \cup \{+\infty, -\infty\} = \overline{\mathbb{R}}$ be a function.

We say that $f$ is measurable (with respect to $\mathscr{A}$) if for every real number $a \in \mathbb{R}$, the set

$$\{x \in X \mid f(x) > a\}$$

belongs to $\mathscr{A}$.

Remark 4.2. We could replace the condition "$f(x) > a$" by "$f(x) \geq a$", "$f(x) < a$", or "$f(x) \leq a$": these are equivalent for defining measurability.
### 4.2 Examples of measurable functions

Example 4.3. Any continuous function \( f: \mathbb{R} \to \mathbb{R} \) is measurable (with respect to the Borel \( \sigma \)-algebra).

Solution. For a continuous \( f \), the set \( f^{-1}(]a, +\infty[) = \{x \in \mathbb{R} \mid f(x) > a\} \) is open for all \( a \in \mathbb{R} \) and hence Borel measurable.

Example 4.4. The indicator function \(\mathbf{1}_A\) of a measurable set \(A\in \mathcal{A}\), defined by:

\[
\mathbf {1} _ {A} (x) = \left\{ \begin{array}{l l} 1 & \text { if } x \in A, \\ 0 & \text { otherwise }, \end{array} \right.
\]

is measurable.

Solution. If \(a < 0\), then \(\{x \mid \mathbf{1}_A(x) > a\} = \mathbb{R}\), which is measurable.

- If \(0 \leq a < 1\), then \(\{x \mid \mathbf{1}_A(x) > a\} = A\), which is measurable by assumption.
- If \(a \geq 1\), then \(\{x \mid \mathbf{1}_A(x) > a\} = \emptyset\), which is measurable.

In all cases, the preimage set \(\{x\mid \mathbf{1}_A(x) > a\}\) is measurable. Therefore, \(\mathbf{1}_A\) is measurable.

□

Example 4.5. Any step (simple) function (piecewise constant on measurable sets) is measurable. Recall that \( f \) is a step function on \( [x_0, x_n] \) if

\[
f (x) = \sum_ {k = 1} ^ {n} a _ {k} \mathbf {1} _ {(x _ {k - 1}, x _ {k} ]} (x)
\]

Solution. This follows from the previous example and item 1 of Property 4.7.

### 4.3 Stability of measurable functions

Measurable functions are stable under many usual operations:

Theorem 4.6 (Stability under Composition). Let \((X, \mathcal{A})\), \((Y, \mathcal{B})\), and \((Z, \mathcal{C})\) be three measurable spaces. If \(f: X \to Y\) is \(\mathcal{A} / \mathcal{B}\)-measurable and \(g: Y \to Z\) is \(\mathcal{B} / \mathcal{C}\)-measurable, then the composition \(g \circ f: X \to Z\) is \(\mathcal{A} / \mathcal{C}\)-measurable.

Proof. Let \( C \in \mathcal{C} \). Since \( g \) is \( \mathcal{B} / \mathcal{C} \)-measurable, we have \( g^{-1}(C) \in \mathcal{B} \). Because \( f \) is \( \mathcal{A} / \mathcal{B} \)-measurable, the preimage of any set in \( \mathcal{B} \) under \( f \) belongs to \( \mathcal{A} \), hence \( f^{-1}(g^{-1}(C)) \in \mathcal{A} \). By the elementary property of preimages,

\[
(g \circ f) ^ {- 1} (C) = f ^ {- 1} \bigl (g ^ {- 1} (C) \bigr).
\]

Thus, \((g\circ f)^{-1}(C)\in \mathcal{A}\) for every \(C\in \mathcal{C}\), which proves that \(g\circ f\) is \(\mathcal{A} / \mathcal{C}\)-measurable.

Property 4.7 (Stability under elementary operations). Let \( f \) and \( g \) be two measurable functions from \( X \) to \( \mathbb{R} \). Then:

1. \(f + g\) is measurable.
2. \(f \cdot g\) is measurable.
3. \(|f|\) is measurable.
4. \(\min (f,g)\) and \(\max (f,g)\) are measurable.

Proof. The key fact in all these proofs is: if $f$ is measurable, then for all $a \in \mathbb{R}$, the set $\{x \in X \mid f(x) > a\}$ is measurable and conversely.

1. Measurability of $f + g$:

Let $a \in \mathbb{R}$. We want to show:

$$\{x \mid f(x) + g(x) > a\} \in \mathscr{A}.$$

We can write:

$$\{x \mid f(x) + g(x) > a\} = \bigcup_{q \in \mathbb{Q}} (\{x \mid f(x) > q\} \cap \{x \mid g(x) > a - q\}).$$

This union is countable since $\mathbb{Q}$ is countable. As $f$ and $g$ are measurable, the sets $\{x \mid f(x) > q\}$ and $\{x \mid g(x) > a - q\}$ are measurable. Intersections of measurable sets are measurable, and countable unions of measurable sets are measurable. Therefore, $f + g$ is measurable.

2. Measurability of $f \cdot g$:

Since continuous functions are measurable, and $f \cdot g$ can be expressed as the limit of combinations of $f$ and $g$, this suffices. Alternatively, one can use:

$$fg = \frac{1}{4} \left[ (f + g)^2 - (f - g)^2 \right],$$

and note composition sums, differences, and the square function (continuous) preserve measurability.

3. Measurability of $|f|$: We use the following criterion: a function $h$ is measurable if, for every $a \in \mathbb{R}$,

$$\{x \in X : h(x) < a\} \in \mathcal{A}.$$

- If $a \le 0$, then

$$\{x \in X : |f(x)| < a\} = \varnothing \in \mathcal{A}.$$

- If $a > 0$, then

$$\{x \in X : |f(x)| < a\} = f^{-1}((-a, a)).$$

Now $(-a, a)$ is an open interval of $\mathbb{R}$, hence a Borel set. Since $f$ is measurable, $f^{-1}((-a, a)) \in \mathcal{A}$.

Thus, for every $a \in \mathbb{R}$, the set $\{x \in X : |f(x)| < a\}$ belongs to $\mathcal{A}$. We conclude that $|f|$ is measurable.

4. Measurability of $\min(f, g)$ and $\max(f, g)$:

We use the formulas:

$$\min(f, g) = \frac{1}{2}(f + g - |f - g|), \quad \max(f, g) = \frac{1}{2}(f + g + |f - g|).$$

Since $+$, $-$, and $|\cdot|$ preserve measurability, $\min(f, g)$ and $\max(f, g)$ are measurable.
Theorem 4.8 (Stability of limit operations; complete space). Let \((X, \mathcal{A}, \mu)\) be a measure space. Let \((f_n)_{n \geq 1}\) be a sequence of \(\mathcal{A}\)-measurable functions taking values in \(\overline{\mathbb{R}}\). Then the functions

\[
\sup _ {n \geq 1} f _ {n}, \quad \inf _ {n \geq 1} f _ {n}, \quad \operatorname * {l i m s u p} _ {n \to \infty} f _ {n}, \quad \operatorname * {l i m i n f} _ {n \to \infty} f _ {n}
\]

are \(\mathcal{A}\)-measurable. In particular, if \(f_n \to f\) \(\mu\)-almost everywhere, then \(f\) is measurable (here it is necessary to assume that \((X, \mathcal{A}, \mu)\) is complete, i.e. such that if \(N \in \mathcal{A}\) and \(\mu(N) = 0\), then every subset \(B \subset N\) also belongs to \(\mathcal{A}\). Otherwise, the limit function \(f\), after modification on a null set, is measurable).

Proof. We use the classical criterion: a function \( g: X \to \overline{\mathbb{R}} \) is measurable if and only if \( \{g < a\} \in \mathcal{A} \) for every \( a \in \mathbb{R} \).

(1) Supremum. For \(a \in \mathbb{R}\),

\[
\left\{\sup _ {n \geq 1} f _ {n} <   a \right\} = \bigcap_ {n = 1} ^ {\infty} \left\{f _ {n} <   a \right\}.
\]

Since each \(\{f_n < a\} \in \mathcal{A}\) and \(\mathcal{A}\) is stable under countable intersections, we obtain the measurability of \(\sup_n f_n\).

(2) Infimum. Similarly,

\[
\left\{\inf _ {n \geq 1} f _ {n} > a \right\} = \bigcap_ {n = 1} ^ {\infty} \left\{f _ {n} > a \right\},
\]

hence \(\inf_n f_n\) is measurable (or equivalently via \(-\inf f_n = \sup(-f_n)\)).

(3) Limsup. For \(a \in \mathbb{R}\),

\[
\left\{\limsup _ {n \to \infty} f _ {n} <   a \right\} = \bigcup_ {k = 1} ^ {\infty} \bigcap_ {n \geq k} \{f _ {n} <   a \}.
\]

The stability of \(\mathcal{A}\) under countable unions and intersections implies the measurability of \(\limsup f_n\).

(4) Liminf. Similarly,

\[
\left\{\liminf _ {n \to \infty} f _ {n} > a \right\} = \bigcup_ {k = 1} ^ {\infty} \bigcap_ {n \geq k} \{f _ {n} > a \},
\]

which shows that \(\liminf f_n\) is measurable.

(5) Almost everywhere limit. Assume that \( f_{n} \to f \) \( \mu \)-almost everywhere. Then on \( E := \{x \in X : \lim f_{n}(x) \text{ exists}\} \) (with \( \mu(X \setminus E) = 0 \)), we have \( f = \limsup f_{n} = \liminf f_{n} \). Let \( g := \limsup f_{n} \), which is measurable by (3). We have \( f = g \) on \( E \), hence for every \( a \in \mathbb{R} \),

\[
\{f <   a \} \Delta \{g <   a \} \subset X \setminus E,
\]

where  \( \Delta \)  denotes the symmetric difference. Since  \( X \setminus E \)  is measurable with measure zero and the space is complete, every subset of  \( X \setminus E \)  is measurable; thus  \( \{f < a\} \in A \)  for all a, and f is measurable. ☐
### 4.4 Negligible sets and "almost everywhere" property

Definition 4.9 (Negligible set). Let \((X, \mathcal{A}, \mu)\) be a measure space. A set \(N \subset X\) is said to be negligible (or null set) for the measure \(\mu\) if:

\[
\mu (N) = 0.
\]

In other words, \(N\) belongs to \(\mathcal{A}\) and has measure zero.

Examples 4.10 (Examples for the Lebesgue measure \(\lambda\) on \(\mathbb{R}\)).

- Example 1: a singleton is negligible.

Let \(x_0 \in \mathbb{R}\). Then:

\[
\lambda (\{x _ {0} \}) = 0.
\]

Proof. For any \(\varepsilon > 0\), we can cover \(\{x_0\}\) with an interval \(I_{\varepsilon} = (x_0 - \varepsilon, x_0 + \varepsilon)\) whose measure is \(2\varepsilon\). By definition of Lebesgue measure as the infimum of lengths of open coverings:

\[
\lambda (\{x _ {0} \}) \leq 2 \varepsilon , \quad \forall \varepsilon > 0.
\]

Hence \(\lambda (\{x_0\}) = 0\)

- Example 2: a finite set is negligible.

Let \( A = \{x_{1},\ldots ,x_{n}\} \subset \mathbb{R} \). By finite additivity of Lebesgue measure:

\[
\lambda (A) = \sum_ {i = 1} ^ {n} \lambda (\{x _ {i} \}) = 0.
\]

- Example 3: the set of rationals \(\mathbb{Q}\) is negligible.

Proof. The rationals are countable: \(\mathbb{Q} = \{q_1, q_2, q_3, \ldots\}\). Then:

\[
\lambda (\mathbb {Q}) = \lambda \left(\bigcup_ {n = 1} ^ {\infty} \{q _ {n} \}\right) \leq \sum_ {n = 1} ^ {\infty} \lambda (\{q _ {n} \}) = 0.
\]

By \(\sigma\)-additivity, \(\lambda(\mathbb{Q}) = 0\).

- Example 4: the Cantor set is negligible.

It is known that the Cantor set \(\mathcal{C} \subset [0,1]\) is uncountable, closed, and has no intervals, but:

\[
\lambda (\mathcal {C}) = 0.
\]

(The proof relies on the construction of the Cantor set by successive removal of intervals, whose total removed length equals 1.)

Definition 4.11 (Property holding almost everywhere). Let \((X, \mathcal{A}, \mu)\) be a measure space. We say that a property \(P(x)\) holds almost everywhere on \(X\) (or \(\mu\)-almost everywhere) if the set of points in \(X\) where \(P(x)\) fails is negligible, i.e.:

\[
\mu \left(\{x \in X \mid P (x) i s f a l s e \}\right) = 0.
\]

We also write: \( P(x) \) is true for \( \mu \)-almost every \( x \in X \), or simply \( P(x) \) is true a.e.
Example 4.12. Let $f, g : X \to \mathbb{R}$ be two measurable functions. We say that $f = g$ almost everywhere on $X$ if:

$$\mu(\{x \in X \mid f(x) \neq g(x)\}) = 0.$$

That is, $f(x) = g(x)$ for $\mu$-almost every $x \in X$.

Back to measurability.

Proposition 4.13. Let $f : \mathbb{R} \to \mathbb{R}$ and let $N \subset \mathbb{R}$ be a negligible set (i.e. $\lambda(N) = 0$) such that $f$ is continuous on $\mathbb{R} \setminus N$. Then $f$ is (Lebesgue-)measurable.

Proof. Fix $a \in \mathbb{R}$. We decompose:

$$E_a = (\mathbb{R} \setminus N) \cap \{x : f(x) > a\} \cup N \cap \{x : f(x) > a\}.$$

On $\mathbb{R} \setminus N$, the function $f$ is continuous. Therefore:

$$\{x \in \mathbb{R} \setminus N : f(x) > a\} = (f|_{\mathbb{R} \setminus N})^{-1}((a, \infty))$$

is open in $\mathbb{R} \setminus N$, hence Borel measurable in $\mathbb{R}$ and thus Lebesgue-measurable. Moreover:

$$N \cap \{x : f(x) > a\} \subset N,$$

so it is negligible (any subset of a negligible set is measurable).

Thus, $E_a$ is the union of two measurable sets, hence measurable. As this holds for all $a \in \mathbb{R}$, $f$ is (Lebesgue-)measurable.

### 4.5 Why is measurability important?

The measurability condition is what ensures that the sets on which the function “takes certain values” are measurable, and therefore integrable in the sense of Lebesgue.

## 5 Integral for the Dirac and counting measures

Integration with respect to the Dirac measure Let $(X, \mathcal{A})$ be a measurable space, $x_0 \in X$ and $f : X \to \mathbb{R}$ a measurable function. We consider the Dirac measure $\delta_{x_0}$. We then define the integral of $f$ with respect to $\delta_{x_0}$ as:

$$\int_X f(x) \, d\delta_{x_0}(x) = f(x_0).$$
Integration with respect to the counting measure Let X be a set, endowed with the σ-algebra 𝒫(X), and let μ be the counting measure. Let f : X → ℝ be a measurable function.

We define the integral of f with respect to μ by the following sum:

$$\int_{X} f(x) \, d\mu(x) = \sum_{x \in X} f(x),$$

provided the series converges absolutely (i.e., ∑ₓ∈ₓ |f(x)| < ∞). In this case, we say that f ∈ L¹(X, μ).

Example 5.1. Let f : ℕ → ℝ be defined by f(n) = 1/n². Then:

$$\int_{\mathbb{N}} f(n) \, d\mu(n) = \sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}.$$

## 6 Integral of simple functions

To build the Lebesgue integral, we start by integrating the simplest possible functions: simple functions, i.e., those taking only finitely many values.

### 6.1 Definition

Definition 6.1. Let (X, 𝒜, μ) be a measure space. A simple (or step) function is any function f : X → ℝ that is measurable and takes only finitely many real values.

In other words, there exists an integer n ∈ ℕ*, real numbers a₁, ..., aₙ ∈ ℝ, and measurable sets A₁, ..., Aₙ ∈ 𝒜 forming a partition of X (with f constant on each Aᵢ), such that:

$$f(x) = \sum_{i=1}^{n} a_i \, \mathbf{1}_{A_i}(x), \quad \forall x \in X.$$

Each Aᵢ is called the level set associated with the value aᵢ. We denote by 𝒮 the set of all simple functions.

Reminder. Let A ⊂ X. A finite family of sets (A₁, ..., Aₙ) ⊂ 𝒜 is called a partition of A if:

(i) ⋃ᵢ₌₁ⁿ Aᵢ = A,

(ii) Aᵢ ∩ Aⱼ = ∅ for all i ≠ j.

That is, the Aᵢ are pairwise disjoint and cover the whole set A.
### 6.2 Definition of the integral of a simple function

Definition 6.2. Let \( f = \sum_{i=1}^{n} a_i \mathbf{1}_{A_i} \) be a non-negative simple function, with \( a_i \in \mathbb{R}^+ \), i.e. \( f \in \mathcal{E}^+ \), \( A_i \in \mathcal{A} \). We define the integral of \( f \) over \( X \) (or over a measurable subset \( E \subset X \)) by:

\[
\int_ {E} f d \mu = \sum_ {i = 1} ^ {n} a _ {i} \mu (A _ {i} \cap E).
\]

Remark 6.3. This formula can be seen as a generalization of rectangle areas: for each value \( a_i \), we measure "how much" of \( E \) takes this value via \( \mu(A_i \cap E) \), then take a weighted sum.

### 6.3 Simple example

Example 6.4. Let \( X = [0,2] \), equipped with the Lebesgue measure \( \lambda \), and consider the function:

\[
f (x) = \left\{ \begin{array}{l l} 1 & \text { if } x \in [ 0, 1), \\ 2 & \text { if } x \in [ 1, 2 ]. \end{array} \right.
\]

We can write:

\[
f (x) = \mathbf {1} _ {[ 0, 1)} (x) + 2 \mathbf {1} _ {[ 1, 2 ]} (x),
\]

and hence:

\[
\int_ {[ 0, 2 ]} f (x) d \lambda (x) = 1 \lambda ([ 0, 1)) + 2 \lambda ([ 1, 2 ]) = 1 \times 1 + 2 \times 1 = 3.
\]

### 6.4 Properties of the integral of simple functions

Property 6.5 (Linearity). Let \( f \) and \( g \) be two simple functions in \( \mathcal{E}^+ \), and \( \alpha, \beta \in \mathbb{R} \). Then:

\[
\int_ {E} (\alpha f + \beta g) d \mu = \alpha \int_ {E} f d \mu + \beta \int_ {E} g d \mu .
\]

Proof. Since \( f \) and \( g \) are simple functions, there exist measurable partitions of \( E \) such that:

\[
f = \sum_ {i = 1} ^ {n} a _ {i} \mathbf {1} _ {A _ {i}}, \quad g = \sum_ {j = 1} ^ {m} b _ {j} \mathbf {1} _ {B _ {j}},
\]

with \(A_{i}, B_{j}\) measurable and \(a_{i}, b_{j} \geq 0\).

We consider the common partition formed by the sets \( C_{i,j} = A_i \cap B_j \), on which:

\[
\alpha f + \beta g = \sum_ {i, j} \left(\alpha a _ {i} + \beta b _ {j}\right) \mathbf {1} _ {C _ {i, j}}.
\]

The integral becomes:

\[
\int_ {E} (\alpha f + \beta g) d \mu = \sum_ {i, j} (\alpha a _ {i} + \beta b _ {j}) \mu (C _ {i, j}) = \alpha \sum_ {i, j} a _ {i} \mu (C _ {i, j}) + \beta \sum_ {i, j} b _ {j} \mu (C _ {i, j}).
\]

But:

\[
\sum_ {i, j} a _ {i} \mu (C _ {i, j}) = \sum_ {i} a _ {i} \mu (A _ {i}), \quad \sum_ {i, j} b _ {j} \mu (C _ {i, j}) = \sum_ {j} b _ {j} \mu (B _ {j}).
\]
Hence:

$$\int_{E} (\alpha f + \beta g) \, d\mu = \alpha \int_{E} f \, d\mu + \beta \int_{E} g \, d\mu. \quad \square$$

**Property 6.6** (Monotonicity). *Let $f$ and $g \in \mathcal{E}^+$ functions on a measurable set $E$ such that $f \leq g$ on $E$. Then:*

$$\int_{E} f \, d\mu \leq \int_{E} g \, d\mu.$$

*Proof.* Since $f \leq g$, we have $g - f \geq 0$. Moreover, $g - f$ is still a simple function (being the sum and difference of simple functions).

By positivity of the integral for (non-negative) simple functions:

$$\int_{E} (g - f) \, d\mu \geq 0.$$

Therefore:

$$\int_{E} g \, d\mu - \int_{E} f \, d\mu \geq 0 \quad \Rightarrow \quad \int_{E} f \, d\mu \leq \int_{E} g \, d\mu. \quad \square$$

**Proposition 6.7.** *Let $f \in \mathcal{E}^+$ function on $X$ and $A \in \mathcal{A}$ a negligible set. Then:*

$$\int_{A} f(x) \, dx = 0.$$

*Proof.* By definition, a simple function $f$ is a linear combination of indicator functions of measurable sets of finite measure:

$$f = \sum_{k=1}^{n} a_k \mathbf{1}_{E_k},$$

where $a_k \in \mathbb{R}$ and each $E_k$ is measurable with finite measure.

We consider the integral of $f$ over the negligible set $A$:

$$\int_{A} f(x) \, dx = \sum_{k=1}^{n} a_k \int_{A} \mathbf{1}_{E_k}(x) \, dx.$$

But $\mathbf{1}_{E_k}(x)$ is measurable, and since $A$ is negligible, we have:

$$\int_{A} \mathbf{1}_{E_k}(x) \, dx = \operatorname{mes}(A \cap E_k) = 0.$$

Thus each term of the sum is zero, giving:

$$\int_{A} f(x) \, dx = 0.$$

**Proposition 6.8.** *Let $(X, \mathcal{A}, \mu)$ be a measure space, and let $f : X \to \mathbb{R}^+$ be a simple function, If*

$$\int_{X} f \, d\mu = 0,$$

*then $f = 0$ $\mu$-almost everywhere on $X$.*
Proof. A simple function $f$ can be written as $f = \sum_{i=1}^{n} \lambda_i \mathbf{1}_{A_i}$ with $\lambda_i \geq 0$ and $A_i \in \mathcal{A}$. We have:

$$\int_X f \, d\mu = \sum_{i=1}^{n} \lambda_i \, \mu(A_i).$$

If this sum is zero, and since all terms are non-negative, for each $i$ we have $\lambda_i \, \mu(A_i) = 0$. Therefore, $\lambda_i = 0$ or $\mu(A_i) = 0$, which implies $f = 0$ almost everywhere.

### 6.5 Why start with simple functions?

- They are easy to integrate.
- Any non-negative measurable function can be approximated by an increasing sequence of simple functions.
- They form the basis for constructing the Lebesgue integral.

## 7 Definition of the Lebesgue integral for a non-negative measurable function

### 7.1 Non-negative measurable functions

Definition 7.1. A function $f : X \to [0, +\infty]$ is said to be non-negative measurable if:

- $f$ is measurable,
- $f(x) \geq 0$ for all $x \in X$.

### 7.2 Approximation by simple functions

Let $f$ be a non-negative measurable function. One can construct a sequence $(\varphi_n)$ of non-negative simple functions such that:

- for all $n$, $\varphi_n(x) \leq \varphi_{n+1}(x) \leq f(x)$,
- the sequence converges to $f$: $\varphi_n(x) \to f(x)$ for all $x \in X$.

Construction. Let $f : X \to [0, +\infty)$ be measurable. For each integer $n \geq 1$, we construct a simple function $\varphi_n$ approximating $f$ from below by:

$$\varphi_n(x) = \sum_{k=0}^{n 2^n - 1} \frac{k}{2^n} \mathbf{1}_{A_{k,n}}(x) + n \mathbf{1}_{\{f(x) \geq n\}}(x),$$

where

$$A_{k,n} = \left\{ x \in X \ \middle|\ \frac{k}{2^n} \leq f(x) < \frac{k+1}{2^n} \right\}.$$

Each $A_{k,n}$ is measurable since $f$ is measurable, hence $\varphi_n$ is a simple function.
Clearly:

$$\varphi_{n}(x)\leq\varphi_{n+1}(x)\leq f(x),\quad\mathbf{and}\quad\lim_{n\to\infty}\varphi_{n}(x)=f(x).$$

![img-3.jpeg](img-3.jpeg)

Proposition 7.2. We have:

$$\varphi_{n}(x)\;=\;\frac{1}{2^{n}}\left\lfloor2^{n}\min\left(f(x),\,n\right)\right\rfloor.$$

Proof. Fix $x\in X$ and set

$$y\;=\;\min\left(f(x),\,n\right)\in[0,n].$$

We distinguish two cases.

Case 1: $y<n$. Then $y\in[0,n)$, and there exists a unique integer $k\in\{0,1,\ldots,n2^{n}-1\}$ such that

$$\frac{k}{2^{n}}\leq y\;<\;\frac{k+1}{2^{n}}.$$

Multiplying by $2^{n}$ gives

$$k\leq 2^{n}y\;<\;k+1,$$

so, by definition of the floor function, $\lfloor 2^{n}y\rfloor=k$. Moreover, since $y=\min(f(x),n)$ and $y<n$, we must have $y=f(x)$. Hence

$$\frac{k}{2^{n}}\leq f(x)<\frac{k+1}{2^{n}}\quad\Longleftrightarrow\quad x\in A_{k,n}.$$

It follows that

$$\varphi_{n}(x)\;=\;\frac{1}{2^{n}}\left\lfloor2^{n}y\right\rfloor\;=\;\frac{k}{2^{n}},$$

and in the slice representation, all terms vanish except the one corresponding to $A_{k,n}$:

$$\sum_{j=0}^{n2^{n}-1}\frac{j}{2^{n}}\mathbf{1}_{A_{j,n}}(x)+n\mathbf{1}_{B_{n}}(x)\;=\;\frac{k}{2^{n}}\cdot 1+n\cdot 0\;=\;\frac{k}{2^{n}}\;=\;\varphi_{n}(x).$$

Case 2: $y=n$. This is equivalent to $f(x)\geq n$. Then

$$\varphi_{n}(x)\;=\;\frac{1}{2^{n}}\left\lfloor2^{n}n\right\rfloor\;=\;\frac{1}{2^{n}}\left(n2^{n}\right)\;=\;n,$$
and in the slice representation, all indicators $\mathbf{1}_{A_{k,n}}(x)$ are zero (since $f(x) \geq n$) while $\mathbf{1}_{\{x, f(x) \geq n\}}(x) = 1$. Hence

$$\sum_{j=0}^{n 2^n-1} \frac{j}{2^n} \mathbf{1}_{A_{j,n}}(x) + n \mathbf{1}_{\{x, f(x) \geq n\}}(x) = 0 + n \cdot 1 = n = \varphi_n(x).$$

In both cases, we obtain pointwise equality between the two definitions. Since $x \in X$ was arbitrary, the equality holds for all $x \in X$, which completes the proof.

**Theorem 7.3** (Density of simple functions in $\mathcal{C}(K)$). Let $K \subset \mathbb{R}^n$ be compact. For any continuous function $f: K \to \mathbb{R}$ and any $\varepsilon > 0$, there exists a simple (step) function $\varphi: K \to \mathbb{R}$ such that:

$$\|f - \varphi\|_\infty < \varepsilon.$$

That is, simple functions are dense in the space of continuous functions on a compact set for the uniform norm.

Idea of the proof. Since $f$ is continuous on a compact set, it is uniformly continuous. We can partition $K$ into finitely many measurable pieces on which $f$ is almost constant. By taking average values or staircase approximations, we build a step function close to $f$. $\square$

### 7.3 Definition of the integral

**Definition 7.4** (Lebesgue integral of a non-negative function). Let $(X, \mathscr{A}, \mu)$ be a measure space, and let $f: X \to [0, +\infty]$ be measurable.

The **Lebesgue integral** of $f$ is the value (possibly infinite) defined by:

$$\int_X f \, d\mu := \sup \left\{ \int_X \varphi \, d\mu \ \middle| \ \varphi \text{ is a simple function, } 0 \leq \varphi \leq f \right\}.$$

In particular, if $(\varphi_n)$ is an increasing sequence of simple functions such that $\varphi_n(x) \uparrow f(x)$ for a.e. $x \in X$, then:

$$\int_X f \, d\mu = \lim_{n \to \infty} \int_X \varphi_n \, d\mu.$$

**Remark 7.5.** This definition coincides with that for simple functions: if $f$ is already a non-negative step function, then the supremum is attained for $f$ itself.

### 7.4 Example

**Example 7.6.** Let $f(x) = x$ on $[0, 1]$, with the Lebesgue measure $\lambda$. We construct an increasing sequence of simple functions converging to $f$:

$$\varphi_n(x) = \sum_{k=1}^n \frac{(k-1)}{n} \mathbf{1}_{(\frac{k-1}{n}, \frac{k}{n})}(x).$$

Then $\varphi_n(x) \leq f(x)$ and $\varphi_n(x) \to f(x)$ as $n \to \infty$. Hence,

$$\int_0^1 f(x) \, dx = \lim_{n \to \infty} \int_0^1 \varphi_n(x) \, dx = \frac{1}{2}.$$
### 7.5 Fundamental properties

Property 7.7 (Linearity). If \( f \) and \( g \) are nonnegative measurable functions and \( \alpha, \beta \geq 0 \), then

\[
\int_ {E} (\alpha f + \beta g) d \mu = \alpha \int_ {E} f d \mu + \beta \int_ {E} g d \mu .
\]

Property 7.8 (Monotonicity). If \( f \) and \( g \) are nonnegative measurable functions and \( f \leq g \), then

\[
\int_ {E} f d \mu \leq \int_ {E} g d \mu .
\]

Proof. Both properties hold for simple functions; by approximation and passage to the limit, they follow for nonnegative measurable functions. \(\square\)

Proposition 7.9. Let \( f \) be a nonnegative measurable function on \( X \) and let \( A \in \mathcal{A} \) be a null set. Then

\[
\int_ {A} f (x) d x = 0.
\]

Proof. Since \( f \) is a nonnegative measurable function on the measure space \( (X, \mathcal{A}, \mu) \), consider an increasing sequence of simple functions \( (\varphi_n)_n \) such that

\[
0 \leq \varphi_ {n} (x) \leq f (x) \quad \text { and } \quad \varphi_ {n} (x) \nearrow f (x) \quad \text { for   almost   every } x \in X.
\]

(This sequence exists by the definition of the Lebesgue integral for nonnegative functions.)

As \( A \) is null, \( \mu(A) = 0 \). For each \( n \), \( \varphi_n \) is a simple function (hence measurable and integrable), and by Proposition 6.7 we have:

\[
\int_ {A} \varphi_ {n} (x) d x = \int_ {X} \varphi_ {n} (x) \mathbf {1} _ {A} (x) d \mu = 0.
\]

By definition,

\[
\int_ {A} f (x) d \mu = \lim _ {n \to \infty} \int_ {A} \varphi_ {n} (x) d \mu = \lim _ {n \to \infty} 0 = 0.
\]

Proposition 7.10. Let \((X, \mathcal{A}, \mu)\) be a measure space, and let \(f: X \to \mathbb{R}\) be a function such that \(f \geq 0\) \(\mu\)-almost everywhere. If

\[
\int_ {X} f d \mu = 0,
\]

then \( f = 0 \) \( \mu \)-almost everywhere on \( X \).

Proof. Let \( f: X \to [0, +\infty) \) be measurable with \( \int_{X} f \, d\mu = 0 \).

By the definition of the Lebesgue integral, there exists an increasing sequence of nonnegative step functions \((\varphi_{n})\) such that

\[
\varphi_ {n} (x) \nearrow f (x) \quad \text { and } \quad \int_ {X} f d \mu = \lim _ {n \to \infty} \int_ {X} \varphi_ {n} d \mu .
\]
Assume by contradiction that there exists a set $A \subset X$ of strictly positive measure such that $f(x) > 0$ for all $x \in A$. By monotone convergence, there exists $n_0$ such that

$$\varphi_{n_0}(x) > \frac{f(x)}{2} > 0 \quad \text{on some subset } A' \subset A \text{ with } \mu(A') > 0.$$

Hence,

$$\int_X \varphi_{n_0}(x) \, d\mu \geq \int_{A'} \varphi_{n_0}(x) \, d\mu > 0,$$

which contradicts $\int_X f \, d\mu = \lim_{n \to \infty} \int_X \varphi_n \, d\mu = 0$. Therefore such a set $A$ cannot exist, and $f = 0$ $\mu$-almost everywhere.

## 7.6 Summary

- Any nonnegative measurable function can be approximated by an increasing sequence of simple functions.
- The Lebesgue integral is defined as the supremum of the integrals of such approximations.
- This robust construction sets up the powerful convergence theorems to come.

We now extend the definition to integrable functions that may take both positive and negative values.

## 8 Integral of General Functions

Up to this point, we have defined the Lebesgue integral only for positive measurable functions. We will now extend this definition to functions that can take both positive and negative values.

### 8.1 Positive Part and Negative Part

Definition 8.1. Let $f : X \to \mathbb{R}$ be a measurable function. We define:

$$f^+(x) = \max(f(x), 0), \quad (\text{positive part})$$

$$f^-(x) = \max(-f(x), 0), \quad (\text{negative part})$$

We then have:

$$f = f^+ - f^-, \quad |f| = f^+ + f^-.$$

Remark 8.2. The functions $f^+$ and $f^-$ are positive and measurable, since they are obtained through operations that preserve measurability.
## 8.2 Definition of the Integral

Definition 8.3 (Lebesgue Integral of a Real Function). Let $f : X \to \mathbb{R}$ be a measurable function. If the integrals of $f^{+}$ and $f^{-}$ are both finite, then we say that $f$ is integrable, and we define:

$$\int_{E} f \, d\mu = \int_{E} f^{+} \, d\mu - \int_{E} f^{-} \, d\mu.$$

Remark 8.4. The condition $\int f^{+} < \infty$ and $\int f^{-} < \infty$ ensures that the difference is meaningful (not $\infty - \infty$).

Theorem 8.5. A function $f : X \to \mathbb{R}$ is integrable (in the sense of Lebesgue) if and only if:

$$\int_{X} |f| \, d\mu < \infty.$$

Proof. This follows from the fact that $|f| = f^{+} + f^{-}$ and from Definition 8.3.

## 8.3 Examples

Example 8.6. The function $f(x) = \frac{1}{1+x^2}$ is continuous on $\mathbb{R}$ and decreases rapidly. It is integrable on $\mathbb{R}$:

$$\int_{\mathbb{R}} \frac{1}{1+x^2} \, dx = \pi.$$

Example 8.7. The function $f(x) = \frac{1}{x}$ on $(0, 1]$ is not integrable (in the sense of Lebesgue) because:

$$\int_{0}^{1} \frac{1}{x} \, dx = +\infty.$$

## 8.4 Summary to Remember

- Any real measurable function can be decomposed into a positive part $f^{+}$ and a negative part $f^{-}$.
- We say that $f$ is integrable if $\int |f| < \infty$.
- The integral of $f$ is then well-defined as the difference between the integrals of $f^{+}$ and $f^{-}$.
- This generalizes the notion of algebraic area to very general functions.

In the next section, we will look at the main properties of the Lebesgue integral, in particular the convergence theorems, which demonstrate the full power of this approach.

## 9 Fundamental Properties of the Lebesgue Integral

The Lebesgue integral has several important properties that make it very useful in analysis. We will present some of them, in particular the convergence theorems, which justify the exchange between limit and integral.
### 9.1 Linearity

Property 9.1. If \( f \) and \( g \) are integrable on \( X \), and if \( \alpha, \beta \in \mathbb{R} \), then:

\[
\int_ {X} (\alpha f + \beta g) d \mu = \alpha \int_ {X} f d \mu + \beta \int_ {X} g d \mu .
\]

### 9.2 Monotonicity

Property 9.2. If \( f \leq g \) almost everywhere on \( X \), and if \( f, g \) are integrable, then:

\[
\int_ {X} f d \mu \leq \int_ {X} g d \mu .
\]

Theorem 9.3 (Monotone Convergence Theorem (Beppo-Levi)). Let \((X, \mathcal{A}, \mu)\) be a measure space, and let \((f_n)_{n \in \mathbb{N}}\) be a sequence of positive measurable functions such that:

1. \( f_{n}(x) \leq f_{n+1}(x) \) for \( \mu \)-almost every \( x \in X \) and for all \( n \) (pointwise increasing),
2. \(f_{n}(x)\to f(x)\) for \(\mu\) -almost every \(x\in X\)

Then the limit function \( f \) is measurable and positive, and:

\[
\lim _ {n \rightarrow \infty} \int_ {X} f _ {n} d \mu = \int_ {X} f d \mu .
\]

Proof. By definition of the integral for a positive measurable function, for each \( n \), there exists an increasing sequence \( (\varphi_{n,k})_{k\in \mathbb{N}} \) of simple functions such that:

\[
0 \leq \varphi_ {n, k} (x) \leq f _ {n} (x) \quad \text { and } \quad \varphi_ {n, k} (x) \xrightarrow [ k \to \infty ]{} f _ {n} (x), \quad \text { for   almost   every } x \in X.
\]

Set, for each \(k\), \(\psi_k(x) := \varphi_{k,k}(x)\). Then:

\[
\psi_ {k} (x) \leq f _ {k} (x) \leq f (x), \quad \text { and } \quad \psi_ {k} (x) \xrightarrow [ k \to \infty ]{} f (x), \quad \mu \text {-almost everywhere.}
\]

Each \(\psi_{k}\) is a simple function. Moreover, the sequence \((\psi_k)\) is increasing.

By the definition of the integral of a positive function as the increasing limit of integrals of simple functions, we have:

\[
\int_ {X} f d \mu = \lim _ {k \rightarrow \infty} \int_ {X} \psi_ {k} d \mu .
\]

But for all \(k\), \(\psi_k \leq f_k\), hence:

\[
\int_ {X} \psi_ {k} d \mu \leq \int_ {X} f _ {k} d \mu \leq \int_ {X} f d \mu .
\]

The sequence \((\int_{X}f_{k}d\mu)\) is therefore increasing and bounded by the same limit as \((\int_{X}\psi_{k}d\mu)\).

We conclude that:

\[
\lim _ {n \rightarrow \infty} \int_ {X} f _ {n} d \mu = \int_ {X} f d \mu .
\]

□

□
Example 9.4. Let $f_n(x) = \min(x, n)$ on $X = [0, +\infty)$, with the Lebesgue measure. Then:

$$f_n(x) \uparrow x \quad \text{for all } x \in \mathbb{R}_+.$$

Thus $f(x) = x$, and we have:

$$\int_0^a f_n(x) \, dx \longrightarrow \int_0^a x \, dx = \frac{a^2}{2}.$$

Each $f_n$ is positive, increasing, and tends to $f$. Beppo-Levi applies perfectly.

# An important application of this theorem

Proposition 9.5. Let $(X, \mathscr{A}, \mu)$ be a measure space, and let $f: X \to \mathbb{R}$ (or $\mathbb{C}$) be an integrable function, i.e. $\int_X |f| \, d\mu < \infty$. If $A \in \mathscr{A}$ is negligible ($\mu(A) = 0$), then:

$$\int_A f \, d\mu = 0.$$

Proof. Let $g := |f|$, a measurable function $\ge 0$ and integrable. We first show that $\int_A g \, d\mu = 0$. Approximate $g$ by an increasing sequence of positive simple functions $(s_k)_{k \ge 1}$ such that $0 \le s_k \uparrow g$ (for example via the standard approximation of positive measurable functions).

Each $s_k$ can be written as $s_k = \sum_{i=1}^{m_k} a_{k,i} \mathbf{1}_{E_{k,i}}$ with $a_{k,i} \ge 0$ and $E_{k,i} \in \mathscr{A}$. Then:

$$\int_A s_k \, d\mu = \sum_{i=1}^{m_k} a_{k,i} \, \mu(A \cap E_{k,i}) \le \sum_{i=1}^{m_k} a_{k,i} \, \mu(A) = 0,$$

since $\mu(A) = 0$. By monotone convergence (Beppo-Levi),

$$\int_A g \, d\mu = \int_A \lim_{k \to \infty} s_k \, d\mu = \lim_{k \to \infty} \int_A s_k \, d\mu = 0.$$

Finally, by the triangle inequality for the integral:

$$\left| \int_A f \, d\mu \right| \le \int_A |f| \, d\mu = \int_A g \, d\mu = 0,$$

hence $\int_A f \, d\mu = 0$.

Remark. In the special case where $\mu$ is the Lebesgue measure on $\mathbb{R}^n$, one usually writes $dx$ instead of $d\mu$; the statement then becomes: $\int_A f(x) \, dx = 0$ whenever $A$ has Lebesgue measure zero.

# 9.3 Fatou's Lemma

Lemma 9.6 (Fatou). Let $(f_n)$ be a sequence of positive measurable functions. Then:

$$\int_X \liminf_{n \to \infty} f_n \, d\mu \le \liminf_{n \to \infty} \int_X f_n \, d\mu.$$
Proof. Let $g(x) = \liminf f_n(x)$. By definition:

$$g(x) = \lim_{n \to \infty} \inf_{k \ge n} f_k(x).$$

Set $g_n(x) = \inf_{k \ge n} f_k(x)$. We have:

$$g_n(x) \le f_k(x) \quad \text{for all } k \ge n.$$

Hence $g_n \le f_k$ for all $k \ge n$ and $g_n \uparrow g$.

By Beppo-Levi:

$$\int_X g \, d\mu = \lim_{n \to \infty} \int_X g_n \, d\mu \le \liminf_{n \to \infty} \int_X f_n \, d\mu.$$

Example 9.7. Let $f_n(x) = \frac{1}{n} \chi_{[0,1/n]}(x)$ on $X = [0, 1]$.

Then:

- $f_n(x) \ge 0$,
- $\liminf f_n(x) = 0$ everywhere,
- $\int_0^1 f_n(x) \, dx = \frac{1}{n} \cdot \frac{1}{n} = \frac{1}{n^2} \to 0$.

Thus:

$$\int_0^1 \liminf f_n(x) = 0 \le \liminf \int_0^1 f_n(x) = 0.$$

Equality holds, but Fatou's lemma more generally provides an inequality in cases where other theorems do not apply.

## 9.4 Lebesgue's Dominated Convergence Theorem

Theorem 9.8 (Lebesgue's Dominated Convergence Theorem). Let $(X, \mathscr{A}, \mu)$ be a measure space. Let $(f_n)_{n \in \mathbb{N}}$ be a sequence of measurable functions such that:

- $f_n(x) \to f(x)$ almost everywhere on $X$;
- there exists a measurable function $g: X \to [0, +\infty]$ such that, for all $n$, $|f_n(x)| \le g(x)$ almost everywhere, and $\int_X g \, d\mu < +\infty$.

Then $f$ is integrable, i.e. measurable and $\int_X |f| \, d\mu < +\infty$, and:

$$\lim_{n \to \infty} \int_X f_n(x) \, d\mu(x) = \int_X f(x) \, d\mu(x).$$

Proof. (1) $f$ is integrable. Since $f_n \to f$ a.e. and the function $x \mapsto |x|$ is continuous, we have $|f_n| \to |f|$ a.e. Moreover, $|f_n| \le g$ a.e. for all $n$, hence by passing to the limit we get $|f| \le g$ a.e. Because $g$ is integrable, it follows that $f \in L^1(\mu)$ and

$$\int_X |f| \, d\mu \le \int_X g \, d\mu < \infty.$$
(2) Fatou-type inequalities to bound the limit superior and limit inferior. Observe that for each $n$, we have $g \pm f_n \geq 0$ a.e. (since $|f_n| \leq g$), and likewise $g \pm f \geq 0$ a.e.

First application of Fatou's Lemma. Applying Fatou's Lemma to the nonnegative sequence $(g + f_n)$, we obtain

$$\int_X (g + f) \, d\mu \leq \liminf_{n \to \infty} \int_X (g + f_n) \, d\mu.$$

Expanding the integrals, this gives

$$\int_X g \, d\mu + \int_X f \, d\mu \leq \liminf_{n \to \infty} \left( \int_X g \, d\mu + \int_X f_n \, d\mu \right).$$

Subtracting $\int_X g \, d\mu$ from both sides yields

$$\int_X f \, d\mu \leq \liminf_{n \to \infty} \int_X f_n \, d\mu.$$

Second application of Fatou's Lemma. Similarly, applying Fatou's Lemma to the nonnegative sequence $(g - f_n)$,

$$\int_X (g - f) \, d\mu \leq \liminf_{n \to \infty} \int_X (g - f_n) \, d\mu,$$

that is,

$$\int_X g \, d\mu - \int_X f \, d\mu \leq \liminf_{n \to \infty} \left( \int_X g \, d\mu - \int_X f_n \, d\mu \right).$$

Subtracting $\int_X g \, d\mu$ and changing signs, we deduce

$$\limsup_{n \to \infty} \int_X f_n \, d\mu \leq \int_X f \, d\mu.$$

(3) Conclusion. From the two previous inequalities,

$$\int_X f \, d\mu \leq \liminf_{n \to \infty} \int_X f_n \, d\mu \leq \limsup_{n \to \infty} \int_X f_n \, d\mu \leq \int_X f \, d\mu,$$

we conclude that the limit $\lim_{n \to \infty} \int_X f_n \, d\mu$ exists and equals $\int_X f \, d\mu$.

Remark 9.9. This proof uses only Fatou's Lemma and the assumption of integrable domination. Note that Step (1) relies solely on the continuity of the absolute value function and the bound $|f_n| \leq g$.

Example 9.10. Let $f_n(x) = \frac{\sin(x)}{n}$ on $X = [0, \pi]$. Then:

$$f_n(x) \to 0 \quad \text{for all } x.$$

Moreover:

$$|f_n(x)| \leq \frac{1}{n} \leq 1 \quad \text{and even } |f_n(x)| \leq |\sin(x)| =: g(x).$$

The function $g(x)$ is integrable on $[0, \pi]$, so we can apply the dominated convergence theorem:

$$\int_0^\pi f_n(x) \, dx \longrightarrow \int_0^\pi 0 \, dx = 0.$$
## 10 Examples and Counter examples

In this section, we present several concrete examples to illustrate the integrability (or lack thereof) of certain functions, depending on whether we use the Riemann or Lebesgue integral.

### 10.1 Continuous function: $f(x) = x$

Example 10.1. The function $f(x) = x$ on $[0, 1]$ is continuous, so:

$$\int_0^1 f(x) \, dx = \frac{1}{2} \quad (\text{Riemann and Lebesgue}).$$

This is a classic case where the two integrals coincide.

### 10.2 Indicator function of the rationals

Example 10.2. Let $f(x) = \mathbf{1}_{\mathbb{Q} \cap [0, 1]}(x)$.

- It is discontinuous everywhere.
- It is not Riemann integrable.
- But it is Lebesgue integrable:

$$\int_0^1 f(x) \, d\lambda = \lambda(\mathbb{Q} \cap [0, 1]) = 0.$$

### 10.3 Unbounded function: $f(x) = \frac{1}{\sqrt{x}}$

Example 10.3. Let $f(x) = \frac{1}{\sqrt{x}}$ on $[0, 1]$.

- It is positive and integrable on $[a, 1]$ for any $a > 0$.
- It has a **singularity at $0^{**}$.
- Computation of the integral:

$$\int_0^1 \frac{1}{\sqrt{x}} \, dx = 2.$$

- Therefore: $f$ is Lebesgue integrable (and also Riemann integrable here).

### 10.4 Non-integrable function: $f(x) = \frac{1}{x}$ on $(0, 1]$

Example 10.4. Consider $f(x) = \frac{1}{x}$ on $(0, 1]$.

- This function is unbounded near 0.
- The improper integral diverges:

$$\int_0^1 \frac{1}{x} \, dx = +\infty.$$

- Therefore $f$ is not Riemann integrable, nor Lebesgue integrable.
### 10.5 Sequence of functions: $f_n(x) = n \cdot \mathbf{1}_{[0, \frac{1}{n}]}(x)$

Example 10.5. Let $f_n(x) = n \cdot \mathbf{1}_{[0, \frac{1}{n}]}(x)$ on $[0, 1]$.

- For all $n$:

$$\int_0^1 f_n(x) \, dx = n \cdot \frac{1}{n} = 1.$$

- But $f_n(x) \to 0$ for all $x > 0$.

- Therefore:

$$\int_0^1 \lim f_n(x) = 0 \neq \lim \int_0^1 f_n(x) = 1.$$

This example shows that one cannot always interchange limits and integrals — here, the Dominated Convergence Theorem cannot be applied because there is no integrable function $g$ that dominates all $f_n$.

## 11 $L^p(\Omega)$ Space

In this section, we consider $(\Omega, \mathcal{B}, \lambda^N)$ as a measured space, where $\Omega \subset \mathbb{R}^N$ is an open set, and $\lambda^N$ is the Lebesgue measure on $\Omega$. The notation $d\lambda^N$ will be abbreviated by $dx$. Let $1 \le p \le +\infty$.

### 11.1 Definition and First Properties

For $1 \le p < +\infty$, we define:

$$\mathcal{L}^p(\Omega) = \left\{ f : \Omega \to \mathbb{R} \text{ (or } \mathbb{C} \text{), measurable, } \int_\Omega |f(x)|^p \, dx < +\infty \right\}.$$

For $p = +\infty$, we define:

$$\mathcal{L}^\infty(\Omega) = \{ f : \Omega \to \mathbb{R} \text{ (or } \mathbb{C} \text{), measurable, } \exists C > 0 \text{ such that } |f(x)| \le C \text{ a.e. on } \Omega \}.$$

Associated Norms. For $f \in \mathcal{L}^p(\Omega)$, we define:

- If $1 \le p < +\infty$, then $\|f\|_p = \left( \int_\Omega |f(x)|^p \, dx \right)^{1/p}$.
- If $p = +\infty$, then $\|f\|_\infty = \operatorname{esssup}_{x \in \Omega} |f(x)| = \inf \{ C > 0 \mid |f(x)| \le C \text{ a.e. on } \Omega \}$.

Proposition 11.1. $\|\cdot\|_p$ is a seminorm on $\mathcal{L}^p(\Omega)$.

Proof. Positivity and homogeneity are straightforward. The triangle inequality follows from Minkowski's inequality (see Chapter 1). It is not a norm on $\mathcal{L}^p(\Omega)$ because if $\|f\|_p = \left( \int_\Omega |f(x)|^p \, dx \right)^{1/p} = 0$, this implies that $f(x) = 0$ a.e. on $\Omega$ and not everywhere, so $f$ is not necessarily the zero function. $\square$
Quotient by Equality Almost Everywhere. The fact that  \( \|f\|_{p}=0 \)  does not necessarily imply f=0 everywhere, but only f=0 almost everywhere, prevents having a norm on  \( \mathcal{L}^{p}(\Omega) \) . To address this, we define an equivalence relation  \( f\sim g \)  if f=g almost everywhere on  \( \Omega \) . The quotient space is:

\[
L ^ {p} (\Omega) = \mathcal {L} ^ {p} (\Omega) / \sim = \left\{\dot {f} \mid f \in \mathcal {L} ^ {p} (\Omega) \right\}, \quad \text { where } \dot {f} = \{g \mid g = f \text { a.e. on } \Omega \}.
\]

Theorem 11.2 (Riesz–Fischer). The space  \( (L^{p}(\Omega), \|\cdot\|_{p}) \)  is a Banach space.

Proof. It is now clear that  \( \|\cdot\|_{p} \)  is a norm on  \( L^{p}(\Omega) \) . Completeness is assumed (the interested reader can refer to [?] for a proof). □

Remark 11.3. •  \( L^{2} \)  is a Hilbert space: an inner product can be defined by  \( (f,g)=\int_{\Omega}f(x)g(x)dx \) .

- Lebesgue integrals allow the definition of norms, distances, projections, convergence, etc.

Example 11.4. On \([0,1]\), the function \(f(x) = \sqrt{x}\) belongs to \(L^p([0,1])\) because:

- If \( p = \infty \), \( \sup_{x \in [0,1]} \sqrt{x} = 1 < +\infty \).

- If \(1 \leq p < +\infty\),

\[
\int_ {0} ^ {1} | \sqrt {x} | ^ {p} d x = \frac {2}{p + 2} <   \infty .
\]

### 11.2 Fundamental Inequalities

- Minkowski. For \(f, g \in L^{p}\):

Proposition 11.5 (Minkowski's Inequality).

\[
\| f + g \| _ {L ^ {p}} \leq \| f \| _ {L ^ {p}} + \| g \| _ {L ^ {p}}.
\]

Proof. This follows from Minkowski's inequality seen in Chapter 1 and from the linearity of the integral. \(\square\)

- Hölder.

Proposition 11.6 (Hölder's Inequality). For \( p, p' \) such that \( 1/p + 1/p' = 1 \) and \( f \in L^p, g \in L^{p'} \), we have \( fg \in L^1 \) and:

\[
\left\| f g \right\| _ {L ^ {1}} \leq \left\| f \right\| _ {L ^ {p}} \left\| g \right\| _ {L ^ {p ^ {\prime}}}.
\]

The Hölder inequality is based on another inequality, namely Young's Inequality.

Lemma 11.7 (Young's Inequality). Let \( p \) and \( p' \) be such that \( \frac{1}{p} + \frac{1}{p'} = 1 \) and \( a, b \in \mathbb{R}^+ \). Then:

\[
a b \leq \frac {1}{p} a ^ {p} + \frac {1}{p ^ {\prime}} b ^ {p ^ {\prime}},
\]

with equality if \(a^p = b^{p'}\).
Young. If $a = 0$ or $b = 0$, the result is immediate. Otherwise, set $x = p \ln a$ and $y = p' \ln b$ and use the fact that the exponential function is (strictly) convex; we then write:

$$ab = \exp \left( \frac{1}{p} x + \frac{1}{p'} y \right) \leq \frac{1}{p} \exp x + \frac{1}{p'} \exp y = \frac{1}{p} a^p + \frac{1}{p'} b^{p'}.$$

The equality case is easy to check and follows from the fact that $p$ and $p'$ are conjugate. $\square$

Hölder. If $p = 1$ then $p' = \infty$, and a direct estimate of the left-hand integral gives the result. For $1 < p < \infty$, suppose that $\|f\|_{L^p}$ and $\|g\|_{L^{p'}}$ are nonzero, and set $F(x) = \frac{|f(x)|}{\|f\|_{L^p}}$ and $G(x) = \frac{|g(x)|}{\|g\|_{L^{p'}}}$. Applying Young's inequality to $F$ and $G$, we get:

$$F(x)G(x) \leq \frac{1}{p} F(x)^p + \frac{1}{p'} G(x)^{p'}.$$

Integrating both sides yields:

$$\frac{1}{\|f\|_{L^p} \|g\|_{L^{p'}}} \int_{\Omega} |f(x)g(x)| \, dx \leq \frac{1}{p} \|F\|_{L^p}^p + \frac{1}{p'} \|G\|_{L^{p'}}^{p'} = 1.$$

Generalization: Hölder's inequality generalizes, by induction, to the case of $n$ functions as follows:

$$\text{If } \sum_{i=1}^n \frac{1}{p_i} = \frac{1}{p} \leq 1 \text{ and } f_i \in L^{p_i} \text{ for } i = 1, 2, \dots, n.$$

$$\text{Then } f = \prod_{i=1}^n f_i \in L^p(\Omega) \quad \text{with} \quad \|f\|_{L^p} \leq \prod_{i=1}^n \|f_i\|_{L^{p_i}}.$$

Inclusion Property.

Proposition 11.8. If $|\Omega| < \infty$ and $1 \leq p \leq q \leq \infty$, then $L^q(\Omega) \hookrightarrow L^p(\Omega)$ continuously.

Proof. The proof uses Hölder's inequality. Let $1 \leq p \leq q$ and $f \in L^q(\Omega)$. We show that there exists $C > 0$ such that $\|f\|_{L^p} \leq C \|f\|_{L^q}$. We write:

$$\int_{\Omega} |f(x)|^p \, dx = \int_{\Omega} |f(x)|^p \mathbf{1}_{\Omega}(x) \, dx \leq \left( \int_{\Omega} (|f(x)|^p)^{\frac{q}{p}} \, dx \right)^{\frac{p}{q}} \left( \int_{\Omega} (\mathbf{1}_{\Omega}(x))^{\alpha} \, dx \right)^{\frac{1}{\alpha}},$$

with $\alpha$ defined by $\frac{p}{q} + \frac{1}{\alpha} = 1$. Raising both sides to the power $\frac{1}{p}$ gives:

$$\|f\|_{L^p} \leq |\Omega|^{\frac{1}{p} - \frac{1}{q}} \|f\|_{L^q}.$$

Interpolation.

Theorem 11.9 (Interpolation). If $f \in L^p \cap L^q$ with $1 \leq p \leq r \leq q \leq \infty$, then:

$$\|f\|_{L^r} \leq \|f\|_{L^p}^{\alpha} \|f\|_{L^q}^{1-\alpha}, \quad \text{where } \frac{1}{r} = \frac{\alpha}{p} + \frac{1-\alpha}{q}, \ \alpha \in [0, 1].$$

Example 11.10. If $f_n \to f$ in $L^p$ and $(f_n)$ is bounded in $L^q$, then $f_n \to f$ in every $L^r$ with $p \leq r < q$.
### 11.3 Density Results

Density of $C(K)$ in $L^1(K)$.

Theorem 11.11 (Density of Continuous Functions in $L^1$ on a Compact Set). Let $K \subset \mathbb{R}^n$ be a compact set endowed with the Lebesgue measure. Then for any function $f \in L^1(K)$ and any $\varepsilon > 0$, there exists a continuous function $\varphi : K \to \mathbb{R}$ such that:

$$\int_K |f(x) - \varphi(x)| \, dx < \varepsilon.$$

In other words, continuous functions on $K$ are dense in $L^1(K)$.

Idea of the Proof. First approximate $f$ by a simple function (dense in $L^1$), then approximate each simple function by a piecewise continuous function (for example via convolution or smoothing). This approximation respects the integral within $\varepsilon$. $\square$

Remark 11.12. In particular, if $\Omega$ is bounded, then $C(\overline{\Omega})$ is dense in $L^1(\Omega)$.

Density of $C_c(\Omega)$. [An even stronger result!]

Theorem 11.13. The space $C_c(\Omega)$ is dense in $L^1(\Omega)$.

Proof. This follows from the previous theorem and truncation. In practice: $\forall f \in L^1(\Omega)$, $\exists f_n \in C_c(\Omega)$ such that $\lim_{n \to \infty} \|f_n - f\|_{L^1} = 0$. $\square$

### 11.4 $L^p$ on a Measured Space $(X, \mathscr{A}, \mu)$

The previous results can be adapted and remain valid for $L^p$ spaces defined on an arbitrary measured space $(X, \mathscr{A}, \mu)$. In this case, the notation is as follows:

Definition 11.14. Let $(X, \mathscr{A}, \mu)$ be a measured space, and $1 \le p < \infty$. We define:

$$L^p(X, \mu) = \left\{ f \text{ measurable} \mid \int_X |f(x)|^p \, d\mu(x) < +\infty \right\}.$$

This is the space of $p$-integrable functions.

For $p = \infty$, we define:

$$L^\infty(X, \mu) = \{ f \text{ measurable} \mid \text{there exists } M \ge 0, \ |f(x)| \le M \text{ a.e. } \}.$$

### 11.5 Summary to Remember

- Beppo-Levi: allows passing the limit inside the integral if the sequence is increasing.
- Dominated (Lebesgue): allows passing to the limit for a sequence dominated by an integrable function.
- Fatou: provides a useful inequality when neither of the two previous conditions is satisfied.
- $L^p$ spaces are Banach spaces and $L^2$ is a Hilbert space.
## 12 Applications of the Lebesgue Integral

The Lebesgue integral plays a fundamental role in many areas of mathematics. We present here two major families of applications: in probability theory and in functional analysis.

### 12.1 Probability and Random Variables

- In probability theory, a **probability space** is a measured space $(\Omega, \mathcal{F}, \mathbb{P})$, where $\mathbb{P}$ is a probability measure: $\mathbb{P}(\Omega) = 1$.
- A **real random variable** is a measurable function $X : \Omega \to \mathbb{R}$.
- The **expectation** of a random variable $X$ is defined by:

$$\mathbb{E}[X] = \int_\Omega X \, d\mathbb{P}.$$

- This is nothing but the Lebesgue integral of $X$ with respect to $\mathbb{P}$.

**Example 12.1.** *If $X$ follows a uniform distribution on $[0, 1]$, then:*

$$\mathbb{E}[X] = \int_0^1 x \, dx = \frac{1}{2}.$$

**Remark 12.2.** *The convergence theorems (dominated convergence, Fatou, etc.) are essential for justifying passing to the limit in sequences of random variables (expectations, moments, etc.).*

### 12.2 Other Application Areas

- **Fourier series**: convergence in $L^2$ norm.
- **Partial Differential Equations**: weak formulation based on $L^p$ spaces.
- **Signal Processing**: signals modeled as elements of $L^2$.
- **Statistics**: moments, variances, expectations via integrals.

### 12.3 Summary

- The Lebesgue integral is the foundation of modern integration theory in probability.
- It allows work in rich functional spaces ($L^p$ spaces).
- It is ubiquitous in analysis, statistics, mathematical physics, and engineering.
## 13 Product Measures and Tonelli and Fubini Theorems

When working with functions defined on a product of measured spaces, it is natural to want to define a multiple integral. For this, we must introduce the notion of a product measure and use the Tonelli and Fubini theorems.

### 13.1 Product Measures

**Definition 13.1** (Product $\sigma$-algebra). *Let $(X, \mathcal{A})$ and $(Y, \mathcal{B})$ be two measurable spaces.*

*The product $\sigma$-algebra on $X \times Y$ is the set $\mathcal{A} \otimes \mathcal{B}$, the smallest $\sigma$-algebra containing all measurable rectangles of the form $A \times B$, with $A \in \mathcal{A}$ and $B \in \mathcal{B}$.*

*In other words:*

$$\mathcal{A} \otimes \mathcal{B} = \sigma \left( \{ A \times B \mid A \in \mathcal{A}, B \in \mathcal{B} \} \right),$$

*where $\sigma(\cdot)$ denotes the generated $\sigma$-algebra.*

**Remark 13.2.** *The sets $A \times B$ are called measurable rectangles and form the basic building blocks of the construction.*

**Definition 13.3** (Product Measure). *Let $(X, \mathcal{A}, \mu)$ and $(Y, \mathcal{B}, \nu)$ be two measured spaces. There exists a unique measure $\mu \otimes \nu$ on $\mathcal{A} \otimes \mathcal{B}$ such that:*

$$(\mu \otimes \nu)(A \times B) = \mu(A) \cdot \nu(B), \quad \text{for all } A \in \mathcal{A}, \ B \in \mathcal{B}.$$

*This defines the product measured space $(X \times Y, \mathcal{A} \otimes \mathcal{B}, \mu \otimes \nu)$.*

**Example 13.4** (Lebesgue Product Measure). *Let*

$$\Omega_1 \subset \mathbb{R}^{N_1}, \quad \Omega_2 \subset \mathbb{R}^{N_2}$$

*be two measurable sets. We endow $\Omega_1$ with the Lebesgue measure $m_{N_1}$ (denoted $dx$) and $\Omega_2$ with the Lebesgue measure $m_{N_2}$ (denoted $dy$).*

*The product measure*

$$m_{N_1} \times m_{N_2}$$

*is defined on the measurable product $\Omega_1 \times \Omega_2 \subset \mathbb{R}^{N_1+N_2}$ by:*

$$(m_{N_1} \times m_{N_2})(A) = \int_{\Omega_1} \left( \int_{\Omega_2} \mathbf{1}_A(x, y) \, dy \right) dx,$$

*for any measurable set $A \subset \Omega_1 \times \Omega_2$.*

*In particular, if $A = A_1 \times A_2$ with $A_1 \subset \Omega_1$ and $A_2 \subset \Omega_2$ measurable, we have:*

$$(m_{N_1} \times m_{N_2})(A_1 \times A_2) = m_{N_1}(A_1) m_{N_2}(A_2).$$

*This measure corresponds exactly to the Lebesgue measure $m_{N_1+N_2}$ restricted to $\Omega_1 \times \Omega_2$.*
### 13.2 Tonelli's Theorem (case of positive functions)

Theorem 13.5 (Tonelli). Let \( f: X \times Y \to [0, +\infty] \) be a measurable function (on the product \( \sigma \)-algebra). Then:

\[
\int_ {X \times Y} f (x, y) d (\mu \otimes \nu) (x, y) = \int_ {X} \left(\int_ {Y} f (x, y) d \nu (y)\right) d \mu (x) = \int_ {Y} \left(\int_ {X} f (x, y) d \mu (x)\right) d \nu (y).
\]

In other words, we can interchange the integrals, even if the total integral is infinite.

Idea of the proof. The idea is to construct an increasing sequence of simple functions \((\varphi_{n})\) such that \(\varphi_{n} \uparrow f\), and to use:

- the definition of the Lebesgue integral via approximations;
• the Beppo-Levi theorem;
- the equality of iterated integrals for simple functions.

Indeed, for a positive simple function:

\[
\varphi (x, y) = \sum_ {k = 1} ^ {n} a _ {k} \cdot \chi_ {A _ {k} \times B _ {k}} (x, y),
\]

we have:

\[
\int_ {X \times Y} \varphi d (\mu \otimes \nu) = \sum_ {k = 1} ^ {n} a _ {k} \mu (A _ {k}) \nu (B _ {k}).
\]

By the definition of the iterated integral, we can also write:

\[
\int_ {X} \left(\int_ {Y} \varphi (x, y) d \nu (y)\right) d \mu (x) = \sum_ {k = 1} ^ {n} a _ {k} \mu (A _ {k}) \nu (B _ {k}).
\]

Thus, the equality holds for simple functions and extends to positive measurable functions by taking the limit (Beppo-Levi).

Example 13.6. Let \( f(x,y) = \chi_{[0,1]\times [0,1]}(x,y) \) on \( \mathbb{R}^2 \).

Then:

\[
\int_ {\mathbb {R} ^ {2}} f (x, y) d x d y = \int_ {0} ^ {1} \int_ {0} ^ {1} 1 d x d y = 1.
\]

Tonelli guarantees that:

\[
\int_ {0} ^ {1} \left(\int_ {0} ^ {1} f (x, y) d x\right) d y = \int_ {0} ^ {1} \left(\int_ {0} ^ {1} f (x, y) d y\right) d x = 1.
\]
### 13.3 Fubini's Theorem (case of integrable functions)

Theorem 13.7 (Fubini). Let \( f: X \times Y \to \mathbb{R} \) be a measurable function such that \( f \in L^{1}(X \times Y, \mu \otimes \nu) \). Then:

- For almost every \( x \), the function \( y \mapsto f(x, y) \) is integrable over \( Y \), and the function \( x \mapsto \int_{Y} f(x, y) d\nu(y) \) is integrable over \( X \); the same holds symmetrically when exchanging \( x \) and \( y \).
- We have:

\[
\int_ {X \times Y} f (x, y) d (\mu \otimes \nu) (x, y) = \int_ {X} \left(\int_ {Y} f (x, y) d \nu (y)\right) d \mu (x) = \int_ {Y} \left(\int_ {X} f (x, y) d \mu (x)\right) d \nu (y)
\]

Idea of the proof. We apply Tonelli's theorem to \( |f| \), which is positive and integrable by hypothesis. This ensures that the absolute integral can be computed via iterated integrals.

Then, we use the linearity of the integral and the fact that the integrals of \( f^{+} \) and \( f^{-} \) (the positive and negative parts of \( f \)) are finite, to extend the result to \( f \).

The complete proof treats the positive/negative cases separately, but the essence is: **Fubini = Tonelli + integrability**.

Example 13.8. Let \( f(x,y) = x \cdot y \) on \([0,1]^2\). Then \( f \) is continuous, hence integrable.

We compute:

\[
\int_ {0} ^ {1} \int_ {0} ^ {1} x y d y d x = \int_ {0} ^ {1} \left[ \frac {1}{2} x \right] d x = \frac {1}{4}.
\]

Fubini guarantees that the order of integration can be exchanged:

\[
\int_ {0} ^ {1} \int_ {0} ^ {1} x y d x d y = \int_ {0} ^ {1} \left[ \frac {1}{2} y \right] d y = \frac {1}{4}.
\]

### 13.4 Counterexample to Fubini: non-integrable function

Example 13.9 (Counterexample to Fubini). Let \( f(x,y) = \frac{1}{x + y} \) on \( X = Y = (0,1) \), with Lebesgue measure.

This function is positive, but:

\[
\int_ {(0, 1) ^ {2}} f (x, y) d x d y = \int_ {0} ^ {1} \int_ {0} ^ {1} \frac {1}{x + y} d x d y = + \infty .
\]

Thus \( f \) is not in \( L^1((0,1)^2) \).

Yet, the iterated integrals formally exist:

\[
\int_ {0} ^ {1} \left(\int_ {0} ^ {1} \frac {1}{x + y} d x\right) d y = \int_ {0} ^ {1} [ \ln (x + y) ] _ {x = 0} ^ {x = 1} d y = \int_ {0} ^ {1} \ln \left(\frac {1 + y}{y}\right) d y.
\]

This last integral also diverges.

Moreover, if we take a function \( f \) whose iterated integral converges in one order but diverges in the other, it violates Fubini's conditions, and the result can be false.

Thus: **if \( f \) is not integrable**, swapping the order may give inconsistent results.
### 13.5 Summary to remember

- Tonelli: for positive functions, the multiple integral (even infinite) can be computed by iterated integration.
- Fubini: for integrable functions, we can swap the order of the integrals.
- These theorems are fundamental tools for double, triple, etc., integrals in modern analysis.

## 14 Change of Variables Theorem

The change of variables is one of the most useful applications of the Lebesgue integral in $\mathbb{R}^n$. It allows transforming a multiple integral by replacing the variables with another coordinate system.

### 14.1 Statement of the theorem in $\mathbb{R}^n$

Theorem 14.1 (Change of Variables). Let $U, V \subset \mathbb{R}^n$ be open sets, and $\Phi : U \to V$ a $C^1$-diffeomorphism (i.e. bijective, differentiable, with continuous derivative, and with differentiable inverse).

Let $f : V \to \mathbb{R}$ be a measurable function.

If $f \circ \Phi \cdot |\det D\Phi|$ is integrable on $U$, then:

$$\int_V f(y) \, dy = \int_U f(\Phi(x)) \cdot |\det D\Phi(x)| \, dx.$$

Definition 14.2. $\det D\Phi(x)$ is the Jacobian of the change of variables, i.e. the determinant of the Jacobian matrix of $\Phi$ at $x$.

### 14.2 Example 1: Polar coordinates in $\mathbb{R}^2$

- Source domain: $U = (0, +\infty) \times (0, 2\pi) \subset \mathbb{R}^2$
- Image domain: $V = \mathbb{R}^2 \setminus \{0\}$
- Change:

$$\Phi(r, \theta) = (r \cos \theta, r \sin \theta)$$

- $\Phi$ is a $C^1$-diffeomorphism from $U$ to $V$.
- Change: $(x, y) = \Phi(r, \theta)$,

$$x = r \cos \theta, \quad y = r \sin \theta, \quad r \in [0, +\infty), \theta \in [0, 2\pi).$$

- Jacobian:

$$|\det D\Phi| = r.$$

- Formula:

$$\int_{\mathbb{R}^2} f(x, y) \, dx dy = \int_0^{2\pi} \int_0^{+\infty} f(r \cos \theta, r \sin \theta) \cdot r \, dr d\theta.$$
### 14.3 Example 2: Cylindrical coordinates in \(\mathbb{R}^3\)

- Source domain: \( U = (0, +\infty) \times (0, 2\pi) \times \mathbb{R} \)
- Image domain: \( V = \mathbb{R}^3 \setminus \{x = y = 0\} \)
- Change:

\[
\Phi (r, \theta , z) = (r \cos \theta , r \sin \theta , z)
\]

- This is a \(C^1\)-diffeomorphism from \(U\) to \(V\).

- Change: \((x,y,z) = \Phi (r,\theta ,z),\)

\[
x = r \cos \theta , \quad y = r \sin \theta , \quad z = z.
\]

- Jacobian:

\[
| \det D \Phi | = r.
\]

- Formula:

\[
\int_ {\mathbb {R} ^ {3}} f (x, y, z) d x d y d z = \int_ {0} ^ {2 \pi} \int_ {0} ^ {+ \infty} \int_ {- \infty} ^ {+ \infty} f (r \cos \theta , r \sin \theta , z) \cdot r d z d r d \theta .
\]

### 14.4 Example 3: Spherical coordinates in \(\mathbb{R}^3\)

- Source domain: \( U = (0, +\infty) \times (0, \pi) \times (0, 2\pi) \)
- Image domain: \( V = \mathbb{R}^3 \setminus \{0\} \)
- Change:

\[
\Phi (r, \phi , \theta) = (r \sin \phi \cos \theta , r \sin \phi \sin \theta , r \cos \phi)
\]

- \(\Phi\) is a \(C^1\)-diffeomorphism on its domain (away from the poles and the \(z\)-axis).

- Change: \((x,y,z) = \Phi (r,\phi ,\theta)\), i.e.

\[
x = r \sin \phi \cos \theta , \quad y = r \sin \phi \sin \theta , \quad z = r \cos \phi ,
\]

with \(r\in [0, + \infty)\) ， \(\phi \in [0,\pi ]\) ， \(\theta \in [0,2\pi)\)

- Jacobian:

\[
| \det D \Phi | = r ^ {2} \sin \phi .
\]

- Formula:

\[
\int_ {\mathbb {R} ^ {3}} f (x, y, z) d x d y d z = \int_ {0} ^ {2 \pi} \int_ {0} ^ {\pi} \int_ {0} ^ {+ \infty} f (\dots) \cdot r ^ {2} \sin \phi d r d \phi d \theta .
\]

where \( f(\ldots) = f(x(r, \theta, \phi), y(r, \theta, \phi), z(r, \phi)) \).
### 14.5 Example 4: Affine change in $\mathbb{R}^n$

- Let $A \in \mathrm{GL}_n(\mathbb{R})$ be an invertible matrix, and $b \in \mathbb{R}^n$.
- Consider the change of variable:

$$\Phi(x) = Ax + b.$$

- This is a $C^\infty$ mapping, bijective, with:

$$D\Phi(x) = A, \quad \text{so } |\det D\Phi(x)| = |\det A|.$$

- If $f : \mathbb{R}^n \to \mathbb{R}$ is measurable and integrable over a set $V = \Phi(U)$, then:

$$\int_V f(y) \, dy = \int_U f(Ax + b) \cdot |\det A| \, dx.$$

**Example 14.3.** Let $A = \begin{pmatrix} 2 & 0 \\ 0 & 3 \end{pmatrix}$, $b = \begin{pmatrix} 1 \\ -1 \end{pmatrix}$, and $f(x, y) = e^{-(x^2 + y^2)}$.

Set:

$$\Phi(x, y) = (2x + 1, 3y - 1), \quad \det A = 6.$$

Then:

$$\int_{\mathbb{R}^2} f(u, v) \, du dv = \int_{\mathbb{R}^2} f(2x + 1, 3y - 1) \cdot 6 \, dx dy.$$

—

### 14.6 Summary to remember

- The theorem allows transforming domains and functions by changing coordinates.
- The Jacobian measures the local “dilation” of the transformation.
- This theorem is fundamental for multiple integrals, geometry, and computations in physics.

## Conclusion

The Lebesgue integral provides a powerful and flexible framework for integration, overcoming many limitations of the Riemann approach. Throughout this chapter, we have highlighted its conceptual foundations and technical strengths:

- Broader class of functions: The Lebesgue integral allows the integration of functions that are not Riemann integrable, including highly discontinuous functions.
- Robust approximations: Any positive measurable function can be approximated by an increasing sequence of simple functions, allowing a general and rigorous definition of the integral.
- Powerful convergence theorems: Theorems such as Beppo-Levi (monotone convergence), dominated convergence (Lebesgue), and Fatou's lemma justify passing to the limit under the integral sign in many situations.
- Handling of infinite domains or unbounded values: The Lebesgue integral remains valid for functions defined on infinite domains or taking infinite values, provided integrability conditions are met.
- Compatibility with products: Tonelli's and Fubini's theorems ensure that we can integrate over product spaces by iterating integrals under clear conditions.
- Change of variables in $\mathbb{R}^n$: Using the Jacobian, the Lebesgue integral rigorously supports coordinate transformations in multiple integrals.
- Functional analysis framework: The Lebesgue integral allows the definition of $L^p$ spaces, which are complete normed vector spaces, with $L^2$ being a Hilbert space.
- Applications in probability: The expectation of a random variable is defined as a Lebesgue integral, making it the foundation of modern probability theory.

In summary, the Lebesgue approach unifies and extends integral calculus to a very wide range of situations in both pure and applied mathematics.

## A Appendix: Comparison between the Riemann and Lebesgue Integrals

The Lebesgue integral was designed to overcome the limitations of the Riemann integral. Although the two coincide for many usual functions, they are based on very different perspectives on integration.

### A.1 Philosophy of the two approaches

- Riemann partitions the interval $[a, b]$ into small pieces along the $x$-axis, then sums the heights $f(x)$ multiplied by the widths of the intervals.
- Lebesgue partitions the $y$-axis (the values taken by $f$), then measures "how many elements of $X$" correspond to each height, using measure theory.

In other words: - Riemann partitions the **domain** ($x$-axis), - Lebesgue partitions the **codomain** ($y$-axis).
### A.2 Compatibility case

If \( f \) is continuous on a segment \([a, b]\), then:

\[
\int_ {a} ^ {b} f (x) d x \quad (\text { Riemann }) = \int_ {[ a, b ]} f d \lambda \quad (\text { Lebesgue }).
\]

More generally:

If \( f \) is bounded and continuous almost everywhere on \([a, b]\), then \( f \) is integrable in both the

### A.3 Functions integrable in the Lebesgue sense but not Riemann

Example A.1. Let \( f(x) = \chi_{\mathbb{Q} \cap [0,1]}(x) \), the indicator function of the rationals in [0, 1].

- It is discontinuous everywhere, hence not Riemann integrable.
- It is Lebesgue integrable because the set of rationals has measure zero:

\[
\int_ {0} ^ {1} f (x) d \lambda (x) = \lambda (\mathbb {Q} \cap [ 0, 1 ]) = 0.
\]

Example A.2. The function \( f_{n}(x) = n \cdot \mathbf{1}_{[0,\frac{1}{n}]}(x) \) has no integral limit in the Riemann sense, but in Lebesgue's framework:

\[
\int_ {0} ^ {1} f _ {n} (x) d x = 1 \quad (\text { constant }), \quad \text { yet } f _ {n} (x) \to 0 a. e.
\]

Thus:

\[
\int_ {0} ^ {1} \lim f _ {n} (x) = 0 \neq \lim \int_ {0} ^ {1} f _ {n} (x) = 1.
\]

Here, only the Lebesgue framework can make the correct distinction and apply an appropriate convergence theorem.

## B Appendix: Support of a measurable function

Definition B.1. Let \( f \) be measurable on \( \Omega \). The support of \( f \) is defined by:

\[
\mathbb{C}_{\Omega}\operatorname{supp}f = \bigcup_{\substack{w\subset \Omega \text{open}\\ f|_{w} = 0\text{a.e.}}}w.
\]

Theorem B.2. The support of f is closed, and f = 0 a.e. on its complement.

Proof. supp \( f \) is closed because its complement is open. Since \( W \subset \Omega \subset \mathbb{R}^N \), there exists an exhaustive sequence of increasing compacts \( (K_n)_{n \in \mathbb{N}} \) (\( K_n \subset K_{n+1} \)) such that \( W = \bigcup_{n \in \mathbb{N}} K_n \). Indeed, we may take \( K_n = \{x \in W; ||x|| \leq n \text{ and } \mathrm{dist}(x, \partial W) \geq \frac{1}{n}\} \). \( K_n \) is closed and bounded, hence compact. We can then extract a finite covering: \( \bigcup_{i=1}^{n_0} w_i \supset K_n \). Since \( f|_{w_i} = 0 \) almost everywhere, we have \( f|_{K_n} = 0 \) almost everywhere, and therefore \( f|_W = 0 \) almost everywhere.
## C Appendix: Pushforward measure

Definition C.1 (Pushforward measure). Let $(X, \mathcal{A}, \mu)$ be a measure space and let $f: X \to Y$ be a measurable map from $(X, \mathcal{A})$ to a measurable space $(Y, \mathcal{B})$. The pushforward measure of $\mu$ by $f$, denoted $f_{\#}\mu$ (or sometimes $f_{*}\mu$), is the measure on $(Y, \mathcal{B})$ given by:

$$(f_{\#}\mu)(B) = \mu(f^{-1}(B)), \quad \forall B \in \mathcal{B}.$$

Remark C.2. When $\mu$ is the Lebesgue measure $\lambda$ on $\mathbb{R}^n$ and $f$ is measurable, the measure $f_{\#}\lambda$ describes the "distribution" of the random variable $f(U)$ when $U$ is uniformly distributed according to $\lambda$.

# Examples C.3.

1. Translation of Lebesgue measure. Let $f: \mathbb{R} \to \mathbb{R}$ be defined by $f(x) = x + a$ with $a \in \mathbb{R}$. Then $f_{\#}\lambda = \lambda$: Lebesgue measure is invariant under translation.

2. Scaling. If $f(x) = bx$ with $b \neq 0$, then for all $B \in \mathcal{B}(\mathbb{R})$:

$$(f_{\#}\lambda)(B) = \lambda(f^{-1}(B)) = \lambda\left(\frac{B}{b}\right) = \frac{1}{|b|}\lambda(B).$$

Hence $f_{\#}\lambda = \frac{1}{|b|}\lambda$.

3. In probability. Let $(\Omega, \mathcal{F}, \mathbb{P})$ be a probability space and $X: \Omega \to \mathbb{R}$ a random variable uniformly distributed on $[0, 1]$, i.e. $X_{\#}\mathbb{P} = \lambda_{[0,1]}$. If we define $Y = X^2$, then the law of $Y$ is the pushforward measure $Y_{\#}\mathbb{P}$. For any Borel set $B \subset [0, 1]$:

$$(Y_{\#}\mathbb{P})(B) = \mathbb{P}(Y \in B) = \mathbb{P}(X \in \sqrt{B}) = \lambda_{[0,1]}(\sqrt{B}).$$

In density form, $Y$ has density $f_Y(y) = \frac{1}{2\sqrt{y}}\mathbf{1}_{[0,1]}(y)$.

## D Appendix: Duality in the spaces $L^p(\Omega)$

Theorem D.1 (Riesz representation for $L^p$ spaces; $1 \le p < +\infty$). Let $1 \le p < +\infty$ and $p'$ be its conjugate exponent ($\frac{1}{p} + \frac{1}{p'} = 1$). Define

$$\begin{array}{rcl} T: & L^{p'} \to (L^p)' \\ & u \mapsto Tu: L^p(\Omega) & \to \mathbb{R} \\ & f & \mapsto Tu(f) = \int_{\Omega} f u dx \end{array}$$

Then $T$ is an isometric isomorphism. That is, $\forall \phi \in (L^p)'$ there exists a unique $u \in L^{p'}$ such that $\phi(f) = <\phi, f >_{(L^p)'L^p} = \int_{\Omega} f u dx \quad \forall f \in L^p(\Omega)$ and $||\phi||_{(L^p)'} = ||u||_{L^{p'}}$.

Proof (for those who want to go further!) $T$ is linear and well-defined: if $u \in L^{p'}(\Omega)$ then $Tu \in (L^p(\Omega))'$. Indeed, $Tu$ is a linear form and

$$|Tu(f)| = \left| \int_{\Omega} f u dx \right| \le \int_{\Omega} |fu| dx \stackrel{\text{Hölder}}{\le} ||f||_{L^p} ||u||_{L^{p'}}.$$

Moreover, $T$ is continuous with $||Tu||_{(L^p)'} \le ||u||_{L^{p'}}$.
To show $T$ is an isometry, it suffices to prove $||Tu||_{(L^p)'} \geq ||u||_{L^{p'}}$. Let

$$f_0 = \begin{cases} |u|^{p'-1} & \text{if } u(x) \neq 0, \\ 0 & \text{if } u(x) = 0. \end{cases}$$

Then $f_0 \in L^p$ and $||f_0||_{L^p} = ||u||_{L^{p'}}^{p'-1}$ (to check!). We have:

$$Tu(f_0) = \int_{\Omega} |u|^{p'-1} u \, dx = \int_{\Omega} |u|^{p'} \, dx = ||u||_{L^{p'}}^{p'}.$$

Thus

$$||Tu||_{(L^p)'} \geq \frac{||u||_{L^{p'}}^{p'}}{||u||_{L^{p'}}^{p'-1}} = ||u||_{L^{p'}}.$$

Hence $T$ is continuous and injective, being linear.

**Remark D.2.** *If $E$ is a reflexive Banach space, then the bidual satisfies $E'' = E$.*

**Lemma D.3.** *$T$ is surjective.*

*Proof.* In fact, $T(L^{p'}) \equiv (L^p)'$.

We will show that $T(L^{p'})$ is closed and dense in $(L^p)'$.

- \( T(L^{p'}) \) is closed because \( T \) is an isometry.
- Let \((f_n)_n \subset T(L^{p'}) \subset V\). We show that \(f_n \underset{n \to +\infty}{\longrightarrow} f\) in \((L^p)'\). For each \(n\), there exists \(u_n\) such that \(f_n = Tu_n\). Moreover, \(||f_k - f_m||_{L^{p'}} = ||u_k - u_m||_{L^{p'}}\), hence \(u_n\) is a Cauchy sequence in \(L^{p'}\), which is a Banach space. Therefore there exists \(u \in L^{p'}\) such that \(u_n \to u\), and since \(T\) is continuous, we have \(f_n \to Tu = f\).
- Is \( T(L^{p'}) \) dense in \( (L^p)' \)?

We show that if $h \in (L^{p'})' = (L^p)''$ (the bidual), then $\forall u \in L^{p'}$,

$$< h, Tu >_{(L^p)''(L^p)'} = 0.$$

The question is now whether we can deduce from this property that $h \equiv 0$. The answer is given by the following proposition (which we will admit):

**Proposition D.4.** *If $(E, ||\cdot||)$ is a Banach space and $A$ is a subset of $E$, then we have the following equivalence:*

$$(A \text{ is dense in } E) \iff (\forall h \in E' \mid < h, x > = 0 \ \forall x \in A \implies h \equiv 0)$$

Here $E = (L^p)'$ and $A = T(L^{p'}) \subset (L^p)'$. We know that $L^p$ is reflexive (the bidual can be identified with the space itself), so $h \in (L^p)'' \equiv L^p$, from which we can take

$$u = \begin{cases} |h|^p h & \text{if } h(x) \neq 0, \\ 0 & \text{if } h(x) = 0. \end{cases}$$

We have $< h, Tu > = 0$, hence $h = 0$ because $< h, Tu > = ||h||_{L^p}$.
