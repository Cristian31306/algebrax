import sympy as sp
from typing import List, Dict, Any
from .gaussian_elimination import convert_to_sympy_matrix

def check_linear_dependence(raw_matrix: List[List[Any]]) -> Dict[str, Any]:
    M = convert_to_sympy_matrix(raw_matrix)
    rows, cols = M.shape
    original_latex = sp.latex(M)
    
    steps = [{
        "description": "Evaluamos la dependencia lineal de los vectores calculando el Rango (Rank) de la matriz que forman.",
        "matrix_latex": ""
    }]
    
    rango = M.rank()
    steps.append({
        "description": f"El rango de la matriz es {rango}.",
        "matrix_latex": ""
    })
    
    # Suponiendo que las filas son los vectores
    if rango < min(rows, cols):
        desc = "Como el rango es menor que el número de vectores (considerando filas o columnas), los vectores son **Linealmente Dependientes**."
    else:
        desc = "Como el rango es máximo, los vectores son **Linealmente Independientes**."
        
    steps.append({"description": desc, "matrix_latex": ""})
    
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": "",
        "solution": None
    }

def calculate_distance(matrix_a: List[List[Any]], matrix_b: List[List[Any]]) -> Dict[str, Any]:
    A = convert_to_sympy_matrix(matrix_a)
    B = convert_to_sympy_matrix(matrix_b)
    
    if A.shape != B.shape or min(A.shape) != 1:
        raise ValueError("Se requieren dos vectores columna o fila del mismo tamaño.")
        
    original_latex = f"v = {sp.latex(A)}, \\quad w = {sp.latex(B)}"
    
    steps = [{
        "description": "Calculamos el vector diferencia $d = v - w$.",
        "matrix_latex": sp.latex(A - B)
    }]
    
    dist_sq = sum((A[i] - B[i])**2 for i in range(len(A)))
    dist = sp.sqrt(dist_sq)
    
    steps.append({
        "description": "La distancia es la norma euclidiana de la diferencia: $||v - w|| = \\sqrt{\\sum (v_i - w_i)^2}$.",
        "matrix_latex": f"\\sqrt{{{sp.latex(dist_sq)}}} = {sp.latex(dist)}"
    })
    
    # Evaluar si se puede aproximar numéricamente (float)
    if not dist.is_rational:
         steps.append({
             "description": f"Aproximación decimal: $\\approx {dist.evalf(5)}$",
             "matrix_latex": ""
         })
    
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": sp.latex(dist),
        "solution": None
    }

def calculate_angle(matrix_a: List[List[Any]], matrix_b: List[List[Any]]) -> Dict[str, Any]:
    A = convert_to_sympy_matrix(matrix_a)
    B = convert_to_sympy_matrix(matrix_b)
    
    if A.shape != B.shape or min(A.shape) != 1:
        raise ValueError("Se requieren dos vectores columna o fila del mismo tamaño.")
        
    original_latex = f"v = {sp.latex(A)}, \\quad w = {sp.latex(B)}"
    steps = []
    
    dot_product = sum(A[i]*B[i] for i in range(len(A)))
    steps.append({
        "description": f"Producto punto $v \\cdot w = {sp.latex(dot_product)}$.",
        "matrix_latex": ""
    })
    
    norm_A_sq = sum(A[i]**2 for i in range(len(A)))
    norm_B_sq = sum(B[i]**2 for i in range(len(B)))
    norm_A = sp.sqrt(norm_A_sq)
    norm_B = sp.sqrt(norm_B_sq)
    
    steps.append({
        "description": f"Normas: $||v|| = {sp.latex(norm_A)}$, $||w|| = {sp.latex(norm_B)}$.",
        "matrix_latex": ""
    })
    
    if norm_A == 0 or norm_B == 0:
        raise ValueError("No se puede calcular el ángulo con el vector nulo.")
        
    cos_theta = dot_product / (norm_A * norm_B)
    steps.append({
        "description": f"Calculamos $\\cos(\\theta) = \\frac{{v \\cdot w}}{{||v|| \\, ||w||}} = {sp.latex(cos_theta)}$.",
        "matrix_latex": ""
    })
    
    theta = sp.acos(cos_theta)
    
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": f"\\theta = {sp.latex(theta)} \\text{{ radianes}} \\approx {sp.deg(theta).evalf(4)}^\\circ",
        "solution": None
    }

def least_squares_steps(raw_matrix: List[List[Any]]) -> Dict[str, Any]:
    # Asumimos que raw_matrix contiene la matriz aumentada [A|b]
    M = convert_to_sympy_matrix(raw_matrix)
    rows, cols = M.shape
    
    if cols < 2:
        raise ValueError("Se requiere una matriz con al menos 2 columnas para separar A y b.")
        
    A = M[:, :-1]
    b = M[:, -1]
    
    original_latex = f"A = {sp.latex(A)}, \\quad b = {sp.latex(b)}"
    steps = []
    
    At = A.T
    steps.append({
        "description": "Planteamos las ecuaciones normales: $A^T A x = A^T b$. Transponemos $A$.",
        "matrix_latex": f"A^T = {sp.latex(At)}"
    })
    
    AtA = At * A
    Atb = At * b
    
    steps.append({
        "description": "Calculamos $A^T A$ y $A^T b$.",
        "matrix_latex": f"A^T A = {sp.latex(AtA)}, \\quad A^T b = {sp.latex(Atb)}"
    })
    
    # Resolver AtA x = Atb
    try:
        x_hat = AtA.solve(Atb)
        steps.append({
            "description": "Resolvemos el sistema resultante para $\\hat{x}$ (la solución de mínimos cuadrados).",
            "matrix_latex": f"\\hat{{x}} = {sp.latex(x_hat)}"
        })
        
        proj = A * x_hat
        steps.append({
            "description": "Opcional: La proyección ortogonal de $b$ sobre el espacio columna de $A$ es $p = A\\hat{x}$.",
            "matrix_latex": f"p = {sp.latex(proj)}"
        })
        
        return {
            "original_matrix_latex": original_latex,
            "steps": steps,
            "final_matrix_latex": f"\\hat{{x}} = {sp.latex(x_hat)}",
            "solution": None
        }
    except ValueError:
        raise ValueError("Las columnas de A no son linealmente independientes, el sistema normal tiene infinitas soluciones.")
