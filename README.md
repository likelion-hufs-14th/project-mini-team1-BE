# Modi Backend

Django REST Framework 기반 백엔드 서버

## 기술 스택

- Python 3.12 / Django 5.2 / DRF 3.17
- Nginx + Let's Encrypt (HTTPS)
- Gunicorn (WSGI)
- SQLite (기본) / MySQL (RDS 연결 예정)
- GitHub Actions + AWS SSM 배포

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

## API 문서

서버 실행 후 아래 URL에서 확인 가능합니다.

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

## 배포 구조

```
Client → Nginx (80/443) → Gunicorn (8000) → Django
```

- 도메인: `antiaging-hufs.store`
- HTTPS: Let's Encrypt 인증서 적용
- CORS 허용: `https://project-mini-team1-fe.vercel.app`, `localhost:5173`

## CD 파이프라인

`main` 브랜치에 push 시 GitHub Actions가 AWS SSM을 통해 EC2에 자동 배포합니다.

### 필요한 GitHub Secrets

| Secret | 설명 |
|---|---|
| `AWS_ROLE_ARN` | OIDC IAM Role ARN |
| `EC2_INSTANCE_ID` | EC2 인스턴스 ID |
| `ENV_FILE` | .env 파일 내용 |

## 서버 Nginx 설정

```bash
sudo cp nginx/nginx.conf /etc/nginx/sites-available/antiaging-hufs.store
sudo ln -s /etc/nginx/sites-available/antiaging-hufs.store /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```
