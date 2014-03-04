#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2014 Rory MacHale

__version__ = 0.3

import ply.lex as lex
import ply.yacc as yacc
import logging
import readline
import code
import re
import sys

# Try this as input!
# Lf.(Lx.f x x)(Lx.Lv.(f x x) v):(lambda f:(lambda n:1 if n == 0 else n * f(n-1)))(5)

class Lexer:
    literals = ['.', '(', ')']

    tokens = (
        'LAMBDA',
        'VAR',
        'ARG',
    )

    def t_LAMBDA(self, t):
        u'L'
        return t

    def t_VAR(self, t):
        r'[a-z]'
        return t

    def t_ARG(self, t):
        r':.*'
        t.value = t.value[1:]
        return t

    t_ignore = ' \t'

    def t_error(self, t):
        print "Illegal character '%s' in '%s'" % (t.value[0], t.value)
        t.lexer.skip(1)

    def test(self, line):
        self.lexer.input(line)
        while True:
            tok = self.lexer.token()
            if tok is None:
                break
            print tok

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, reflags=re.UNICODE, **kwargs)

class Parser:
    def __init__(self, debug=False):
        self.lexer = Lexer()
        self.tokens = self.lexer.tokens
        self.literals = self.lexer.literals
        self.build(debug=debug)

    precedence = (
        ('right', '.'),
        ('right', 'APPLICATION'),
        ('nonassoc', 'VAR'),
        ('nonassoc', 'LAMBDA'),
        ('right', '('),
    )

    def p_top(self, p):
        '''top : expr argument'''
        self.result = (p[1], p[2])

    def p_expr(self, p):
        '''expr : VAR
                | LAMBDA VAR '.' expr
                | '(' expr ')'
                | application
        '''
        if len(p) == 2 and isinstance(p[1], basestring):
            p[0] = ('var', (p[1]))
        elif len(p) == 5:
            p[0] = ('lambda', (p[2], p[4]))
        elif p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = ('call', (p[1][0], p[1][1]))

    def p_application(self, p):
        '''application : expr expr %prec APPLICATION'''
        p[0] = (p[1], p[2])

    def p_argument(self, p):
        '''argument : ARG 
                    | 
        '''
        if len(p) == 2:
            p[0] = ('args', (p[1]))
        else:
            p[0] = ('args', None)

    def p_top_error(self, p):
        '''top : error'''
        self.errval = 'Syntax error'

    def p_error(self, p):
        self.error = True

    def build(self, **kwargs):
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, line, debug):
        self.error = False
        self.errval = "Syntax error"
        self.parser.parse(line, debug=debug)
        if self.error:
            return (None, self.errval)
        return self.result

    def lexpr(self, ast):
        pred, args = ast
        if pred == 'lambda':
            return "(lambda %s: (%s))" % (args[0], self.lexpr(args[1]))
        elif pred == 'call':
           return "%s(%s)" % (self.lexpr(args[0]), self.lexpr(args[1]))
        else:
            return args[0]

    def codegen(self, ast):
        return self.lexpr(ast)

class LambdaInterpreter(code.InteractiveConsole):
    def __init__(self, p, locals=(), filename=None):
        self.parser = p
        code.InteractiveConsole.__init__(self, locals=locals, filename=filename)

    def dump_ast(self, t, d=0):
        s = "%*s" % (d*2, '')
        if isinstance(t, tuple):
            for v in t:
                self.dump_ast(v, d+1)
        else:
            print "%s%s" % (s, t)

    def interact(self, banner, verbose=False, debug=False):
        try:
            while True:
                line = self.raw_input('$ ')
                if len(line.strip()) > 0:
                    code_ast, code_args = self.parser.parse(line, debug=debug)
                    if code_ast is None:
                        print "%s" % code_args
                    else:
                        code_py = "(%s)" % self.parser.codegen(code_ast)
                        if code_args[0] == 'args' and code_args[1] is not None:
                            code_py += "%s" % (code_args[1],)
                            try:
                                code_co = code.compile_command(code_py)
                            except:
                                code_co = None
                            if code_co is None:
                                print "Code (%s) did not compile" % (code_py)
                            else:
                                if verbose:
                                    print code_ast
                                    self.dump_ast(code_ast)
                                    print code_py
                                try:
                                    exec code_co
                                except:
                                    e, v, s = sys.exc_info()
                                    print "Runtime error (%s)" % v
                        else:
                            print "%s" % code_py
                            if verbose:
                                self.dump_ast(code_ast)
                    print
        except EOFError:
            pass

    def test(self, expr):
        result =  self.parser.parse(expr)
        if result[0] is None:
            print result[1]
        else:
            intr.dump_ast(result)

def banner(full):
    sbanner = 'Lambda Interpreter v%s' % (__version__)
    if full:
        sbanner += " Copyright (c) 2014 Rory MacHale"
    return sbanner

def interpret(args, verbose=False):
    logging.basicConfig(level = logging.DEBUG)
    cons = Parser()
    intr = LambdaInterpreter(cons)
    print banner(False)
    log = None
    if args.logger:
        log = logging.getLogger()
    intr.interact(banner, verbose=verbose, debug=log)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Lambda interpreter')
    parser.add_argument('-l', '--logger', action='store_true',
        help='Log parsing process')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Verbose expression evaluation')
    args = parser.parse_args()
    interpret(args, args.verbose)

if __name__ == "__main__":
    main()
