CREATE SCHEMA desafio_python

CREATE TABLE desafio_python.recurso(
	nome_recurso text primary key,
	qtde_recurso int);

CREATE TABLE desafio_python.usuario(
	id_usuario text primary key,
	nome_usuario text unique,
	senha text,
	tipo text);

CREATE TABLE desafio_python.emprestimo(
	id_usuario text references desafio_python.usuario(id_usuario),
	nome_recurso text references desafio_python.recurso(nome_recurso),
	qtde_recurso int,
	data_inicio date,
	data_fim date,
	status text);