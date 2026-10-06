"""Bounded beginner Python interpreter. Never eval, exec, import or spawn code."""
import ast
import math
import operator
from dataclasses import dataclass

class LearningError(ValueError):pass
@dataclass
class LearningResult:
    output:str
    steps:int

class LessonPython:
    def __init__(self):self.values={};self.lines=[];self.steps=0
    def tick(self):
        self.steps+=1
        if self.steps>10000:raise LearningError('Lesson step limit reached (10,000).')
    def bounded(self,value,depth=0):
        self.tick()
        if depth>12:raise LearningError('Sequence nesting limit reached.')
        if isinstance(value,int) and value.bit_length()>256:raise LearningError('Integer limit reached.')
        if isinstance(value,float) and not math.isfinite(value):raise LearningError('Only finite numbers are supported.')
        if isinstance(value,str) and len(value)>4000:raise LearningError('Text limit reached.')
        if isinstance(value,(list,tuple)):
            if len(value)>200:raise LearningError('List limit reached (200).')
            for item in value:self.bounded(item,depth+1)
        if value is not None and not isinstance(value,(str,int,float,bool,list,tuple)):raise LearningError('Unsupported lesson value.')
        return value
    def expression(self,node):
        self.tick()
        if isinstance(node,ast.Constant):return self.bounded(node.value)
        if isinstance(node,ast.Name):
            if node.id not in self.values:raise LearningError('Unknown variable: '+node.id)
            return self.values[node.id]
        if isinstance(node,(ast.List,ast.Tuple)):return self.bounded([self.expression(n) for n in node.elts])
        if isinstance(node,ast.BinOp):
            left=self.expression(node.left);right=self.expression(node.right)
            if isinstance(node.op,ast.Pow):
                if not isinstance(left,(int,float)) or not isinstance(right,int) or not 0<=right<=12 or abs(left)>10000:raise LearningError('Power limit reached.')
            if isinstance(node.op,ast.Mult) and isinstance(left,(str,list)):
                if not isinstance(right,int) or right<0 or len(left)*right>4000:raise LearningError('Sequence multiplication limit reached.')
            if isinstance(node.op,ast.Mult) and isinstance(right,(str,list)):
                if not isinstance(left,int) or left<0 or len(right)*left>4000:raise LearningError('Sequence multiplication limit reached.')
            if isinstance(node.op,ast.Add) and isinstance(left,(str,list)):
                if type(left) is not type(right):raise LearningError('Add two values of the same type.')
                if len(left)+len(right)>4000:raise LearningError('Sequence addition limit reached.')
            elif isinstance(node.op,ast.Mult) and (isinstance(left,(str,list)) or isinstance(right,(str,list))):pass
            elif not isinstance(left,(int,float)) or not isinstance(right,(int,float)):
                raise LearningError('This operator supports numbers only; text formatting is disabled.')
            operations={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.FloorDiv:operator.floordiv,ast.Mod:operator.mod,ast.Pow:operator.pow}
            fn=operations.get(type(node.op))
            if not fn:raise LearningError('Unsupported arithmetic operation.')
            return self.bounded(fn(left,right))
        if isinstance(node,ast.UnaryOp):
            value=self.expression(node.operand);fn={ast.USub:operator.neg,ast.UAdd:operator.pos,ast.Not:operator.not_}.get(type(node.op))
            if not fn:raise LearningError('Unsupported unary operation.')
            return self.bounded(fn(value))
        if isinstance(node,ast.Compare):
            left=self.expression(node.left)
            for op,right_node in zip(node.ops,node.comparators):
                right=self.expression(right_node);fn={ast.Eq:operator.eq,ast.NotEq:operator.ne,ast.Lt:operator.lt,ast.LtE:operator.le,ast.Gt:operator.gt,ast.GtE:operator.ge,ast.In:lambda a,b:a in b,ast.NotIn:lambda a,b:a not in b}.get(type(op))
                if not fn:raise LearningError('Unsupported comparison.')
                if not fn(left,right):return False
                left=right
            return True
        if isinstance(node,ast.BoolOp):
            result=False
            for item in node.values:
                result=self.expression(item)
                if isinstance(node.op,ast.And) and not result:return result
                if isinstance(node.op,ast.Or) and result:return result
            return result
        if isinstance(node,ast.Call):
            if not isinstance(node.func,ast.Name) or node.keywords:raise LearningError('Only named lesson functions without keyword arguments are supported.')
            name=node.func.id;args=[self.expression(a) for a in node.args]
            if name=='print':
                text=' '.join(str(a) for a in args)
                if sum(len(line)+1 for line in self.lines)+len(text)>16000:raise LearningError('Output limit reached.')
                self.lines.append(text);return None
            if name=='range':
                if not 1<=len(args)<=3 or not all(isinstance(a,int) for a in args):raise LearningError('range expects 1–3 integers.')
                result=range(*args)
                if len(result)>200:raise LearningError('range limit reached (200).')
                return list(result)
            fn={'len':len,'str':str,'int':int,'float':float,'abs':abs,'round':round,'sum':sum,'min':min,'max':max}.get(name)
            if not fn:raise LearningError('Unsupported function: '+name)
            return self.bounded(fn(*args))
        if isinstance(node,ast.Subscript):
            value=self.expression(node.value);index=self.expression(node.slice)
            if not isinstance(value,(list,tuple,str)) or not isinstance(index,int):raise LearningError('Only integer indexes on lesson sequences are supported.')
            return value[index]
        raise LearningError('Unsupported Python feature: '+type(node).__name__)
    def assign(self,target,value):
        if not isinstance(target,ast.Name) or target.id.startswith('_'):raise LearningError('Use a simple variable name without a leading underscore.')
        if len(self.values)>=100 and target.id not in self.values:raise LearningError('Variable limit reached.')
        self.values[target.id]=self.bounded(value)
    def block(self,nodes):
        for node in nodes:
            self.tick()
            if isinstance(node,ast.Expr):self.expression(node.value)
            elif isinstance(node,ast.Assign):
                value=self.expression(node.value)
                for target in node.targets:self.assign(target,value)
            elif isinstance(node,ast.AugAssign):
                if not isinstance(node.target,ast.Name):raise LearningError('Use a simple variable.')
                value=self.expression(ast.BinOp(left=ast.Name(id=node.target.id),op=node.op,right=node.value));self.assign(node.target,value)
            elif isinstance(node,ast.If):self.block(node.body if self.expression(node.test) else node.orelse)
            elif isinstance(node,ast.For):
                sequence=self.expression(node.iter)
                if not isinstance(sequence,(list,tuple,str)):raise LearningError('Loop over a lesson sequence.')
                for value in sequence:self.assign(node.target,value);self.block(node.body)
                self.block(node.orelse)
            elif isinstance(node,ast.While):
                while self.expression(node.test):self.tick();self.block(node.body)
                self.block(node.orelse)
            elif isinstance(node,ast.Pass):pass
            else:raise LearningError('Unsupported statement: '+type(node).__name__)
    def run(self,code):
        if len(code)>20000:raise LearningError('Code limit reached (20,000 characters).')
        try:
            tree=ast.parse(code)
            if sum(1 for _ in ast.walk(tree))>1200:raise LearningError('Syntax tree limit reached.')
            self.block(tree.body)
        except LearningError:raise
        except (SyntaxError,TypeError,ValueError,IndexError,ZeroDivisionError,OverflowError,RecursionError) as error:raise LearningError(str(error)) from None
        return LearningResult('\n'.join(self.lines),self.steps)

LESSONS={
'Python':[
 ('Hello, Timor-Leste','print("Hello, Timor-Leste!")\nname = "LAFA"\nprint("Learning with", name)\n'),
 ('Variables and arithmetic','students = 24\ngroups = 4\nprint("Students per group:", students // groups)\n'),
 ('Loops','for number in range(1, 6):\n    print(number, number * number)\n'),
 ('Conditions','score = 80\nif score >= 60:\n    print("Keep learning!")\nelse:\n    print("Try again. Small steps help.")\n'),
],
'JavaScript':[('Browser basics','const message = "Hello, Timor-Leste!";\nconsole.log(message);\n// Read and export this lesson; JavaScript execution is not enabled here.\n')],
'HTML':[('My learning page','<!doctype html>\n<html lang="en">\n  <head><title>Learning with LAFA</title></head>\n  <body><h1>Hello, Timor-Leste!</h1><p>Learn one step at a time.</p></body>\n</html>\n')],
'CSS':[('Style a learning page','body { font-family: sans-serif; background: #eef7ef; }\nh1 { color: #287544; }\n')],
}
REFERENCES={'Python':'https://docs.python.org/3/tutorial/','JavaScript':'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide','HTML':'https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content','CSS':'https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics'}

LESSON_KEYS={'Hello, Timor-Leste':'lesson_hello','Variables and arithmetic':'lesson_variables','Loops':'lesson_loops','Conditions':'lesson_conditions','Browser basics':'lesson_browser','My learning page':'lesson_html','Style a learning page':'lesson_css'}
