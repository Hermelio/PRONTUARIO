# PRONTUARIO - Escopo Inicial

## Visao Geral

Sistema de prontuario eletronico e gestao de atendimento domiciliar para empresas de Home Care, clinicas e profissionais autonomos que realizam visitas domiciliares.

A plataforma deve centralizar:

- Gestao de atendimentos domiciliares
- Prontuario eletronico
- Agenda de profissionais
- Avaliacoes clinicas
- Controle financeiro
- Geolocalizacao de pacientes
- Dashboards analiticos
- Geracao de PDFs
- Exportacao para Excel
- Auditoria
- Controle de permissoes por perfil

## Tecnologias

- Backend: Django e Django REST Framework
- Frontend: Bootstrap 5, HTML5, CSS3 e JavaScript
- Banco de dados: PostgreSQL em producao
- Arquivos: upload de documentos e anexos clinicos

## Modulo de Profissionais

Cadastro completo dos profissionais da empresa, incluindo dados pessoais, dados profissionais, status e documentos anexos.

Documentos previstos:

- Diploma
- Certificados
- Registro do conselho
- Documentos pessoais
- Comprovantes
- Outros arquivos

## Modulo de Pacientes

Cadastro completo de pacientes, endereco, geolocalizacao, dados clinicos, responsavel e profissional de referencia.

Recursos de geolocalizacao:

- Latitude e longitude
- Link para Google Maps
- Rota ate o paciente

## Diretriz de Implementacao

Esta primeira etapa cria a base de dados e administracao para profissionais e pacientes. As telas operacionais, API REST, agenda, prontuario clinico, financeiro e dashboards serao evoluidos em etapas seguintes.
