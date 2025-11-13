# Database Monitoring System with Flask

Система моніторингу бази даних з використанням Prometheus та Grafana для відстеження активності користувачів та роботи з ресурсами.

## Архітектура

Система складається з наступних компонентів:

1. **PostgreSQL Database** - Зберігання ресурсів, користувачів та статистики використання
2. **Data Generator** - Python скрипт для симуляції активності в БД
3. **Prometheus** - Збір та зберігання метрик (Time Series Database)
4. **Postgres Exporter** - Експорт метрик PostgreSQL до Prometheus
5. **Grafana** - Візуалізація метрик через дашборди
6. **Auth Service** - Flask сервіс з JWT аутентифікацією та CRUD API

## Функціональність

- ✅ JWT токен-базована аутентифікація
- ✅ CRUD операції з ресурсами (авторизовані користувачі)
- ✅ Prometheus метрики для відстеження дій користувачів
- ✅ Автоматична ініціалізація баз даних
- ✅ Real-time збір та візуалізація метрик
- ✅ Генерація тестових даних

## Швидкий старт

### Вимоги

- Docker
- Docker Compose v2

### Запуск системи

```bash
docker-compose down -v && docker-compose up -d --build
```

Очікуйте 30-60 секунд для ініціалізації всіх сервісів.

### Перевірка статусу

```bash
docker-compose ps
```

### Доступ до сервісів

- **Auth Service**: http://localhost:5000
- **Prometheus Metrics**: http://localhost:5000/metrics
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **PostgreSQL**: localhost:55432 (metrics/metrics_pass)

## API Endpoints

### Аутентифікація

**Реєстрація користувача**
```bash
POST /register
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "password": "password123"
}

Response (201):
{
  "message": "User registered successfully"
}
```

**Вхід в систему (Login)**
```bash
POST /login
Content-Type: application/json

Body:
{
  "email": "admin@example.com",
  "password": "admin"
}

Response (200):
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Перевірка токену**
```bash
GET /verify
Authorization: Bearer <your-token>

Response (200):
{
  "message": "Token is valid",
  "email": "admin@example.com"
}
```

### CRUD операції (потрібен JWT токен)

**Створити ресурс**
```bash
POST /actions/create
Authorization: Bearer <your-token>
Content-Type: application/json

Body:
{
  "name": "Resource Name",
  "author": "Author Name",
  "annotation": "Description",
  "kind": "article",
  "purpose": "education",
  "open_date": "2024-01-01",
  "expiry_date": "2025-01-01",
  "usage_conditions": "public",
  "url": "https://example.com"
}

Response (201):
{
  "message": "Resource created successfully",
  "id": 1
}
```

**Отримати всі ресурси**
```bash
GET /actions/read
Authorization: Bearer <your-token>

Response (200):
{
  "message": "Resources retrieved successfully",
  "data": [...]
}
```

**Оновити ресурс**
```bash
POST /actions/update
Authorization: Bearer <your-token>
Content-Type: application/json

Body:
{
  "id": 1,
  "name": "Updated Name",
  "annotation": "Updated description"
}

Response (200):
{
  "message": "Resource updated successfully",
  "id": 1
}
```

**Видалити ресурс**
```bash
DELETE /actions/delete
Authorization: Bearer <your-token>
Content-Type: application/json

Body:
{
  "id": 1
}

Response (200):
{
  "message": "Resource deleted successfully",
  "id": 1
}
```

### Моніторинг

**Prometheus метрики**
```bash
GET /metrics

Response: Prometheus-formatted metrics
```

## Тестові користувачі

За замовчуванням доступні користувачі (визначені в `auth/init.db.sql`):
- `admin@example.com` / `admin`
- `user@example.com` / `user`

## Тестування

Запустіть автоматизований тестовий скрипт:
```bash
python test_auth.py
```

Скрипт тестує:
- Реєстрацію нових користувачів
- Логін з правильними та неправильними credentials
- Перевірку токену
- CRUD операції (create, read, update, delete)
- Метрики

## Метрики

Система збирає наступні метрики:

- `user_actions_total{action="create|read|update|delete", user="email"}` - Кількість операцій по типу та користувачу
- `flask_http_request_total` - Загальна кількість HTTP запитів
- `flask_http_request_duration_seconds` - Тривалість запитів
- PostgreSQL метрики (через postgres_exporter):
  - Активні з'єднання
  - Кількість транзакцій
  - Розмір БД
  - І багато інших

## Структура проекту

```
/
├── auth/                      # Сервіс аутентифікації
│   ├── main.py               # Flask API з JWT та CRUD
│   ├── database.py           # Ініціалізація SQLite БД
│   ├── init.db.sql           # SQL схема для users.db
│   ├── entrypoint.sh         # Startup скрипт для Docker
│   ├── Dockerfile            # Docker образ auth сервісу
│   ├── requirements.txt      # Python залежності
│   └── users.db              # SQLite база користувачів
├── python/                   # Генератор даних
│   ├── generator.py          # Скрипт симуляції активності
│   ├── Dockerfile            # Docker образ генератора
│   └── requirements.txt      # Python залежності
├── sql/                      # PostgreSQL ініціалізація
│   └── init.sql              # SQL схема для resources, app_users, usage_stats
├── grafana/                  # Grafana конфігурація
│   ├── provisioning/         # Auto-provisioning
│   │   ├── dashboards/
│   │   │   └── default.yml
│   │   └── datasources/
│   │       └── prometheus.yml
│   └── dashboards/           # JSON дашборди
│       ├── auth_service_monitoring.json
│       └── business_metrics.json
├── prometheus/               # Prometheus конфігурація
│   └── prometheus.yml        # Scrape configs
├── docker-compose.yml        # Оркестрація сервісів
├── test_auth.py             # Автоматизовані тести
└── README.md                # Цей файл
```

## Команди

### Перегляд логів

```bash
# Логи всіх сервісів
docker-compose logs -f

# Логи конкретного сервісу
docker-compose logs -f auth
docker-compose logs -f postgres
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f generator
```

## Grafana Dashboards

Система включає 2 преконфігуровані дашборди:

### 1. Auth Service Monitoring
- HTTP request rate
- Request duration
- Error rate
- User actions по типу (create/read/update/delete)

### 2. Business Metrics
- Resource operations rate (INSERT/UPDATE/DELETE)
- Total resources
- Active users
- Usage statistics records
- Database operations over time

Доступ: http://localhost:3000 (admin/admin)

## Розширення

### Додавання нових метрик

Додайте Counter/Gauge/Histogram в `auth/main.py`:
```python
from prometheus_client import Counter

custom_metric = Counter('metric_name', 'Description', ['label1', 'label2'])
custom_metric.labels(label1='value1', label2='value2').inc()
```

### Додавання нових endpoints

Створіть новий Blueprint або додайте route в `auth/main.py`:
```python
@app.route('/new-endpoint', methods=['GET'])
@verify_token
def new_endpoint():
    # Your logic here
    return jsonify({'data': 'response'}), 200
```