"""
URNA ELETRÔNICA - ATPS
Exemplo didático em Python + SQLite.

Antes de entregar:
- Leia e teste o código.
- Personalize a interface e os dados de teste.
- Complete seus dados no README e grave o vídeo solicitado pela professora.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("urna_eletronica.db")
MINIMO_VOTOS = 10


def conectar():
    return sqlite3.connect(DB_PATH)


def criar_banco():
    """Cria as tabelas necessárias caso ainda não existam."""
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS candidatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero INTEGER NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                partido TEXT NOT NULL
            )
        """)
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS eleitores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identificador TEXT NOT NULL UNIQUE,
                data_voto TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                candidato_id INTEGER NOT NULL,
                FOREIGN KEY (candidato_id) REFERENCES candidatos(id)
            )
        """)
        conexao.commit()


def cadastrar_candidato():
    print("\n=== CADASTRO DE CANDIDATO ===")
    try:
        numero = int(input("Número do candidato: ").strip())
        nome = input("Nome do candidato: ").strip()
        partido = input("Partido: ").strip()

        if not nome or not partido:
            print("Nome e partido são obrigatórios.")
            return

        with conectar() as conexao:
            conexao.execute(
                "INSERT INTO candidatos (numero, nome, partido) VALUES (?, ?, ?)",
                (numero, nome, partido)
            )
            conexao.commit()
        print("Candidato cadastrado com sucesso!")
    except ValueError:
        print("Digite um número válido para o candidato.")
    except sqlite3.IntegrityError:
        print("Esse número já está cadastrado.")


def listar_candidatos():
    with conectar() as conexao:
        candidatos = conexao.execute(
            "SELECT id, numero, nome, partido FROM candidatos ORDER BY numero"
        ).fetchall()

    print("\n========== CANDIDATOS ==========")
    if not candidatos:
        print("Nenhum candidato cadastrado.")
    else:
        for _, numero, nome, partido in candidatos:
            print(f"Nº {numero} | {nome} | Partido: {partido}")
    print("================================")
    return candidatos


def votar():
    print("\n========== ÁREA DE VOTAÇÃO ==========")
    identificador = input("Identificação do eleitor (ex.: matrícula ou código): ").strip()

    if not identificador:
        print("A identificação não pode ficar vazia.")
        return

    with conectar() as conexao:
        ja_votou = conexao.execute(
            "SELECT 1 FROM eleitores WHERE identificador = ?",
            (identificador,)
        ).fetchone()

        if ja_votou:
            print("VOTO NÃO REGISTRADO: este eleitor já votou.")
            return

        candidatos = conexao.execute(
            "SELECT id, numero, nome, partido FROM candidatos ORDER BY numero"
        ).fetchall()

        if not candidatos:
            print("Cadastre pelo menos um candidato antes de iniciar a votação.")
            return

        print("\nCandidatos disponíveis:")
        for _, numero, nome, partido in candidatos:
            print(f"{numero} - {nome} ({partido})")

        try:
            numero_escolhido = int(input("Digite o número do seu candidato: ").strip())
        except ValueError:
            print("Número inválido. Voto não registrado.")
            return

        candidato = conexao.execute(
            "SELECT id, nome FROM candidatos WHERE numero = ?",
            (numero_escolhido,)
        ).fetchone()

        if candidato is None:
            print("Candidato não encontrado. Voto não registrado.")
            return

        confirmacao = input(
            f"Confirma seu voto em {candidato[1]}? (S/N): "
        ).strip().upper()

        if confirmacao != "S":
            print("Votação cancelada. Nenhum voto foi registrado.")
            return

        try:
            conexao.execute(
                "INSERT INTO eleitores (identificador, candidato_id) VALUES (?, ?)",
                (identificador, candidato[0])
            )
            conexao.commit()
            print("VOTO COMPUTADO COM SUCESSO!")
        except sqlite3.IntegrityError:
            print("Não foi possível registrar: eleitor já votou ou dados inválidos.")


def mostrar_resultado():
    with conectar() as conexao:
        total = conexao.execute("SELECT COUNT(*) FROM eleitores").fetchone()[0]
        resultados = conexao.execute("""
            SELECT c.numero, c.nome, c.partido, COUNT(e.id) AS votos
            FROM candidatos c
            LEFT JOIN eleitores e ON e.candidato_id = c.id
            GROUP BY c.id, c.numero, c.nome, c.partido
            ORDER BY votos DESC, c.numero
        """).fetchall()

    print("\n========== RESULTADO DA ELEIÇÃO ==========")
    print(f"Total de votos registrados: {total}")
    if not resultados:
        print("Não há candidatos cadastrados.")
        return

    for numero, nome, partido, votos in resultados:
        percentual = (votos / total * 100) if total else 0
        print(f"Nº {numero} | {nome} ({partido})")
        print(f"Votos: {votos} | Percentual: {percentual:.1f}%")
        print("-" * 40)

    maior_votacao = resultados[0][3]
    vencedores = [r for r in resultados if r[3] == maior_votacao]

    if total == 0:
        print("Ainda não há votos para definir um resultado.")
    elif len(vencedores) > 1:
        print("Resultado: empate entre os candidatos acima.")
    else:
        print(f"Mais votado: {vencedores[0][1]}")

    print("==========================================")


def painel():
    with conectar() as conexao:
        total = conexao.execute("SELECT COUNT(*) FROM eleitores").fetchone()[0]
        quantidade = conexao.execute("SELECT COUNT(*) FROM candidatos").fetchone()[0]
    print("\n========== PAINEL DA URNA ==========")
    print(f"Candidatos cadastrados: {quantidade}")
    print(f"Votos computados: {total}")
    print(f"Meta mínima da atividade: {MINIMO_VOTOS} votações")
    if total < MINIMO_VOTOS:
        print(f"Faltam {MINIMO_VOTOS - total} voto(s) para atingir o mínimo.")
    else:
        print("Mínimo de 10 votações atingido!")
    print("====================================")


def menu():
    criar_banco()

    while True:
        print("""
╔══════════════════════════════════════╗
║          SISTEMA DE URNA             ║
╠══════════════════════════════════════╣
║ 1 - Cadastrar candidato              ║
║ 2 - Listar candidatos                ║
║ 3 - Registrar voto                   ║
║ 4 - Exibir resultado                 ║
║ 5 - Ver painel da votação            ║
║ 0 - Sair                             ║
╚══════════════════════════════════════╝
""")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_candidato()
        elif opcao == "2":
            listar_candidatos()
        elif opcao == "3":
            votar()
        elif opcao == "4":
            mostrar_resultado()
        elif opcao == "5":
            painel()
        elif opcao == "0":
            print("Sistema encerrado. Obrigado!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
