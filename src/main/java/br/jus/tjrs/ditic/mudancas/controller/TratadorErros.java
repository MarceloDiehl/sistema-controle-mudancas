package br.jus.tjrs.ditic.mudancas.controller;

import br.jus.tjrs.ditic.mudancas.service.RegraException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import java.util.Map;

/** Todo erro da API sai como {"mensagem": "..."}, que a tela mostra como aviso. */
@RestControllerAdvice
public class TratadorErros {

    private static final Logger LOG = LoggerFactory.getLogger(TratadorErros.class);

    @ExceptionHandler(RegraException.class)
    public ResponseEntity<Map<String, String>> regra(RegraException e) {
        return ResponseEntity.status(e.getStatus()).body(Map.of("mensagem", e.getMessage()));
    }

    @ExceptionHandler({HttpMessageNotReadableException.class, MethodArgumentTypeMismatchException.class})
    public ResponseEntity<Map<String, String>> invalido(Exception e) {
        return ResponseEntity.badRequest().body(Map.of("mensagem", "Dados inválidos. Confira os campos e tente de novo."));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> inesperado(Exception e) throws Exception {
        // deixa o Spring tratar o que já tem resposta própria (rota inexistente, método não permitido...)
        if (e instanceof org.springframework.web.ErrorResponse) throw e;
        LOG.error("Erro inesperado na API", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("mensagem", "Erro inesperado no servidor. Tente de novo; se continuar, avise o suporte."));
    }
}
