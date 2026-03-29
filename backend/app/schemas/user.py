from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# 注册时前端发来的数据格式
class UserRegisterRequest(BaseModel):
    username: str
    password: str
    real_name: str
    class_name: Optional[str] = None
    role: Optional[str] = "student" # 默认注册为学生

# 登录时前端发来的数据格式
class UserLoginRequest(BaseModel):
    username: str
    password: str

# 后端返回给前端的用户信息（注意：绝对不要把密码返回给前端！）
class UserResponse(BaseModel):
    id: str
    username: str
    real_name: str
    class_name: Optional[str] = None
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)