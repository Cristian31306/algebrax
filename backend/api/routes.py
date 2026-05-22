from fastapi import APIRouter, HTTPException
from models.matrix import MatrixRequest, DoubleMatrixRequest, MathOperationResponse
from services.gaussian_elimination import gaussian_elimination_steps
from services.cramer import cramer_steps
from services.inverse import inverse_gauss_jordan_steps, inverse_adj_steps
from services.lu_factorization import lu_factorization_steps
from services.matrix_algebra import matrix_add_steps, matrix_subtract_steps, matrix_multiply_steps, matrix_transpose_steps
from services.vector_spaces import check_linear_dependence, calculate_distance, calculate_angle, least_squares_steps
from services.linear_transformations import linear_transformation_analysis

router = APIRouter()

def execute_operation(func, request_data):
    try:
        result = func(request_data)
        return MathOperationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/solve/gaussian-elimination", response_model=MathOperationResponse)
def solve_gaussian(request: MatrixRequest):
    return execute_operation(gaussian_elimination_steps, request.matrix)

@router.post("/solve/cramer", response_model=MathOperationResponse)
def solve_cramer(request: MatrixRequest):
    return execute_operation(cramer_steps, request.matrix)

@router.post("/solve/inverse-gauss", response_model=MathOperationResponse)
def solve_inverse_gauss(request: MatrixRequest):
    return execute_operation(inverse_gauss_jordan_steps, request.matrix)

@router.post("/solve/inverse-adj", response_model=MathOperationResponse)
def solve_inverse_adj(request: MatrixRequest):
    return execute_operation(inverse_adj_steps, request.matrix)

@router.post("/solve/lu", response_model=MathOperationResponse)
def solve_lu(request: MatrixRequest):
    return execute_operation(lu_factorization_steps, request.matrix)

@router.post("/solve/matrix-algebra/add", response_model=MathOperationResponse)
def solve_add(request: DoubleMatrixRequest):
    return execute_operation(lambda req: matrix_add_steps(req.matrix, req.matrix_b), request)

@router.post("/solve/matrix-algebra/subtract", response_model=MathOperationResponse)
def solve_subtract(request: DoubleMatrixRequest):
    return execute_operation(lambda req: matrix_subtract_steps(req.matrix, req.matrix_b), request)

@router.post("/solve/matrix-algebra/multiply", response_model=MathOperationResponse)
def solve_multiply(request: DoubleMatrixRequest):
    return execute_operation(lambda req: matrix_multiply_steps(req.matrix, req.matrix_b), request)

@router.post("/solve/matrix-algebra/transpose", response_model=MathOperationResponse)
def solve_transpose(request: MatrixRequest):
    return execute_operation(matrix_transpose_steps, request.matrix)

@router.post("/solve/vector-spaces/dependence", response_model=MathOperationResponse)
def solve_dependence(request: MatrixRequest):
    return execute_operation(check_linear_dependence, request.matrix)

@router.post("/solve/vector-spaces/distance", response_model=MathOperationResponse)
def solve_distance(request: DoubleMatrixRequest):
    return execute_operation(lambda req: calculate_distance(req.matrix, req.matrix_b), request)

@router.post("/solve/vector-spaces/angle", response_model=MathOperationResponse)
def solve_angle(request: DoubleMatrixRequest):
    return execute_operation(lambda req: calculate_angle(req.matrix, req.matrix_b), request)

@router.post("/solve/vector-spaces/least-squares", response_model=MathOperationResponse)
def solve_least_squares(request: MatrixRequest):
    return execute_operation(least_squares_steps, request.matrix)

@router.post("/solve/linear-transformations/analysis", response_model=MathOperationResponse)
def solve_linear_transform(request: MatrixRequest):
    return execute_operation(linear_transformation_analysis, request.matrix)

