from datetime import datetime, timedelta

from apoio import banco, entrar_admin, esperar_url, finalizar


def test_ct_001_10(page, registro):
    inicio = datetime.now() - timedelta(seconds=2)
    entrar_admin(page)
    page.click("a.app-logout")
    esperar_url(page, r"/welcome")
    with banco() as c, c.cursor() as cur:
        cur.execute(
            "SELECT log_operacao, tipo_acao, entidade_afetada, usuario_perfil, log_data, usu_id FROM tb_log "
            "WHERE log_data >= %s ORDER BY log_id", (inicio.strftime("%Y-%m-%d %H:%M:%S"),),
        )
        linhas = cur.fetchall()
    operacoes = [linha[0] for linha in linhas]
    for linha in linhas:
        registro.passo(log_operacao=linha[0], tipo_acao=linha[1], entidade=linha[2], perfil=linha[3], data=linha[4], usu_id=linha[5])
    registro.conferir("login" in operacoes, f"Sem registro de login na tb_log (operações: {operacoes})")
    registro.conferir("logout" in operacoes, f"Sem registro de logout na tb_log (operações: {operacoes})")
    finalizar(registro)
