package br.jus.tjrs.ditic.mudancas.security;

import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/** Resposta de erro no mesmo formato da API ({"mensagem": "..."}), para os filtros de segurança. */
public final class RespostaJson {

    private RespostaJson() { }

    public static void enviar(HttpServletResponse res, int status, String mensagem) throws IOException {
        res.setStatus(status);
        res.setContentType("application/json");
        res.setCharacterEncoding(StandardCharsets.UTF_8.name());
        // as mensagens são fixas, do próprio código: não há aspas nem barras para escapar
        res.getWriter().write("{\"mensagem\":\"" + mensagem + "\"}");
    }
}
