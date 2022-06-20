from enum import Enum, auto

from skyscript.lexer import Lexer, Token

from vec import Vec
from entity.base import Entity

class Event:
    def __init__(self, event, target):
        self.event = event
        self.target = target

    def __repr__(self):
        return "Event: %s @ %s" % (self.event, self.target)

class Type(Enum):
    NUMERICAL = auto()
    STRING = auto()

class LookupTable:
    def __init__(self):
        self.env = {}

    def __repr__(self):
        return str(self.env)

    def lookup(self, var):
        if var in self.env:
            return self.env[var]
        elif "$" in self.env:
            return self.env["$"].lookup(var)
        else:
            return None

    def insert(self, var, val):
        self.env[var] = val

    def push_scope(self):
        self.env = {"$": self.env}

    def pop_scope(self):
        if "$" in self.env:
            self.env = self.env["$"]

class SkyScript:
    def __init__(self, level):
        self.index = 0
        self.tokens = []
        
        self.level = level

        self.env = LookupTable()

    def __assert(self, actual, expected):
        if actual != expected:
            raise SyntaxError("Expected %s got %s at %i" % (expected, actual, self.index))

    def __type_assert(self, actual, expected):
        if expected == Type.STRING and type(actual) == str:
            pass
        elif expected == Type.NUMERICAL and type(actual) in (int, float):
            pass
        else:
            raise SyntaxError("Expected %s got %s at %i" % (expected, type(actual), self.index))

    def __eat(self):
        if self.index < len(self.tokens):
            self.index += 1
            token = self.tokens[self.index - 1]
            print("%i:" % (self.index), token[0], token[1])
            return token
        else:
            return None, None

    def __look(self):
        if self.index + 1 < len(self.tokens):
            return self.tokens[self.index]
        else:
            return None, None

    def __run_keyword(self):
        token, value = self.__eat()

        if token == Token.TEXTURE:
            name = self.__run_exp()
            path = self.__run_exp()
            
            self.__type_assert(name, Type.STRING)
            self.__type_assert(path, Type.STRING)

            print("TODO HOOKUP TEXTURE LOADER", name, path)

            return None
        elif token == Token.BACKGROUND:
            name = self.__run_exp()
            x = self.__run_exp()
            y = self.__run_exp()
            width = self.__run_exp()
            height = self.__run_exp()
            direction = self.__run_exp()
            
            self.__type_assert(name, Type.STRING)
            self.__type_assert(x, Type.NUMERICAL)
            self.__type_assert(y, Type.NUMERICAL)
            self.__type_assert(width, Type.NUMERICAL)
            self.__type_assert(height, Type.NUMERICAL)
            self.__type_assert(direction, Type.NUMERICAL)

            print("TODO HOOKUP BACKG LOADER", name, x, y, width, height, direction)

            return None
        elif token == Token.SURFACE:
            x1 = self.__run_exp()
            y1 = self.__run_exp()
            x2 = self.__run_exp()
            y2 = self.__run_exp()

            self.__type_assert(x1, Type.NUMERICAL)
            self.__type_assert(y1, Type.NUMERICAL)
            self.__type_assert(x2, Type.NUMERICAL)
            self.__type_assert(y2, Type.NUMERICAL)

            print("TODO HOOKUP SURF LOADER", x1, y1, x2, y2)

            return None
        elif token == Token.ENTITY:
            name = self.__run_exp()
            x = self.__run_exp()
            y = self.__run_exp()

            self.__type_assert(name, Type.STRING)
            self.__type_assert(x, Type.NUMERICAL)
            self.__type_assert(y, Type.NUMERICAL)

            print("TODO HOOKUP ENTITY LOADER", name, x, y)

            entity = Entity(Vec(x, y))
            return entity

    def __run_factor(self):
        token, value = self.__look()

        if token == Token.NUM:
            self.__eat()
            return int(value)
        elif token == Token.ID:
            self.__eat()

            token, _ = self.__look()
            if token == Token.DOT:
                # self.__eat()
                # token, _ = self.__eat()
                # self.__assert(token, Token.ID)
                # return self.env.lookup(value)
                pass
            elif token == Token.AT:
                self.__eat()
                token, target_value = self.__eat()
                self.__assert(token, Token.ID)
                return Event(value, target_value)
            else:
                return self.env.lookup(value)

        elif token == Token.STRING:
            self.__eat()
            return value

        elif token == Token.LPAR:
            self.__eat()
            exp = self.__run_exp()
            token, _ = self.__eat()

            self.__assert(token, Token.RPAR)

            return exp
        elif token == Token.SUB:
            self.__eat()
            exp = self.__run_exp()

            return -exp
        else:
            return self.__run_keyword()

    def __run_term(self):
        factor = self.__run_factor()

        token, _ = self.__look()
        if token == Token.MUL:
            self.__eat()
            return factor * self.__run_factor()
        else:
            return factor

    def __run_exp(self):
        term = self.__run_term()

        token, _ = self.__look()

        if token == Token.ADD:
            self.__eat()
            term2 = self.__run_term()

            self.__type_assert(term, Type.NUMERICAL)
            self.__type_assert(term2, Type.NUMERICAL)

            return term + term2
        elif token == Token.SUB:
            self.__eat()
            term2 = self.__run_term()

            self.__type_assert(term, Type.NUMERICAL)
            self.__type_assert(term2, Type.NUMERICAL)

            return term - term2
        else:
            return term

    def __run_on(self):
        self.__eat()

        event_name = self.__run_exp()
        params = []

        token, _ = self.__eat()
        if token == Token.WITH:
            token, value = self.__eat()
            while token != Token.DO:
                self.__assert(token, Token.ID)
                params.append(value)

                token, value = self.__eat()

        self.__assert(token, Token.DO)

        print("ON %s WITH %s DO" % (event_name, str(params)))

    def __run_if(self):
        self.__eat()

        exp = self.__run_exp()

    def __run_let(self):
        self.__eat()

        token, var = self.__eat()
        self.__assert(token, Token.ID)

        token, _ = self.__eat()
        self.__assert(token, Token.COLON)

        exp = self.__run_exp()

        self.env.insert(var, exp)

        print(self.env)

    def __run_send(self):
        self.__eat()

        token, event = self.__eat()
        self.__assert(token, Token.ID)

        if self.__look() == Token.WITH:
            self.__eat()
            values = self.__run_with()

    def __run_block(self):
        while self.__look()[0] != Token.end:
            self.__run_stm()

    def __run_stm(self):
        token, value = self.__look()
        if token == Token.ON:
            self.__run_on()
        elif token == Token.IF:
            self.__run_if()
        elif token == Token.LET:
            self.__run_let()
        elif token == Token.SEND:
            self.__run_send()
        else:
            self.__run_exp()

    def __run(self):
        while self.index < len(self.tokens):
            self.__run_stm()

    def run(self, src):
        lexer = Lexer()
        self.index = 0
        self.tokens = lexer.tokenize(src)

        # i = 0
        # for token in self.tokens:
        #     print("%i:" % (i), token[0], token[1])
        #     i += 1

        self.__run()

# interpreter = SkyScript()
# for i in range(10000):
#     interpreter.run("send calc 1+2-3*4/5 end")

# interpreter.run("send (1+2-3*4/5) end")

# interpreter.run("""
# on entity detector hurt with damage do
#   a : calc (1 + 2) * 5 end
#   x : 100

#   if damage > x then
#     send slide_door with
#       door : prop door
#       speed : 100
#     end
#   end
#   send play_sound with sound : Ouch end
#   send play_sound with sound : idc end
# end

# on 

# on slide_door with door speed do
  
# end
# """)