import sympy as sp
from typing import List, Dict, Any
from .gaussian_elimination import convert_to_sympy_matrix

def matrix_add_steps(matrix_a: List[List[Any]], matrix_b: List[List[Any]]) -> Dict[str, Any]:
    A = convert_to_sympy_matrix(matrix_a)
    B = convert_to_sympy_matrix(matrix_b)
    
    if A.shape != B.shape:
        raise ValueError("Las matrices deben tener las mismas dimensiones para sumarse.")
        
    original_latex = f"{sp.latex(A)} + {sp.latex(B)}"
    steps = [{
        "description": "Sumamos los elementos correspondientes de la Matriz A y la Matriz B ($C_{ij} = A_{ij} + B_{ij}$).",
        "matrix_latex": ""
    }]
    
    C = A + B
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": sp.latex(C),
        "solution": None
    }

def matrix_subtract_steps(matrix_a: List[List[Any]], matrix_b: List[List[Any]]) -> Dict[str, Any]:
    A = convert_to_sympy_matrix(matrix_a)
    B = convert_to_sympy_matrix(matrix_b)
    
    if A.shape != B.shape:
        raise ValueError("Las matrices deben tener las mismas dimensiones para restarse.")
        
    original_latex = f"{sp.latex(A)} - {sp.latex(B)}"
    steps = [{
        "description": "Restamos los elementos de la Matriz B a los correspondientes de la Matriz A ($C_{ij} = A_{ij} - B_{ij}$).",
        "matrix_latex": ""
    }]
    
    C = A - B
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": sp.latex(C),
        "solution": None
    }

def matrix_multiply_steps(matrix_a: List[List[Any]], matrix_b: List[List[Any]]) -> Dict[str, Any]:
    A = convert_to_sympy_matrix(matrix_a)
    B = convert_to_sympy_matrix(matrix_b)
    
    if A.shape[1] != B.shape[0]:
        raise ValueError("El número de columnas de la Matriz A debe coincidir con el número de filas de la Matriz B.")
        
    original_latex = f"{sp.latex(A)} \\times {sp.latex(B)}"
    steps = [{
        "description": "Multiplicamos filas de A por columnas de B. $C_{ij} = \\sum_{k=1}^{n} A_{ik} B_{kj}$",
        "matrix_latex": ""
    }]
    
    C = A * B
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": sp.latex(C),
        "solution": None
    }

def matrix_transpose_steps(matrix_a: List[List[Any]]) -> Dict[str, Any]:
    A = convert_to_sympy_matrix(matrix_a)
    original_latex = sp.latex(A)
    
    steps = [{
        "description": "Intercambiamos las filas por las columnas. El elemento $A_{ij}$ pasa a ser $A_{ji}$.",
        "matrix_latex": ""
    }]
    
    C = A.T
    
    # Identificar simetría opcionalmente
    if A.is_square:
        if A == C:
            steps.append({"description": "La matriz es Simétrica, ya que $A = A^T$.", "matrix_latex": ""})
        elif A == -C:
            steps.append({"description": "La matriz es Antisimétrica, ya que $A = -A^T$.", "matrix_latex": ""})
            
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": sp.latex(C),
        "solution": None
    }
