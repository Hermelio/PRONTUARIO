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

Neste ambiente local ja usamos `.venv` isolado dentro do proprio projeto.

Endpoints iniciais:

- `/` pagina inicial
- `/healthcheck/` verificacao simples da aplicacao
- `/admin/` Django Admin

## Modulos iniciados

- Profissionais: dados pessoais, endereco, conselho, especialidades, status e documentos.
- Pacientes: dados cadastrais, endereco, geolocalizacao, dados clinicos, responsavel e profissional de referencia.
- Agenda: agendamento por paciente/profissional, horarios, status e recorrencias.
- Check-in/Check-out: validacao por GPS, raio permitido, distancia e duracao do atendimento.
- Prontuario Eletronico: evolucoes por paciente, historico, pesquisa, filtros e impressao.
- Avaliacoes Clinicas: modelos por especialidade, formularios personalizados e metricas comparativas.
- Intercorrencias: eventos do tratamento com gravidade, classificacao e conduta realizada.
- Exames e Documentos: anexos de exames, receitas, laudos, PDFs e fotos vinculados ao paciente.
- Financeiro: recebimentos, repasses, percentuais e fechamento mensal.
- Dashboard: indicadores gerais assistenciais, financeiros, clinicos e mapa operacional.
- Controle de Acesso: perfis administrador, coordenador, profissional e financeiro.
- Login do SaaS: `/login/`
- Portal pos-login: `/app/`

O escopo inicial esta documentado em `docs/ESCOPO_INICIAL.md`.

## Deploy

Este repositorio esta preparado para ser clonado no servidor e atualizado via `git pull`.
