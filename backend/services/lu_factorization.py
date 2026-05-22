import sympy as sp
from typing import List, Dict, Any
from .gaussian_elimination import convert_to_sympy_matrix

def lu_factorization_steps(raw_matrix: List[List[Any]]) -> Dict[str, Any]:
    M = convert_to_sympy_matrix(raw_matrix)
    rows, cols = M.shape
    
    if rows != cols:
        raise ValueError("La matriz debe ser cuadrada para la descomposición LU de Doolittle.")
        
    original_latex = sp.latex(M)
    steps = []
    
    L = sp.eye(rows)
    U = M.copy()
    
    steps.append({
        "description": "Inicializamos la matriz $L$ como la matriz identidad y la matriz $U$ como la matriz original $A$.",
        "matrix_latex": f"L = {sp.latex(L)}, \\quad U = {sp.latex(U)}"
    })
    
    for c in range(rows):
        if U[c, c] == 0:
            raise ValueError("Pivote nulo encontrado. La factorización LU básica requiere que no haya intercambios de filas. Se requeriría factorización PLU.")
            
        for r in range(c + 1, rows):
            factor = U[r, c] / U[c, c]
            L[r, c] = factor
            U.row_op(r, lambda v, j: v - factor * U[c, j])
            
            steps.append({
                "description": f"Multiplicador $L_{{{r+1}{c+1}}} = {sp.latex(factor)}$. Restamos a la fila {r+1} la fila {c+1} multiplicada por este factor en $U$.",
                "matrix_latex": f"L = {sp.latex(L)}, \\quad U = {sp.latex(U)}"
            })
            
    final_latex = f"A = LU \\implies L = {sp.latex(L)}, \\quad U = {sp.latex(U)}"
    
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": final_latex,
        "solution": None
    }
