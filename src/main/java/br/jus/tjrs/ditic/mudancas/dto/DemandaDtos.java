package br.jus.tjrs.ditic.mudancas.dto;

import java.util.List;

/**
 * Formatos de entrada e saída da API das demandas. Datas em AAAA-MM-DD, data e hora em AAAA-MM-DDTHH:MM,
 * pessoas pelo id (texto). "coordenador" é a carga compartilhada dos coordenadores; "sistema", o autor automático.
 */
public final class DemandaDtos {

    private DemandaDtos() { }

    public record Demanda(Long id, String sei, String descricao, String comarca, String regiao,
                          String responsavel, String tecnico, String inicio, String fim, String hora,
                          String situacao, String ticketPrincipal, TicketEm ticketEm, String acionadaEm,
                          List<Subticket> subtickets, String informacoes, List<Historico> historico, int qtdHistorico,
                          String criadaEm, Aviso aviso, String motivoCancelamento,
                          String excluidaEm, String excluidaPor, String motivoExclusao) { }

    public record TicketEm(String data, String usuario) { }

    public record Subticket(String empresa, String numero, String finalidade, int quantidade, Integer metro) { }

    public record Historico(String data, String usuario, String texto) { }

    public record Aviso(String tipo, String para, String em) { }

    /** Demanda alterada e, quando há, o alerta de ticket ou SEI repetido ("atencao") e quantos subtickets entraram. */
    public record Resposta(Demanda demanda, String atencao, Integer incluidos) { }

    public record Nova(String sei, String comarca, String descricao, String responsavel,
                       String inicio, String fim, String hora) { }

    public record Dados(String sei, String comarca, String descricao, String responsavel,
                        String inicio, String fim, String hora, String informacoes) { }

    /** "acionada", "concluida" ou "cancelada" (esta só do coordenador, com motivo). */
    public record MudancaSituacao(String situacao, String motivo) { }

    public record Ticket(String numero) { }

    /** Um ou mais números de 6 dígitos no mesmo campo, ex.: "183136 / 183139". */
    public record NovosSubtickets(String empresa, String numeros, String servico, Integer quantidade, Integer metro) { }

    /** campo = "servico", "quantidade" ou "metro"; valor vazio tira o serviço ou o metro linear. */
    public record CampoSubticket(String campo, String valor) { }

    public record Texto(String texto) { }

    public record Motivo(String motivo) { }

    /** "relatorio" ou "acionamento": registra no histórico que o texto foi gerado. */
    public record Documento(String tipo) { }

    /**
     * Custo do relatório, em centavos. "infra" é a parte da Infraestrutura (WECOM); "verbas", os tickets de
     * Infraestrutura sem metro linear, que usam a verba estimada; "semPreco", os tickets fora da soma.
     */
    public record Custo(long total, long infra, List<String> semPreco, List<Verba> verbas, long valorMetro, int metrosEstimados) { }

    public record Verba(String numero, long valor) { }
}
