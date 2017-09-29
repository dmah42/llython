#from llvmlite import ir

#doublety = ir.DoubleType()
#fnty = ir.FunctionType(doublety, (doublety, doublety))
#
#module = ir.Module(name=__file__)
#func = ir.Function(module, fnty, name="fpadd")
#
#block = func.append_basic_block(name="entry")
#builder = ir.IRBuilder(block)
#
#a, b = func.args
#result = builder.fadd(a, b, name="res")
#builder.ret(result)
#
#print(module)


# -------------- TODO ----------------------
# Parse the AST of the given file
# Visit every node in the AST emitting code
# ???
# Profit!


import argparse
import ast
from llvmlite import ir

parser = argparse.ArgumentParser(description='Convert python to LLVM IR')
parser.add_argument('-i', '--input', type=str, nargs=1, required=True,
    help='the python script to convert')

args = parser.parse_args()
filename = args.input[0]

with open(filename) as f:
  src = f.read()

tree = ast.parse(src, filename)

print(ast.dump(tree))

class IRVisitor(ast.NodeVisitor):

  def __init__(self):
    self.blocks = []
    super(IRVisitor, self).__init__()

  def _cur_block(self):
    return self.blocks[-1]

  def generic_visit(self, node):
    i = 0
    print type(node).__name__
    ast.NodeVisitor.generic_visit(self, node)

  def visit_Module(self, node):
    self.module = ir.Module(name=filename)
    # Map variable names to pointers
    self.named_values = {}

    # Top-level block
    func = ir.Function(self.module, ir.FunctionType(ir.VoidType(), []), name='module_fn')
    self.blocks.append(func.append_basic_block(name='top-level'))

    ast.NodeVisitor.generic_visit(self, node)

    self.blocks.pop()

  def visit_FunctionDef(self, node):
    name = node.name
    args = []
    # TODO: handle vararg and kwarg and defaults
    for a in node.args.args:
      args.append(a.id)
    # TODO: Stop assuming double
    doublety = ir.DoubleType()
    argtys = [doublety for a in args]
    fnty = ir.FunctionType(doublety, argtys)
    func = ir.Function(self.module, fnty, name=name)

    idx = 0
    for a in func.args:
      a.name = args[idx]
      idx+=1

    self.blocks.append(func.append_basic_block(name='entry'))
    builder = ir.IRBuilder(self._cur_block())

    # TODO: stack of named values
    for a in func.args:
      var = builder.alloca(ir.DoubleType(), name=a.name)
      builder.store(a, var)
      self.named_values[a.name] = var

    self.ret = None

    print 'entering function'
    for e in node.body:
      ast.NodeVisitor.visit(self, e)

    print 'done with function'

    if self.ret:
      builder.ret(self.ret)

    self.blocks.pop()

  def visit_Assign(self, node):
    print 'Assign: ' + ast.dump(node)

    print type(node.value)

    builder = ir.IRBuilder(self._cur_block())

    # Get values
    values = []
    if type(node.value) is ast.Num:
      print '  adding value: ' + ast.dump(node.value)
      values.append(ir.Constant(ir.DoubleType(), node.value.n))
    elif type(node.value) is ast.Name:
      print '  getting var: ' + ast.dump(node.value)
      var = node.value.id
      if var not in self.named_values:
        raise Exception('Var %s not defined' % var)
      values.append(builder.load(self.named_values[var], var))
    else:
      raise Exception

    # Generate targets
    targets = []
    for t in node.targets:
      if type(t) is ast.Name:
        print '  adding target ' + t.id
        targets.append(t.id)
      else:
        raise Exception

    # Build up target map
    target_values = {}
    i = 0
    for t in targets:
      v = values[i] if i < len(values) else None
      target_values[t] = v
      i += 1

    print target_values

    for n in target_values:
      if n not in self.named_values:
        var = builder.alloca(ir.DoubleType(), name=n)
        self.named_values[n] = var
      builder.store(target_values[n], self.named_values[n])

v = IRVisitor()
v.visit(tree)
print(v.module)
