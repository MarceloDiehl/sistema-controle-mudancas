package br.jus.tjrs.ditic.mudancas.service;

import org.springframework.http.HttpStatus;

/** Regra de negócio não atendida: a mensagem vai para a tela como está. */
public class RegraException extends RuntimeException {

    private final HttpStatus status;

    public RegraException(HttpStatus status, String mensagem) {
        super(mensagem);
        this.status = status;
    }

    /** Dado inválido no pedido (400). */
    public static RegraException invalido(String mensagem) { return new RegraException(HttpStatus.BAD_REQUEST, mensagem); }

    /** A situação atual não permite a ação (409). */
    public static RegraException conflito(String mensagem) { return new RegraException(HttpStatus.CONFLICT, mensagem); }

    public static RegraException naoEncontrada(String mensagem) { return new RegraException(HttpStatus.NOT_FOUND, mensagem); }

    public static RegraException proibido(String mensagem) { return new RegraException(HttpStatus.FORBIDDEN, mensagem); }

    public HttpStatus getStatus() { return status; }
}
