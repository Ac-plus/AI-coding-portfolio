# Backend

轻量级 OJ 后端，使用 Python 标准库实现 HTTP 服务，使用文件系统存储题目与提交记录，使用 `g++` 执行 C++17 评测。

## 启动

```bash
PYTHONPATH=/root/oj_system python3 scripts/run_backend.py
```

默认地址：`http://127.0.0.1:8000`

## 核心接口

- `GET /api/health`
- `GET /api/problems`
- `GET /api/problems/{id}`
- `GET /api/tags`
- `POST /api/problems`
- `POST /api/submissions`
- `GET /api/submissions/{id}`

## 提交格式

`POST /api/submissions`

```json
{
  "problem_id": "two-sum",
  "source_code": "#include <vector>\n#include <unordered_map>\nusing namespace std;\nclass Solution { ... };"
}
```
