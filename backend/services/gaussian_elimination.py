import sympy as sp
from typing import List, Dict, Any

def convert_to_sympy_matrix(raw_matrix: List[List[Any]]) -> sp.Matrix:
    """Convierte la entrada a una matriz de SymPy interpretando fracciones/números, con validaciones robustas."""
    sympy_matrix = []
    for r_idx, row in enumerate(raw_matrix):
        sympy_row = []
        for c_idx, val in enumerate(row):
            if val is None or (isinstance(val, str) and val.strip() == ""):
                raise ValueError(f"Fila {r_idx+1}, Columna {c_idx+1}: El campo no puede estar vacío.")
            
            try:
                if isinstance(val, str):
                    val_clean = val.strip().replace(' ', '')
                    if '/' in val_clean:
                        parts = val_clean.split('/')
                        if len(parts) != 2:
                            raise ValueError()
                        num = sp.sympify(parts[0])
                        den = sp.sympify(parts[1])
                        if not num.is_number or not den.is_number:
                            raise ValueError()
                        if den == 0:
                            raise ZeroDivisionError()
                        sympy_row.append(sp.nsimplify(num / den))
                    else:
                        s_val = sp.sympify(val_clean)
                        if not s_val.is_number:
                            raise ValueError()
                        sympy_row.append(s_val)
                else:
                    s_val = sp.nsimplify(val)
                    if not s_val.is_number:
                        raise ValueError()
                    sympy_row.append(s_val)
            except ZeroDivisionError:
                raise ValueError(f"Fila {r_idx+1}, Columna {c_idx+1}: División por cero (ej. '{val}').")
            except Exception:
                raise ValueError(f"Fila {r_idx+1}, Columna {c_idx+1}: Valor inválido '{val}'. Debe ser un número entero, decimal o fracción (ej. 3, -1.5, 2/3).")
        sympy_matrix.append(sympy_row)
    return sp.Matrix(sympy_matrix)


def gaussian_elimination_steps(raw_matrix: List[List[Any]]) -> Dict[str, Any]:
    """
    Realiza la eliminación gaussiana devolviendo los pasos intermedios.
    """
    M = convert_to_sympy_matrix(raw_matrix)
    original_latex = sp.latex(M)
    steps = []
    
    rows, cols = M.shape
    r = 0 # Fila actual del pivote
    
    for c in range(cols):
        if r >= rows:
            break
            
        # Buscar el pivote
        pivot_row = r
        while pivot_row < rows and M[pivot_row, c] == 0:
            pivot_row += 1
            
        if pivot_row == rows:
            continue # Columna de ceros por debajo de r
            
        # Intercambio de filas si el pivote no está en la fila actual
        if pivot_row != r:
            M.row_swap(r, pivot_row)
            steps.append({
                "description": f"Intercambiar fila {r+1} con fila {pivot_row+1} para posicionar el pivote.",
                "matrix_latex": sp.latex(M)
            })
            
        # Hacer el pivote igual a 1
        pivot_val = M[r, c]
        if pivot_val != 1:
            # Multiplicar la fila por 1/pivot_val
            M.row_op(r, lambda v, j: v / pivot_val)
            steps.append({
                "description": f"Multiplicar la fila {r+1} por ${sp.latex(1/pivot_val)}$ para hacer el pivote 1.",
                "matrix_latex": sp.latex(M)
            })
            
        # Hacer ceros por debajo del pivote
        for i in range(r + 1, rows):
            factor = M[i, c]
            if factor != 0:
                # F_i = F_i - factor * F_r
                M.row_op(i, lambda v, j: v - factor * M[r, j])
                steps.append({
                    "description": f"Restar a la fila {i+1} la fila {r+1} multiplicada por ${sp.latex(factor)}$ para hacer ceros bajo el pivote.",
                    "matrix_latex": sp.latex(M)
                })
        r += 1
        
    solution_list = None
    if cols == rows + 1:
        # Es un sistema de ecuaciones del tipo N x (N+1)
        # 1. Verificar inconsistencia
        inconsistent = False
        for i in range(rows):
            all_zeros = True
            for j in range(cols - 1):
                if M[i, j] != 0:
                    all_zeros = False
                    break
            if all_zeros and M[i, cols - 1] != 0:
                inconsistent = True
                break
                
        if inconsistent:
            steps.append({
                "description": "El sistema es **Incompatible** (no tiene solución), ya que se llega a una inconsistencia del tipo $0 = k$ (con $k \\neq 0$).",
                "matrix_latex": ""
            })
        else:
            # Calcular rango
            rank = 0
            for i in range(rows):
                if any(M[i, j] != 0 for j in range(cols - 1)):
                    rank += 1
            
            n_vars = cols - 1
            if rank < n_vars:
                steps.append({
                    "description": f"El sistema tiene **Infinitas Soluciones** (sistema compatible indeterminado). El número de variables (${n_vars}$) es mayor que el rango de la matriz de coeficientes (${rank}$).",
                    "matrix_latex": ""
                })
            else:
                steps.append({
                    "description": "El sistema tiene **Solución Única**. Procedemos con la sustitución hacia atrás.",
                    "matrix_latex": ""
                })
                
                sol_vals = [None] * n_vars
                # Ir desde la última fila hacia arriba
                for i in range(n_vars - 1, -1, -1):
                    const_term = M[i, n_vars]
                    terms_str = []
                    subbed_val = const_term
                    
                    for j in range(i + 1, n_vars):
                        coef = M[i, j]
                        if coef != 0:
                            subbed_val -= coef * sol_vals[j]
                            val_j_latex = sp.latex(sol_vals[j])
                            if coef > 0:
                                terms_str.append(f"- ({sp.latex(coef)})({val_j_latex})")
                            else:
                                terms_str.append(f"+ ({sp.latex(-coef)})({val_j_latex})")
                    
                    sol_vals[i] = sp.simplify(subbed_val)
                    
                    var_name = f"x_{{{i+1}}}"
                    if not terms_str:
                        desc_step = f"De la fila {i+1} obtenemos directamente: ${var_name} = {sp.latex(sol_vals[i])}$."
                    else:
                        sub_expr = "".join(terms_str)
                        desc_step = f"Sustituimos las variables ya conocidas en la fila {i+1}: ${var_name} = {sp.latex(const_term)} {sub_expr} = {sp.latex(sol_vals[i])}$."
                    
                    steps.append({
                        "description": desc_step,
                        "matrix_latex": ""
                    })
                
                solution_list = [f"x_{{{i+1}}} = {sp.latex(sol_vals[i])}" for i in range(n_vars)]

    return {
        "original_matrix_latex": original_latex,
        "steps": steps,
        "final_matrix_latex": sp.latex(M),
        "solution": solution_list
    }

