# _*_ coding: utf-8 _*_
"""PLC 계층 구조 조회 응답 모델"""
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class UnitData(BaseModel):
    """Unit 데이터 모델"""
    unit: str = Field(..., description="호기")
    plc_id: str = Field(..., description="PLC ID")
    create_dt: datetime = Field(..., description="생성일시")
    user: str = Field(..., description="생성자")
    
    class Config:
        from_attributes = True


class EquipmentGroup(BaseModel):
    """장비그룹 모델"""
    equipment_group: str = Field(..., description="장비그룹")
    unit_data: List[UnitData] = Field(..., description="Unit 데이터 목록")
    
    class Config:
        from_attributes = True


class Line(BaseModel):
    """Line 모델"""
    line: str = Field(..., description="Line")
    equipment_groups: List[EquipmentGroup] = Field(..., description="장비그룹 목록")
    
    class Config:
        from_attributes = True


class Process(BaseModel):
    """공정 모델"""
    process: str = Field(..., description="공정")
    lines: List[Line] = Field(..., description="Line 목록")
    
    class Config:
        from_attributes = True


class Plant(BaseModel):
    """Plant 모델"""
    plant: str = Field(..., description="Plant")
    processes: List[Process] = Field(..., description="공정 목록")
    
    class Config:
        from_attributes = True


class PlcTreeResponse(BaseModel):
    """PLC 계층 구조 조회 응답"""
    data: List[Plant] = Field(..., description="Plant 목록")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "plant": "PLT1",
                        "processes": [
                            {
                                "process": "PLT1-PRC1",
                                "lines": [
                                    {
                                        "line": "PLT1-PRC1-LN1",
                                        "equipment_groups": [
                                            {
                                                "equipment_group": "PLT1-PRC1-LN1-EQ1",
                                                "unit_data": [
                                                    {
                                                        "unit": "PLT1-PRC1-LN1-EQ1-U1",
                                                        "plc_id": "PLT1-PRC1-LN1-EQ1-U1-PLC01",
                                                        "create_dt": "2023-10-01T10:00:00Z",
                                                        "user": "admin"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
