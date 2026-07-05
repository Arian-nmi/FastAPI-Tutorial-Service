from pydantic import BaseModel, Field, field_validator


class UserLoginSchema(BaseModel):
    username: str = Field(..., max_length=250, description="username of a user")
    password: str = Field(..., max_length=250, description="password of a user")


class UserRegisterSchema(BaseModel):
    username: str = Field(..., max_length=250, description="username of a user")
    password: str = Field(..., min_length=8, max_length=250, description="password of a user")
    password_confirm: str = Field(..., min_length=8, max_length=250, description="password confirmation")


    @field_validator("password_confirm")
    def check_password_match(cls, password_confirm, validation):
        if password_confirm != validation.data.get("password"):
            raise ValueError("password doesn't match")
        return password_confirm
    

class UserRefreshTokenSchema(BaseModel):
    refresh_token: str = Field(..., description="refresh token of a user")