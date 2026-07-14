# Modi Backend

Django 기반 백엔드 서버

## 환경변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고 값을 채워주세요.

```bash
cp .env.example .env
```

| 변수 | 설명 | 예시 |
|---|---|---|
| `SECRET_KEY` | Django 시크릿 키 | `your-django-secret-key` |
| `DEBUG` | 디버그 모드 | `False` |
| `DB_ENGINE` | DB 엔진 | `django.db.backends.mysql` |
| `DB_NAME` | 데이터베이스 이름 | RDS 생성 후 입력 |
| `DB_USER` | DB 유저 | RDS 생성 후 입력 |
| `DB_PASSWORD` | DB 비밀번호 | RDS 생성 후 입력 |
| `DB_HOST` | RDS 엔드포인트 | RDS 생성 후 입력 |
| `DB_PORT` | DB 포트 | `3306` |

## 로컬 실행

DB 환경변수 없이 실행하면 SQLite를 사용합니다.

```bash
cd modi
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Docker 실행

```bash
docker build -t modi-backend .
docker run --env-file .env -p 8000:8000 modi-backend
```

## CD 파이프라인

`main` 브랜치에 push 시 GitHub Actions가 자동으로 ECR push + EC2 배포를 수행합니다.

### 필요한 GitHub Secrets

| Secret | 설명 |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM 액세스 키 |
| `AWS_SECRET_ACCESS_KEY` | IAM 시크릿 키 |
| `ECR_REGISTRY` | ECR 레지스트리 URL |
| `EC2_HOST` | EC2 퍼블릭 IP |
| `EC2_USERNAME` | SSH 유저 (예: `ubuntu`) |
| `EC2_SSH_KEY` | EC2 SSH 프라이빗 키 |
