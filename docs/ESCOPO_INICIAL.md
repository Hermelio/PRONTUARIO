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

## Modulo de Prontuario Eletronico

Cada paciente deve possuir um historico clinico completo com evolucoes.

Campos da evolucao:

- Data
- Hora
- Profissional
- Descricao do atendimento
- Procedimentos realizados
- Conduta
- Observacoes

Funcionalidades:

- Tela especifica de prontuario por paciente
- Botao para nova evolucao
- Historico de evolucoes
- Pesquisa por texto
- Filtros por profissional e periodo
- Impressao
- Base para exportacao PDF

## Modulo de Avaliacoes

O sistema deve permitir avaliacoes clinicas especificas por especialidade.

Tipos iniciais:

- Avaliacao ortopedica
- Avaliacao gerontologica
- Avaliacao cardiorrespiratoria
- Avaliacao neurologica
- Avaliacao personalizada

Campos e indicadores previstos:

- Dor
- Amplitude de movimento
- Forca muscular
- Escalas funcionais
- Mobilidade
- Equilibrio
- Cognicao
- Independencia funcional
- Saturacao
- Frequencia cardiaca
- Frequencia respiratoria
- Escalas respiratorias
- Escalas neurologicas
- Sensibilidade

## Evolucao de Indicadores e Comparativos

As avaliacoes devem permitir comparacao ao longo do tempo, por exemplo:

- Avaliacao inicial
- Reaplicacao apos 30 dias
- Reaplicacao apos 60 dias
- Reaplicacao apos 90 dias

Comparativos gerados:

- Evolucao percentual
- Comparacao entre avaliacoes
- Indicadores de melhora
- Indicadores de piora
- Base para graficos de linha, barras e historico temporal

## Modulo de Intercorrencias

Registrar eventos ocorridos durante o tratamento.

Campos:

- Paciente
- Data
- Hora
- Profissional
- Descricao da intercorrencia
- Gravidade
- Conduta realizada
- Classificacao

Classificacoes:

- Leve
- Moderada
- Grave
- Critica

## Modulo de Exames e Documentos

Todos os arquivos devem ficar vinculados ao paciente.

Tipos previstos:

- Exames laboratoriais
- Exames de imagem
- Receitas medicas
- Relatorios
- Laudos
- PDFs
- Fotos

## Modulo Financeiro

Controle de recebimentos:

- Valor do atendimento
- Quantidade de atendimentos
- Convenio
- Particular

Controle de repasses:

- Valor recebido pela empresa
- Valor devido ao profissional
- Percentual da empresa
- Percentual do profissional

Fechamento mensal:

- Periodo de inicio e fim
- Quantidade de atendimentos realizados
- Valor total faturado
- Valor a receber pela empresa
- Valor a receber pelo profissional
- Valores pendentes

Relatorios financeiros:

- Por profissional
- Por paciente
- Por periodo
- Por convenio
- Por especialidade

## Dashboard

Indicadores gerais:

- Pacientes totais, ativos, inativos e novos
- Profissionais totais, ativos e inativos
- Atendimentos de hoje, semana, mes, pendentes e concluidos
- Faturamento mensal e anual
- Valores a receber e valores pagos
- Evolucao media dos pacientes
- Indicadores clinicos
- Mapa com pacientes cadastrados, atendimentos do dia e profissionais em atendimento

## Controle de Acesso

Perfis:

- Administrador: acesso total
- Coordenador: gestao de pacientes, profissionais e agenda
- Profissional: acesso aos proprios pacientes e atendimentos
- Financeiro: acesso aos modulos financeiros

## Diferenciais Futuros

- Aplicativo mobile Android e iOS
- Assinatura digital
- Prescricao eletronica
- Integracao WhatsApp
- Integracao Google Agenda
- Integracao com convenios
- Notificacoes automaticas
- Inteligencia Artificial para geracao de resumos clinicos
- Alertas de pacientes em risco
- Sugestao automatica de evolucao baseada no historico
