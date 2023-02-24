from copy import deepcopy
from time import time
import itertools as it


diatomic = ['O', 'N', 'H', 'F', 'Cl', 'I', 'Br']
activity = ['Li', 'K', 'Ba', 'Sr', 'Ca', 'Na', 'Mg', 'Al', 'Zn', 'Cr', 'Fe', 'Cd', 'Co', 'Ni', 'Sn', 'Pb', 'H', 'Cu', 'Hg', 'Ag', 'Pt', 'Au', 'F', 'Cl', 'Br', 'I']
path = 'data.csv'
table = {}


with open(path) as file:
    for each in file.readlines():
        line = each.strip('\n').split(',')
        for i in range(1, len(line)-1):
            line[i] = float(line[i])
        table[line[0]] = line[1:]


def lookup(name=str) -> list:
    for element, data in table.items():
        if name == element:
            return [element, data]


def expand(molecule=str):
    try:
        if not molecule[0].isdigit():
            molecule = '1' + molecule
    except TypeError:
        print('Invalid Input')
        return None
    except IndexError:
        print('Empty Input')
        return None

    result = []
    while '(' in molecule or not molecule.isdigit():
        if '(' in molecule:
            begin = molecule.find('(')
            end = molecule.find(')')
            information = lookup(molecule[begin+1:end])
        else:
            for each in molecule:
                if each.isupper() is True:
                    break
            begin = molecule.find(each)
            end = begin+1 if len(molecule) > 2 and molecule[begin+1].islower() is True else begin
            information = lookup(molecule[begin:end+1])

        if information is not None:
            quantity = 1
            for i in range(end+1, len(molecule)+1):
                if i == len(molecule) or not molecule[i].isdigit():
                    break
            if molecule[end+1:i] != '':
                quantity = int(molecule[end+1:i])
        else:
            print('Unable to find the atom or polyatomic molecule')
            return None

        molecule = molecule[:begin] + molecule[i:]
        result.insert(0, [quantity, information])

    result.insert(0, int(molecule))
    return result


class Element():
    def __init__(self, quantity, name, parameter) -> None:
        self.name = name
        self.quantity = quantity
        self.number = parameter[0]
        self.mass = parameter[1]
        self.charge = parameter[2:5]
        self.structure = parameter[5]

        while 0 in self.charge and len(self.charge) > 1:
            self.charge.remove(0)
        if self.structure == '0':
            self.structure = None
        

class Molecule():
    def __init__(self, name) -> None:
        self.atoms = []
        self.coef = 1
        self.bond = None
        self.mass = 0

        try:
            expansion = expand(name)
            self.coef = expansion[0]
            for each in expansion[1:]:
                temp = Element(each[0], each[1][0], each[1][1])
                self.atoms.append(temp)
        except TypeError:
            print('Unable to the read the input')
            return None

        flag = 0
        for atom in self.atoms:
            if atom.name == 'C' or atom.name == 'H':
                flag += 1
        if len(self.atoms) == 1:
            self.bond = 'single'
        elif len(self.atoms) == 2:
            charge = self.atoms[0].charge[0] * self.atoms[1].charge[0]
            self.bond = 'ionic' if charge < 0 else 'covalent'
        if flag >= 2:
            self.bond = 'organic'


    def show(self):
        print(f'Coefficient: {self.coef} | Bond: {self.bond} | Mass: {self.mass}')
        for atom in self.atoms:
            print(f'{atom.__dict__}')


    def weigh(self):
        self.mass = 0
        for atom in self.atoms:
            self.mass += (atom.mass * atom.quantity)
        self.mass *= self.coef


    def digas(self):
        if self.bond == 'single' and self.atoms[0].name in diatomic:
            self.atoms[0].quantity = 2


    def rectify(self):
        if 'ionic' in self.bond:
            if self.atoms[0].charge[0] > 0:
                self.atoms[0], self.atoms[1] = self.atoms[1], self.atoms[0]
            charge = abs(self.atoms[0].quantity * self.atoms[0].charge[0])
            for i in range(len(self.atoms[1].charge)):
                if self.atoms[1].charge[i] * self.atoms[1].quantity == charge:
                    self.atoms[1].charge = [self.atoms[1].charge[i]]
                    self.bond = '*ionic'
                    break
        self.digas()
        self.weigh()


    def form(self):
        if 'ionic' in self.bond:
            lcm = 1
            while lcm % self.atoms[0].charge[0] or lcm % self.atoms[1].charge[0]:
                lcm += 1
            self.atoms[0].quantity = int(abs(lcm / self.atoms[0].charge[0]))
            self.atoms[1].quantity = int(abs(lcm / self.atoms[1].charge[0]))
            self.bond = '*ionic'
        self.digas()
        self.weigh()


class Equation():
    def __init__(self, equation) -> None:
        self.short = tuple(equation)
        self.comp = []
        self.reaction = None
        self.counter = {}

        try:
            for each in equation:
                molecule = Molecule(each)
                molecule.rectify()
                self.comp.append(molecule)
        except TypeError:
            return None
        

    def simple(self):
        output = []
        for molecule in self.comp:
            name = str(molecule.coef)
            for atom in molecule.atoms:
                name += f'({atom.name}){atom.quantity}'
            output.append(name)
        return output


    def refresh(self):
        self.counter.clear()
        for molecule in self.comp:
            for atom in molecule.atoms:
                if atom.structure is None:
                    polyatomic = expand(atom.name)
                    for each in polyatomic[1:]:
                        count = each[0] * atom.quantity * molecule.coef
                        if each[1][0] not in self.counter:
                            self.counter[each[1][0]] = count
                        else:
                            self.counter[each[1][0]] += count
                else:
                    count = atom.quantity * molecule.coef
                    if atom.name not in self.counter:
                        self.counter[atom.name] = count
                    else:
                        self.counter[atom.name] += count


    def show(self):
        print('-' * 100)
        print(f'{self.short} | {self.reaction} | {self.counter}')
        for molecule in self.comp:
            molecule.show()


    def react(self):
        if len(self.comp) == 1 and len(self.comp[0].atoms) == 2:
            self.reaction = 'decompose'
        elif len(self.comp) == 2:
            if self.comp[0].bond == 'single' and self.comp[1].bond == 'single':
                charge = self.comp[0].atoms[0].charge[0] * self.comp[1].atoms[0].charge[0]
                self.reaction = '*combine' if charge < 0 else 'combine'
            for i in range(2):
                if self.comp[0-i].bond == 'organic' and self.comp[1-i].atoms[0].name == 'O':
                    self.reaction = 'combust'
                elif self.comp[0-i].bond == 'single' and self.comp[1-i].bond == '*ionic':
                    self.reaction = 'single'
                elif self.comp[0-i].bond == '*ionic' and self.comp[1-i].bond == '*ionic':
                    if 'H' in self.short[0-i] and '(OH)' in self.short[1-i]:
                        self.reaction = 'neutralize'
                        break
                    else:
                        self.reaction = 'double'
        else:
            return False
                    
    
    def predict(self):
        def decompose():
            a = f'{self.comp[0].atoms[0].name}{self.comp[0].atoms[0].quantity}'
            b = f'{self.comp[0].atoms[1].name}{self.comp[0].atoms[1].quantity}'
            product = Equation([a, b])
            return product


        def combine():
            product = Equation([f'({self.comp[0].atoms[0].name})({self.comp[1].atoms[0].name})'])
            return product
        
        
        def combust():
            for molecule in self.short:
                product = Equation(['H2O', 'CO2', 'SO2']) if 'S' in molecule else Equation(['H2O', 'CO2'])
                return product
                

        def single():
            if len(self.comp[0].atoms) > len(self.comp[1].atoms):
                self.comp[0], self.comp[1] = self.comp[1], self.comp[0]
            product = deepcopy(self)
            if activity.index(self.comp[0].atoms[0].name) < activity.index(self.comp[1].atoms[1].name):
                product.comp[0].atoms[0], product.comp[1].atoms[1] = product.comp[1].atoms[1], product.comp[0].atoms[0]
            return product
        

        def neutralize():
            if self.comp[0].atoms[0].name == 'OH':
                salt = f'({self.comp[0].atoms[1].name})({self.comp[1].atoms[0].name})'
            else:
                salt = f'({self.comp[0].atoms[0].name})({self.comp[1].atoms[1].name})'
            product = Equation([salt, 'H2O'])
            return product
            

        def double():
            product = deepcopy(self)
            product.comp[0].atoms[0], product.comp[1].atoms[0] = product.comp[1].atoms[0], product.comp[0].atoms[0]
            return product


        if self.react() is False:
            product = None
        elif self.reaction == 'decompose':
            product = decompose()
        elif self.reaction == '*combine':
            product = combine()
        elif self.reaction == 'combust':
            product = combust()
        elif self.reaction == 'single':
            product = single()
        elif self.reaction == 'neutralize':
            product = neutralize()
        elif self.reaction == 'double':
            product = double()
        else:
            product = None
    
        if product is not None:
            for i in range(len(product.comp)):
                product.comp[i].form()

            update = []
            for molecule in product.comp:
                name = str(molecule.coef)
                for atom in molecule.atoms:
                    name += f'({atom.name}){atom.quantity}'
                update.append(name)
            product.short = tuple(update)
        else:
            print('Unable to determine the reaction type')

        return product


def balance(equation, max=10):
    try:
        reactant = Equation(equation)
        product = reactant.predict()
        length = len(reactant.comp) + len(product.comp)
    except AttributeError:
        print('Unable to balance the equation')
        return None

    for i in it.product(range(1, max+1), repeat=length):
        reactant.comp[0].coef = i[0]
        product.comp[0].coef = i[1]
        if length >= 3:
            if len(reactant.comp) == 2:
                reactant.comp[1].coef = i[2]
            else:
                product.comp[1].coef = i[2]
        if length >= 4:
            product.comp[1].coef = i[3]
        if length >= 5:
            product.comp[2].coef = i[4]

        reactant.refresh()
        product.refresh()

        if reactant.counter == product.counter:
            for i in range(len(reactant.comp)):
                reactant.comp[i].weigh()
            for i in range(len(product.comp)):
                product.comp[i].weigh()
            return reactant, product
    else:
        print('Calculation failed')


if __name__ == '__main__':
    equation = balance(['C6H14', 'O2'], max=30)
    print(f'{equation[0].simple()} -> {equation[1].simple()}')
