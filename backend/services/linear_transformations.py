import sympy as sp
from typing import List, Dict, Any
from .gaussian_elimination import convert_to_sympy_matrix

def linear_transformation_analysis(raw_matrix: List[List[Any]]) -> Dict[str, Any]:
    M = convert_to_sympy_matrix(raw_matrix)
    rows, cols = M.shape
    
    original_latex = f"T(x) = Ax, \\quad A = {sp.latex(M)}"
    steps = []
    
    # Imagen (Espacio Columna)
    steps.append({
        "description": "Calculamos la Imagen (o Recorrido) de la transformación lineal. Corresponde al espacio generado por las columnas de $A$.",
        "matrix_latex": ""
    })
    
    colspace = M.columnspace()
    colspace_latex = ", \\quad ".join(sp.latex(v) for v in colspace)
    steps.append({
        "description": f"Base de la Imagen: $\\{{ {colspace_latex} \\}}$. Dimensión (Rango) = {len(colspace)}.",
        "matrix_latex": ""
    })
    
    # Núcleo (Espacio Nulo)
    steps.append({
        "description": "Calculamos el Núcleo (o Kernel) resolviendo $Ax = 0$.",
        "matrix_latex": ""
    })
    
    nullspace = M.nullspace()
    if not nullspace:
        nullspace_latex = "\\{ 0 \\}"
        dim_null = 0
    else:
        nullspace_latex = ", \\quad ".join(sp.latex(v) for v in nullspace)
        dim_null = len(nullspace)
        
    steps.append({
        "description": f"Base del Núcleo: $\\{{ {nullspace_latex} \\}}$. Nulidad = {dim_null}.",
        "matrix_latex": ""
    })
    
    # Teorema de las dimensiones
    steps.append({
        "description": f"Verificamos el Teorema de la Dimensión: $\\dim(V) = \\dim(\\text{{Imagen}}) + \\dim(\\text{{Núcleo}})$. Es decir, ${cols} = {len(colspace)} + {dim_null}$.",
        "matrix_latex": ""
    })
    
    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": f"\\text{{Img}}(T) = \\text{{span}}\\{{ {colspace_latex} \\}}, \\quad \\text{{Nuc}}(T) = \\text{{span}}\\{{ {nullspace_latex} \\}}",
        "solution": None
    }
