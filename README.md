PyLambda v0.3
=============

PyLambda is a simple hybrid lambda / Python expression evaluator.

It evaluates lambda expressions by binding python arguments to its variables.
Behind the scenes it converts a lambda expression into a python
expression consisting of anonymous functions (defined using `lambda`) and then
combines it with the python arguments.

For information on lambda expressions, see http://wikipedia.org/wiki/Lambda_calculus.

Usage
-----
The program presents itself as a REPL (read-evaluate-print-loop). Start it up
and just enter expressions. When you are finished, enter `Ctrl-D` to exit.

Lambda expressions should be entered using the standard notation, *except*
instead of using the 'λ' symbol, use 'L'.

Examples:

    Lx.x:(2)
    2

The identity function. The general form is *lambda-expression*:*python-arguments*.

    Lx.Ly.y:(2)(3)
    3

Note the need to bracket each argument.

    Lf.Lx.f x:(lambda x:x+1)(2)
    3

Lambda expressions are not particularly interesting unless at least one of the
arguments passed in is a function (defined using lambda):

    Lf.(Lx.x x)(Lx.Lv.(f x x)v):(lambda f:(lambda n:1 if n==0 else n*f(n-1)))(5)
    120

The last case is an example of the Y-combinator. Because the python evaluator
has applicative order (eager evaluation), the normal Y-combinator
expression has been converted to a form which implements lazy evaluation.

The Y-combinator expression here converts the single-step factorial function into
a fully recursive factorial, which calculates `5! = 120`.

Prerequisites
-------------
PyLambda requires [PLY 3.4](http://www.dabeaz.com/ply/), which must be installed
prior to PyLambda installation.

ToDo
----
Evaluation using normal order without requiring any explicit syntax.

