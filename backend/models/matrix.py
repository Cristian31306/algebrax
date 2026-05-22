from pydantic import BaseModel, Field, validator
from typing import List, Union

class MatrixRequest(BaseModel):
    matrix: List[List[Union[float, int, str]]] = Field(
        ..., 
        description="Matriz bidimensional de valores numéricos o fracciones (como strings ej. '1/2')"
    )

    @validator('matrix')
    def validate_matrix_dimensions(cls, v):
        if not v:
            raise ValueError("La matriz no puede estar vacía")
        
        cols = len(v[0])
        for row in v:
            if len(row) != cols:
                raise ValueError("Todas las filas deben tener la misma cantidad de columnas")
        
        return v

class StepResponse(BaseModel):
    description: str
    matrix_latex: str = "" # Hacemos que sea opcional o string vacío si no hay matriz en el paso

class MathOperationResponse(BaseModel):
    original_matrix_latex: str
    steps: List[StepResponse]
    final_matrix_latex: str
    solution: Union[List[str], None] = None

class DoubleMatrixRequest(BaseModel):
    matrix: List[List[Union[float, int, str]]]
    matrix_b: List[List[Union[float, int, str]]]
    
    @validator('matrix', 'matrix_b')
    def validate_matrix_dimensions(cls, v):
        if not v:
            raise ValueError("La matriz no puede estar vacía")
        cols = len(v[0])
        for row in v:
            if len(row) != cols:
                raise ValueError("Todas las filas deben tener la misma cantidad de columnas")
        return v

