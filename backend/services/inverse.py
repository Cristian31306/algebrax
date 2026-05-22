import sympy as sp
from typing import List, Dict, Any
from .gaussian_elimination import convert_to_sympy_matrix

def inverse_gauss_jordan_steps(raw_matrix: List[List[Any]]) -> Dict[str, Any]:
    M = convert_to_sympy_matrix(raw_matrix)
    rows, cols = M.shape
    
    if rows != cols:
        raise ValueError("La matriz debe ser cuadrada para calcular su inversa.")
        
    original_latex = sp.latex(M)
    steps = []
    
    # Crear la matriz aumentada [A | I]
    I = sp.eye(rows)
    M_aug = M.row_join(I)
    
    steps.append({
        "description": "Creamos la matriz aumentada $[A | I]$ concatenando la matriz identidad.",
        "matrix_latex": sp.latex(M_aug)
    })
    
    # Eliminación de Gauss-Jordan
    for c in range(rows):
        # Pivoteo parcial
        pivot_row = c
        while pivot_row < rows and M_aug[pivot_row, c] == 0:
            pivot_row += 1
            
        if pivot_row == rows:
            raise ValueError("La matriz no es invertible (determinante 0).")
            
        if pivot_row != c:
            M_aug.row_swap(c, pivot_row)
            steps.append({
                "description": f"Intercambiamos fila {c+1} y fila {pivot_row+1} para obtener un pivote distinto de 0.",
                "matrix_latex": sp.latex(M_aug)
            })
            
        # Hacer 1 el pivote
        pivot_val = M_aug[c, c]
        if pivot_val != 1:
            M_aug.row_op(c, lambda v, j: v / pivot_val)
            steps.append({
                "description": f"Multiplicamos la fila {c+1} por $\\frac{{1}}{{{sp.latex(pivot_val)}}}$ para hacer el pivote 1.",
                "matrix_latex": sp.latex(M_aug)
            })
            
        # Hacer 0 el resto de la columna
        for i in range(rows):
            if i != c:
                factor = M_aug[i, c]
                if factor != 0:
                    M_aug.row_op(i, lambda v, j: v - factor * M_aug[c, j])
                    steps.append({
                        "description": f"Restamos a la fila {i+1} la fila {c+1} multiplicada por ${sp.latex(factor)}$ para anular el elemento de la columna {c+1}.",
                        "matrix_latex": sp.latex(M_aug)
                    })
                    
    inverse_matrix = M_aug[:, rows:]
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": sp.latex(inverse_matrix),
        "solution": None
    }

def inverse_adj_steps(raw_matrix: List[List[Any]]) -> Dict[str, Any]:
    M = convert_to_sympy_matrix(raw_matrix)
    rows, cols = M.shape
    
    if rows != cols:
        raise ValueError("La matriz debe ser cuadrada para calcular su inversa.")
        
    original_latex = sp.latex(M)
    steps = []
    
    det = M.det()
    steps.append({
        "description": f"Calculamos el determinante de la matriz: $|A| = {sp.latex(det)}$.",
        "matrix_latex": ""
    })
    
    if det == 0:
        raise ValueError("La matriz no es invertible (determinante 0).")
        
    cofactor_matrix = M.cofactor_matrix()
    steps.append({
        "description": "Calculamos la matriz de cofactores $C$, donde $C_{ij} = (-1)^{i+j} M_{ij}$.",
        "matrix_latex": sp.latex(cofactor_matrix)
    })
    
    adj_matrix = cofactor_matrix.T
    steps.append({
        "description": "Calculamos la matriz adjunta $Adj(A)$, que es la traspuesta de la matriz de cofactores $C^T$.",
        "matrix_latex": sp.latex(adj_matrix)
    })
    
    inv_matrix = adj_matrix / det
    steps.append({
        "description": f"Calculamos la inversa multiplicando la matriz adjunta por $\\frac{{1}}{{|A|}} = \\frac{{1}}{{{sp.latex(det)}}}$.",
        "matrix_latex": sp.latex(inv_matrix)
    })
    
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": sp.latex(inv_matrix),
        "solution": None
    }
