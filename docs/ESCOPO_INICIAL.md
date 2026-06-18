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

## Modulo de Agenda

A agenda deve funcionar como uma central operacional semelhante ao Google Agenda, com visoes diaria, semanal e mensal.

Funcionalidades previstas:

- Visualizacao global de profissionais e pacientes
- Agendamento por paciente e profissional
- Hora inicial e hora final
- Tipo de atendimento
- Observacoes
- Status: agendado, confirmado, em atendimento, finalizado e cancelado
- Reagendamento e cancelamento
- Base para arrastar e soltar atendimentos na interface
- Recorrencias diarias, semanais e mensais

Exemplos de recorrencia:

- Paciente A: 3 vezes por semana
- Paciente B: 2 vezes por semana
- Paciente C: atendimento mensal

## Modulo de Check-in e Check-out

Objetivo: validar se o profissional esteve realmente na residencia do paciente.

Check-in:

- Captura da latitude atual
- Captura da longitude atual
- Registro do horario de chegada
- Comparacao com a latitude e longitude cadastradas no paciente
- Validacao por raio configuravel: 50, 100 ou 200 metros

Check-out:

- Registro do horario de saida
- Registro da localizacao de saida
- Calculo da duracao do atendimento

Historico armazenado:

- Data e hora
- Localizacao
- Distancia da residencia
- Profissional responsavel
- Paciente
- Agendamento vinculado
