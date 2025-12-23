# Django 纯后端 API 服务

这是一个配置为纯后端 API 服务的 Django 项目，专为前后端分离架构设计。



## API 端点

### 公开接口（无需认证）

- `GET /api/health/` - 健康检查
- `GET /api/info/` - API 信息
- `GET /api/users/register/` - 注册接口信息
- `POST /api/users/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录

### 需要认证的接口

- `GET /api/users/` - 用户列表
- `GET /api/users/{id}/` - 获取用户详情
- `POST /api/users/` - 创建用户（等同于注册）
- `PUT /api/users/{id}/` - 更新用户信息
- `DELETE /api/users/{id}/` - 删除用户
- `GET /api/users/me/` - 获取当前用户信息
- `POST /api/auth/logout/` - 用户登出

## 配置说明



### 1. 添加了 REST Framework
- 配置了 JSON 渲染器和解析器
- 设置了认证和权限类
- 启用了分页和过滤功能

### 2. 数据库
- 使用 SQLite 作为开发数据库
- 已配置好用户认证相关表

## 环境准备

### 1. 安装依赖

首先安装项目所需的 Python 依赖包：

```bash
pip install -r requirements.txt
```

### 2. 数据库迁移

运行数据库迁移命令创建必要的表结构：

```bash
python manage.py migrate
```

## 启动服务

```bash
python manage.py runserver 8000
```

服务将在 http://127.0.0.1:8000 启动

## 测试账号

已创建的测试账号：
- **用户名**: testuser
- **密码**: testpass123

此账号可用于测试登录和认证功能。



### 认证方式
1. **Token 认证**: 在请求头中添加 `Authorization: Token your-token`
2. **Session 认证**: 先登录获取 session，后续请求会自动携带 cookie

### 权限说明
- **公开接口**: 无需任何认证即可访问，适合健康检查、用户注册等
- **认证接口**: 需要提供有效的认证凭据才能访问，适合用户管理、数据操作等

## 接口测试记录

以下是对所有接口的测试结果和使用方式：

### 1. 健康检查接口
**请求方式**: `GET /api/health/`
**状态**: ✅ 测试成功
**测试结果**:
```json
{
    "status": "healthy",
    "timestamp": "2025-12-15T12:20:34.916565Z",
    "message": "Django API Backend is running"
}
```

### 2. API 信息接口
**请求方式**: `GET /api/info/`
**状态**: ✅ 测试成功
**测试结果**:
```json
{
    "name": "Django API Backend",
    "version": "1.0.0",
    "description": "纯后端 API 服务",
    "authentication": "Bearer Token or Session Authentication required for protected endpoints",
    "public_endpoints": ["GET /api/health/", "GET /api/info/", "POST /api/users/register/", "POST /api/auth/login/"],
    "protected_endpoints": ["GET /api/users/", "GET /api/users/me/", "PUT /api/users/{id}/", "DELETE /api/users/{id}/..."],
    "endpoints": {
        "health": "/api/health/",
        "info": "/api/info/",
        "users": "/api/users/",
        "user_register": "/api/users/register/",
        "current_user": "/api/users/me/",
        "login": "/api/auth/login/",
        "logout": "/api/auth/logout/"
    }
}
```

### 3. 注册接口信息
**请求方式**: `GET /api/users/register/`
**状态**: ✅ 测试成功
**测试结果**:
```json
{
    "message": "This is the user registration endpoint.",
    "method": "POST",
    "required_fields": ["username", "password"],
    "optional_fields": ["email", "first_name", "last_name"],
    "example": {
        "username": "newuser",
        "password": "securepassword",
        "email": "user@example.com"
    }
}
```

### 4. 用户注册接口
**请求方式**: `POST /api/users/register/`
**状态**: ✅ 测试成功
**请求参数**:
```json
{
    "username": "testuser456",
    "password": "testpass123",
    "email": "test456@example.com"
}
```
**测试结果**:
```json
{
    "message": "User created successfully",
    "user": {
        "id": 4,
        "username": "testuser456",
        "email": "test456@example.com",
        "first_name": "",
        "last_name": "",
        "date_joined": "2025-12-15T12:22:37.701968Z"
    }
}
```

### 5. 用户登录接口
**请求方式**: `POST /api/auth/login/`
**状态**: ✅ 测试成功
**请求参数**:
```json
{
    "username": "testuser456",
    "password": "testpass123"
}
```
**测试结果**:
```json
{
    "message": "Login successful",
    "token": "3faa831bacce32f11600bb4e7a58e4076560fdde",
    "user": {
        "id": 4,
        "username": "testuser456",
        "email": "test456@example.com",
        "first_name": "",
        "last_name": "",
        "date_joined": "2025-12-15T12:22:37.701968Z"
    }
}
```

### 6. 用户列表接口（需要认证）
**请求方式**: `GET /api/users/`
**状态**: ✅ 测试成功
**认证方式**: Token认证 - `Authorization: Token 3faa831bacce32f11600bb4e7a58e4076560fdde`
**测试结果**:
```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        // 用户列表数据
    ]
}
```

### 7. 用户详情接口（需要认证）
**请求方式**: `GET /api/users/{id}/`
**状态**: ✅ 测试成功
**认证方式**: Token认证 - `Authorization: Token 3faa831bacce32f11600bb4e7a58e4076560fdde`
**测试结果**:
```json
{
    "id": 4,
    "username": "testuser456",
    "email": "test456@example.com",
    "first_name": "",
    "last_name": "",
    "date_joined": "2025-12-15T12:22:37.701968Z"
}
```

### 8. 当前用户信息接口（需要认证）
**请求方式**: `GET /api/users/me/`
**状态**: ✅ 测试成功
**认证方式**: Token认证 - `Authorization: Token 3faa831bacce32f11600bb4e7a58e4076560fdde`
**测试结果**:
```json
{
    "id": 4,
    "username": "testuser456",
    "email": "test456@example.com",
    "first_name": "",
    "last_name": "",
    "date_joined": "2025-12-15T12:22:37.701968Z"
}
```

### 9. 用户登出接口（需要认证）
**请求方式**: `POST /api/auth/logout/`
**状态**: ✅ 测试成功
**认证方式**: Token认证 - `Authorization: Token 3faa831bacce32f11600bb4e7a58e4076560fdde`
**测试结果**:
```json
{
    "message": "Logout successful"
}
```

## 测试总结

✅ **所有接口测试均成功完成！**

### 测试环境
- **测试时间**: 2025-12-15 12:20-12:30 (UTC)
- **测试工具**: PowerShell Invoke-RestMethod
- **服务器地址**: http://127.0.0.1:8000
- **认证Token**: 3faa831bacce32f11600bb4e7a58e4076560fdde

### 测试账号信息
- **用户名**: testuser456
- **密码**: testpass123
- **邮箱**: test456@example.com

### 注意事项
1. 所有时间戳均为UTC时间格式
2. 认证接口需要在请求头中添加 `Authorization: Token your-token`
3. 注册用户时用户名必须唯一，如果已存在会返回错误
4. Token在登出后会失效，需要重新登录获取新的Token


kkwww

ww
