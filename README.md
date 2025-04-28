# 🤖 BPMN Diagram Generator

<div align="center">

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-blue.svg)

Система автоматической генерации BPMN-диаграмм из текстового или голосового описания с AI-анализом и валидацией.

[🚀 Быстрый старт](#установка) •
[🛠 Разработка](#команды-разработчика)

</div>

## ✨ Возможности

- 🎯 Генерация BPMN 2.0 диаграмм из текста  
- 🎤 Поддержка голосового ввода с распознаванием речи  
- 🔍 AI-валидация и анализ диаграмм  
- 🛠 Автоматическое исправление ошибок в диаграммах  
- 🌐 Интерактивный веб-интерфейс для редактирования и просмотра  
- 🚀 API для интеграции с другими системами  

## 🚀 Быстрый старт

### Предварительные требования

- Docker 20.10+  
- Docker Compose 2.0+  
- NVIDIA Container Toolkit (для GPU, опционально)  

### Установка

1. Клонируйте репозиторий:  
   ```bash
   git clone https://github.com/yourusername/bpmn-diagram-generator.git
   cd bpmn-diagram-generator
   ```

2. Скопируйте файл конфигурации:  
   ```bash
   cp env.example .env
   ```

3. Измените файл конфигурации при необходимости:  
   ```bash
   nano .env
   ```

4. Запустите систему:  
   - Для CPU:  
     ```bash
     make dev-all-cpu
     ```
   - Для GPU (если доступно):  
     ```bash
     make dev-all-gpu
     ```

### Доступ к системе

- 🌐 **Frontend:** [http://localhost:3000](http://localhost:3000)  
- 🔧 **Backend API:** [http://localhost:8000](http://localhost:8000)  
- 📚 **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)  

## 🏗 Архитектура

### Технологический стек

| Компонент    | Технологии                            |
|-------------|---------------------------------------|
| Frontend    | React, BPMN.js, TypeScript            |
| Backend     | FastAPI, Taskiq, Socket.IO            |
| AI/ML       | Ollama/OpenAI LLM, Xinference (Whisper)|
| Хранилища   | PostgreSQL, Redis, RabbitMQ           |

### Структура проекта

```
.
├── backend/           # FastAPI приложение
├── frontend/         # React приложение
├── deploy/           # Docker конфигурации
├── scripts/         # Утилиты
└── Makefile         # Сборка проекта
```

## 💻 Разработка

### Команды разработчика

- Запуск frontend в режиме разработки:  
  ```bash
  make frontend-dev
  ```

- Запуск backend в режиме разработки:  
  ```bash
  make backend-dev
  ```

- Запуск инфраструктуры (базы данных, брокеры сообщений):  
  ```bash
  make infra-dev
  ```

- Запуск всех сервисов, за исключением Self-hosted Ollama и Xinference:  
  ```bash
  make without-ml
  ```

### 🔧 Конфигурация

Основные параметры конфигурации задаются в файле `.env`. Ниже приведены ключевые настройки:

#### Основные настройки
- `ENVIRONMENT` - Окружение выполнения (`local`|`dev`|`prod`)  
- `DEBUG` - Режим отладки (`1` - включено, `0` - выключено)  
- `LOG_LEVEL` - Уровень логирования (`DEBUG`|`INFO`|`WARNING`|`ERROR`)  

#### База данных PostgreSQL
- `DB_USERNAME` - Имя пользователя БД  
- `DB_PASSWORD` - Пароль БД  
- `DB_HOST` - Хост БД  
- `DB_PORT` - Порт БД (по умолчанию `5432`)  
- `DB_NAME` - Имя базы данных  
- `POSTGRESQL_URL` - Полный URL подключения (переопределяет отдельные настройки)  
  Формат: `postgresql://user:pass@host:port/dbname`

#### Конфигурация Redis
- `REDIS_PASSWORD` - Пароль Redis  
- `REDIS_HOST` - Хост Redis  
- `REDIS_PORT` - Порт Redis (по умолчанию `6379`)  
- `REDIS_FULL_URL` - Полный URL подключения к Redis  
  Формат: `redis://user:pass@host:port/0`

#### Конфигурация RabbitMQ
- `RABBITMQ_USERNAME` - Имя пользователя брокера сообщений  
- `RABBITMQ_PASSWORD` - Пароль брокера сообщений  
- `RABBITMQ_HOST` - Хост RabbitMQ  
- `RABBITMQ_PORT` - AMQP порт (по умолчанию `5672`)  
- `RABBITMQ_FULL_URL` - Полный URL подключения AMQP  
  Формат: `amqp://user:pass@host:port/`

#### Основные настройки AI
- `REQUIRE_MODELS` - Приложение не запустится, если моделей не существует 

#### Распознавание речи (Xinference)
- `XINFERENCE_API_URL` - Конечная точка API Whisper  
- `XINFERENCE_MODEL` - Название модели ASR (`whisper-large-v3-turbo`)  
- `XINFERENCE_MODEL_REPLICA` - Количество реплик модели  
- `XINFERENCE_N_GPU` - Количество используемых GPU (опционально)  

#### Провайдеры AI моделей
##### Конфигурация Ollama (по умолчанию)
- `OLLAMA_URL` - Конечная точка сервера Ollama  
- `OLLAMA_MODEL` - Модель LLM по умолчанию (`gemma3:1b`)  

##### Конфигурация OpenAI
- `USE_OPENAI` - Переключение на провайдера OpenAI (`1`-включено, `0`-выключено)  
  При включении конфигурация Ollama автоматически игнорируется  
- `OPENAI_API_TOKEN` - Ваш API-ключ OpenAI  
- `OPENAI_MODEL` - Название модели (`gemini-2.0-flash`)  
- `OPENAI_URL` - Пользовательская конечная точка API  
- `OPENAI_CHAT_COMPLETIONS_ENDPOINT` - Путь к конечной точке завершения  

#### Важные примечания:
1. При `USE_OPENAI=1`:  
   - Конфигурация Ollama игнорируется  
   - Все LLM-запросы используют OpenAI-совместимый API  

2. Для production:  
   - Всегда используйте `FULL_URL` для сложных строк подключения  

3. GPU-ускорение:  
   - Требует драйверов NVIDIA и CUDA toolkit  
   - Установите `XINFERENCE_N_GPU` для включения GPU-инференса  

4. При использовании опций с `*_FULL_URL`, конкретные конфигурации будут игнорироваться  

---

<div align="center">
  <strong>Сделано с ❤️ командой разработки</strong>
</div>
