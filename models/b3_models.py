from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class Provento(BaseModel):
    id: int
    descricaoProduto: str
    dataPagamento: str
    tipoEvento: str
    nomeParticipante: str
    quantidadeTotal: int
    precoUnitario: float
    totalNegociado: float

class MesProventos(BaseModel):
    mesAno: str
    totalDoMes: float
    proventos: List[Provento]

class Movimento(BaseModel):
    tipoOperacao: str
    tipoMovimentacao: str
    nomeProduto: str
    instituicao: str
    quantidade: Optional[int]
    valorOperacao: Optional[float]
    precoUnitario: Optional[float]
    dataMovimentacao: str
    tipo_ativo: Optional[str]

class MesMovimentos(BaseModel):
    data: str
    movimentacoes: List[Movimento]