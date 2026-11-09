-- BANCO DE DADOS: URNA ELETRÔNICA
-- Compatível com SQLite

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS candidatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    partido TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eleitores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identificador TEXT NOT NULL UNIQUE,
    data_voto TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    candidato_id INTEGER NOT NULL,
    FOREIGN KEY (candidato_id) REFERENCES candidatos(id)
);

-- Exemplos de candidatos para testar. Execute uma única vez.
INSERT OR IGNORE INTO candidatos (numero, nome, partido)
VALUES
    (10, 'Ana Souza', 'Partido da Educação'),
    (20, 'Bruno Lima', 'Partido da Cidade'),
    (30, 'Carla Mendes', 'Partido da Renovação');

-- Consulta de apuração:
SELECT c.numero, c.nome, c.partido, COUNT(e.id) AS total_votos
FROM candidatos c
LEFT JOIN eleitores e ON e.candidato_id = c.id
GROUP BY c.id, c.numero, c.nome, c.partido
ORDER BY total_votos DESC;
