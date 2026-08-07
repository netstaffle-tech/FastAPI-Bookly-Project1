from .models import User
from sqlalchemy.ext.asyncio import AsyncSession 
from .schemas import UserCreateModel
from sqlalchemy import select,desc
from .utils import generate_password_hash


class UserService:
    async def get_user_by_email(self,email:str,session:AsyncSession):
        sql = select(User).where(User.email == email)
        result = await session.execute(sql)
        return result.scalar_one_or_none()
    
    async def user_exists(self,email:str,session:AsyncSession):
        user = await self.get_user_by_email(email,session)
        if user is None:
            return False
        return True

    async def create_user(self,user_data:UserCreateModel,session:AsyncSession):
        user_data_dict = user_data.model_dump()
        password = user_data_dict.pop("password")
        new_user = User(**user_data_dict,password_hash=generate_password_hash(password))
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
