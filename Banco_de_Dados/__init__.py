import psycopg2

#String de conexão
DATABASE_URL = "postgresql://neondb_owner:npg_9clR3uKrMkpa@ep-solitary-sun-acu02rkx-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"


def inserir_classificacao(usuario_id, noticia_id, classificacao_manchete, classificacao_contexto, classificacao_geral):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        sql = """
        INSERT INTO classificacoes (usuario_id, noticia_id, classificacao_manchete, classificacao_contexto, classificacao_geral)
        VALUES (%s, %s, %s, %s, %s)
        """

        cur.execute(sql, (usuario_id, noticia_id, classificacao_manchete, classificacao_contexto, classificacao_geral))
        conn.commit()

    except Exception as e:
        print(f"Erro ao inserir classificação: {e}")
    finally:
        cur.close()
        conn.close()

def usuario_existe(email):
    try:
        # Conecta ao banco
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Consulta para verificar se existe um usuário com esse email
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        resultado = cur.fetchone()

        if resultado:
            return True
        else:
            return False

    except Exception as e:
        print(f"Erro ao verificar usuário: {e}")
        return False  # Em caso de erro, assume que não existe

    finally:
        cur.close()
        conn.close()

def obter_noticia_por_id(noticia_id):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Seleciona as informações da notícia
        cur.execute("""
            SELECT id, manchete, descricao, link 
            FROM noticias 
            WHERE id = %s
        """, (noticia_id,))

        resultado = cur.fetchone()

        if resultado:
            noticia = {
                "id": resultado[0],
                "manchete": resultado[1],
                "descricao": resultado[2],
                "link": resultado[3]
            }
            return noticia
        else:
            return None

    except Exception as e:
        print(f"Erro ao buscar notícia: {e}")
        return None

    finally:
        cur.close()
        conn.close()



noticia = obter_noticia_por_id(1)
if noticia:
     print(noticia)
else:
     print("Notícia não encontrada.")





