# Django + DRF Template

Django와 Django REST Framework를 사용한 백엔드 개발을 위한 템플릿 프로젝트입니다.

## 🛠️ 기술 스택

- **Python**: 3.12+
- **Django**: 최신 버전
- **Django REST Framework**: REST API 개발
- **UV**: 패키지 관리 및 가상환경
- **SQLite**: 기본 데이터베이스 (변경 가능)

## 📦 포함된 패키지

### 메인 패키지
- `django`: Django 웹 프레임워크
- `djangorestframework`: REST API 구축
- `django-cors-headers`: CORS 처리
- `python-decouple`: 환경변수 관리
- `pillow`: 이미지 처리

### 개발용 패키지
- `black`: 코드 포맷터
- `flake8`: 코드 린터
- `pytest`: 테스트 프레임워크
- `pytest-django`: Django용 pytest 플러그인

## 🚀 빠른 시작

### 1. 레포지토리 복제
```bash
git clone <your-template-repo-url> my-new-project
cd my-new-project
```

### 2. 환경변수 설정
`.env` 파일을 수정하여 프로젝트에 맞게 설정하세요:
```env
DEBUG=True
SECRET_KEY=your-new-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 3. 의존성 설치 및 서버 실행
```bash
# 패키지 설치
uv sync

# 마이그레이션
uv run python manage.py migrate

# 슈퍼유저 생성 (선택사항)
uv run python manage.py createsuperuser

# 개발 서버 실행
uv run python manage.py runserver
```

## 📁 프로젝트 구조

```
project/
├── config/             # Django 설정
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── api/                # API 관련 파일들
│   ├── urls.py
│   ├── views.py
│   └── serializers.py
├── apps/               # Django 앱들을 여기에 생성
├── static/             # 정적 파일
├── media/              # 업로드된 미디어 파일
├── templates/          # Django 템플릿
├── .env                # 환경변수 (Git에 포함되지 않음)
├── pyproject.toml      # UV 프로젝트 설정
└── README.md
```

## 🔧 개발 도구

### 코드 포맷팅
```bash
uv run black .
```

### 코드 린팅
```bash
uv run flake8
```

### 테스트 실행
```bash
uv run pytest
```

## 📝 새 앱 추가하기

```bash
# 새 Django 앱 생성
uv run python manage.py startapp myapp apps/myapp

# settings.py의 LOCAL_APPS에 추가
LOCAL_APPS = [
    'apps.myapp',
]
```

## 🌐 API 엔드포인트

- `/api/` - API 루트
- `/api/health/` - 헬스 체크
- `/admin/` - Django 관리자

## 🔒 보안 설정

프로덕션 환경에서는 다음 사항들을 확인하세요:

1. `DEBUG=False`로 설정
2. `SECRET_KEY` 새로 생성
3. `ALLOWED_HOSTS` 적절히 설정
4. 데이터베이스 설정 변경
5. HTTPS 설정

## 📚 추가 리소스

- [Django 공식 문서](https://docs.djangoproject.com/)
- [Django REST Framework 문서](https://www.django-rest-framework.org/)
- [UV 공식 문서](https://docs.astral.sh/uv/)

## 🤝 기여하기

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 📄 라이센스

MIT License