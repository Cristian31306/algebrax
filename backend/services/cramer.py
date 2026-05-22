import sympy as sp
from typing import List, Dict, Any
from .gaussian_elimination import convert_to_sympy_matrix

def cramer_steps(raw_matrix: List[List[Any]]) -> Dict[str, Any]:
    M = convert_to_sympy_matrix(raw_matrix)
    rows, cols = M.shape
    
    # Para Cramer, la matriz ampliada debe ser n x (n+1)
    if cols != rows + 1:
        raise ValueError("El método de Cramer requiere un sistema cuadrado de N ecuaciones con N incógnitas (Matriz Nx(N+1))")
        
    A = M[:, :-1]
    b = M[:, -1]
    
    original_latex = sp.latex(M)
    steps = []
    
    det_A = A.det()
    steps.append({
        "description": f"Calculamos el determinante de la matriz de coeficientes $A$: $|A| = {sp.latex(det_A)}$.",
        "matrix_latex": sp.latex(A)
    })
    
    if det_A == 0:
        steps.append({
            "description": "El determinante es 0, por lo tanto el sistema no tiene solución única por la regla de Cramer.",
            "matrix_latex": ""
        })
        return {
            "original_matrix_latex": original_latex,
            "steps": steps,
            "final_matrix_latex": sp.latex(M),
            "solution": None
        }
        
    solution = []
    for i in range(rows):
        Ai = A.copy()
        Ai[:, i] = b
        det_Ai = Ai.det()
        
        steps.append({
            "description": f"Sustituimos la columna {i+1} por el vector de términos independientes $b$ para obtener $A_{i+1}$. Su determinante es $|A_{i+1}| = {sp.latex(det_Ai)}$.",
            "matrix_latex": sp.latex(Ai)
        })
        
        x_i = det_Ai / det_A
        solution.append(f"x_{i+1} = \\frac{{{sp.latex(det_Ai)}}}{{{sp.latex(det_A)}}} = {sp.latex(x_i)}")
        
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": "",
        "solution": solution
    }
