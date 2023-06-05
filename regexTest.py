from classes.Regex import *
a = 'aa*(bb*aa*b)*#'
b = '((1(00*1)*1)|0)*#' # Essa exemplo dá erro
af = er_to_dfa(b)
print(af)
