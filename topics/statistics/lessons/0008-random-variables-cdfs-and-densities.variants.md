## rv

::: number rv-v4 answer=0.1944 tolerance=0.005
Two fair dice are rolled, and \(X\) = the larger of the two faces (so (2,5) ↦ 5 and (4,4) ↦ 4). What is \(P(X = 4)\)? (A fraction, or a decimal to two places or better.)
--- explain
\(\{X = 4\}\): both faces at most 4 (16 pairs) minus both at most 3 (9 pairs), so 7 outcomes: \(P(X = 4) = 7/36\).
:::

## cdf

::: math cdf-v5 answer="19/216"
*Adapted from Casella & Berger, Exercise 1.53, exponent changed.* A river's yearly high-water mark \(Y\) has cdf
\(F_Y(y) = 1 - 1/y^3\) for \(y \ge 1\) (and 0 for \(y < 1\)). What is \(P(2 < Y \le 3)\)? (A fraction or expression.)
--- explain
\(P(a < Y \le b) = F_Y(b) - F_Y(a) = (1 - \tfrac1{27}) - (1 - \tfrac18) = \tfrac18 - \tfrac1{27} = \tfrac{19}{216}\).
:::

## normc

::: math normc-v2 answer="3/2"
*Adapted from Casella & Berger, Exercise 1.54(b), rate changed.* \(f(x) = c\,e^{-3|x|}\) for all real \(x\). What value of \(c\) makes \(f\) a pdf?
--- explain
By symmetry \(\int_{-\infty}^{\infty} e^{-3|x|}\,dx = 2\int_0^\infty e^{-3x}\,dx = \tfrac23\), so \(c = 3/2\).
:::

::: math normc-v4 answer="2"
\(f(x) = c / x^3\) for \(x > 1\), and 0 elsewhere. What value of \(c\) makes \(f\) a pdf?
--- explain
\(\int_1^\infty x^{-3}\,dx = \tfrac12\), so \(c = 2\).
:::

## pmfpdf

::: math pmfpdf-v3 answer="1/10"
A discrete \(X\) takes the values 1, 2, 3, 4 with pmf \(f(x) = c\,x\). What value of \(c\) makes \(f\) a pmf?
--- explain
\(c(1 + 2 + 3 + 4) = 10c = 1\), so \(c = 1/10\). (Then \(P(X = 4) = 0.4\): a pmf value is a probability, so it is at most 1.)
:::
