# aspq2qasp
Script to translate ASP(Q) programs into QASP. Compatible with the solvers [PyQASP](https://github.com/MazzottaG/PyQASP.git), [q_asp](https://github.com/bernardocuteri/q_asp.git) and [qasp2qbf](https://github.com/potassco/qasp2qbf.git).

# Usage
    $ aspq2qasp <file>
Where `<file>` is a .aspq file. 

If a file name is not specified, the program reads from stdin. 

N.B.: for the parser to work correctly, there must be no internal spaces in the atoms:
ex A(X,Y) is correct, A(X, Y) isn't. 
A comma followed by a space must be used only for conjuction in the body of the rules. 
