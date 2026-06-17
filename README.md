# PRONTUARIO

Projeto Django inicial para o SaaS PRONTUARIO.

## Desenvolvimento local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Endpoints iniciais:

- `/` pagina inicial
- `/healthcheck/` verificacao simples da aplicacao
- `/admin/` Django Admin

## Deploy

Este repositorio esta preparado para ser clonado no servidor e atualizado via `git pull`.
