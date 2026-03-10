import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

SUMMARY_FILE_PATH = Path(__file__).parent / "sample_law_versions_tax.json"
DETAIL_FILE_PATH = Path(__file__).parent / "sample_law_versions_detail.json"

router = APIRouter(prefix="/law-versions", tags=["Law Versions"])

class LawVersion(BaseModel):
    id: str
    mst: str = Field(..., alias="신구법일련번호")
    law_id: str = Field(..., alias="신구법ID")
    name: str = Field(..., alias="신구법명")
    effective_date: str = Field(..., alias="시행일자")
    category: str = Field(..., alias="법령구분명")
    promulgation_date: str = Field(..., alias="공포일자")
    promulgation_no: str = Field(..., alias="공포번호")
    amendment_type: str = Field(..., alias="제개정구분명")
    department: str = Field(..., alias="소관부처명")

    class Config:
        populate_by_name = True

@router.get("/", response_model=List[LawVersion])
def get_law_versions(
    mst: Optional[str] = Query(None, description="신구법일련번호로 필터링"),
    name: Optional[str] = Query(None, description="신구법명으로 필터링 (부분 일치)")
):
    try:
        with open(SUMMARY_FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Accessing the list from the JSON structure
        versions = data.get("OldAndNewLawSearch", {}).get("oldAndNew", [])
        
        # If a query parameter is provided, filter the list
        
        if name:
            # name이 "부가가치세법"이면 "부가가치세법 시행령"도 포함되도록 'in' 연산자 사용
            versions = [v for v in versions if name in v.get("신구법명", "")]
            
        if mst:
            versions = [v for v in versions if v.get("신구법일련번호") == mst]
        
        # Otherwise, return the full list
        return versions

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="JSON file not found.")
    
# 2. Deep Content (Complex LawDetailResponse model)

# 1. 개별 조문 (최하위 단위)
class ProvisionItem(BaseModel):
    no: str
    content: str

# 2. 조문 목록 (신조문/구조문 목록)
class ProvisionList(BaseModel):
    items: List[ProvisionItem] = Field(..., alias="조문")

# 3. 상세 데이터용 기본 정보 (목록용 LawVersion과 비슷하지만 키 이름이 다름)
class LawBaseInfo(BaseModel):
    is_current: str = Field(..., alias="현행여부")
    law_id: str = Field(..., alias="법령ID")
    mst: str = Field(..., alias="법령일련번호")
    law_type: str = Field(..., alias="법종구분")
    name: str = Field(..., alias="법령명")
    effective_date: str = Field(..., alias="시행일자")
    promulgation_no: str = Field(..., alias="공포번호")
    amendment_type: str = Field(..., alias="제개정구분명")
    promulgation_date: str = Field(..., alias="공포일자")

# 4. 최종 상세 응답 모델 (OldAndNewService 객체 대응)
class LawDetailResponse(BaseModel):
    new_provisions: ProvisionList = Field(..., alias="신조문목록")
    old_provisions: ProvisionList = Field(..., alias="구조문목록")
    old_info: LawBaseInfo = Field(..., alias="구조문_기본정보")
    new_info: LawBaseInfo = Field(..., alias="신조문_기본정보")

    class Config:
        populate_by_name = True
        
# Updated Route in app/api/law_versions.py

@router.get("/{law_id}/comparison", response_model=LawDetailResponse)
def get_law_comparison(law_id: str):
    """
    Fetches the 'Old vs New' detail for a specific Law ID.
    Example: /api/law-versions/001571/comparison
    """
    try:
        with open(DETAIL_FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        detail = data.get("OldAndNewService")
        
        # Validation: Ensure the Law ID in the file matches the request
        # Note: In the detail JSON, this is often '법령ID'
        if detail["신조문_기본정보"]["법령ID"] != law_id:
            raise HTTPException(status_code=404, detail=f"No comparison found for Law ID {law_id}")
            
        return detail
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Detail data file not found.")