from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    # 1. 检查账号是否已经存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="该登录账号已被注册！")
    
    # 2. 创建新用户实体
    new_user = User(
        username=request.username,
        password=request.password,
        real_name=request.real_name,
        class_name=request.class_name,
        role=request.role
    )
    
    # 3. 存入数据库
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=UserResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    # 在数据库中同时匹配账号和密码
    user = db.query(User).filter(
        User.username == request.username,
        User.password == request.password
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误！")
        
    return user