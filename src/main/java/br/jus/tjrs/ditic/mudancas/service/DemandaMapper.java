package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.dto.DemandaDtos;
import br.jus.tjrs.ditic.mudancas.model.Carga;
import br.jus.tjrs.ditic.mudancas.model.Demanda;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;

import java.util.List;

import static br.jus.tjrs.ditic.mudancas.service.Formatos.hora;
import static br.jus.tjrs.ditic.mudancas.service.Formatos.iso;

/** Demanda no formato da tela (precisa de uma transação aberta para ler os subtickets e o histórico). */
public final class DemandaMapper {

    private DemandaMapper() { }

    /** Com {@code qtdHistorico} negativo, inclui o histórico completo. */
    public static DemandaDtos.Demanda dto(Demanda d, int qtdHistorico) {
        boolean completo = qtdHistorico < 0;
        List<DemandaDtos.Historico> hist = completo
                ? d.getHistorico().stream().map(h -> new DemandaDtos.Historico(iso(h.getDataHora()), autor(h.getAutor()), h.getTexto())).toList()
                : null;
        String responsavel = switch (d.getCarga()) {
            case TECNICO -> id(d.getTecnico());
            case COORDENADOR -> FluxoDemanda.COORDENADOR;
            case SETOR -> null;
        };
        DemandaDtos.Aviso aviso = d.getAvisoTipo() == null ? null : new DemandaDtos.Aviso(d.getAvisoTipo().id(),
                FluxoDemanda.AVISO_COORDENADOR.equals(d.getAvisoPara()) ? FluxoDemanda.COORDENADOR : d.getAvisoPara(), iso(d.getAvisoEm()));
        return new DemandaDtos.Demanda(
                d.getId(), d.getSei() == null ? "" : d.getSei(), d.getDescricao(), d.getLocalTexto(),
                d.getLocal() == null ? null : d.getLocal().getRegiao(),
                responsavel, d.getCarga() == Carga.TECNICO ? null : id(d.getTecnico()),
                iso(d.getDataInicio()), iso(d.getDataFim()), hora(d.getHorario()),
                d.getSituacao().id(), d.getTicketPrincipal(),
                d.getTicketPrincipal() == null || d.getTicketEm() == null ? null : new DemandaDtos.TicketEm(iso(d.getTicketEm()), autor(d.getTicketPor())),
                iso(d.getAcionadaEm()),
                d.getSubtickets().stream().map(s -> new DemandaDtos.Subticket(s.getEmpresa().getNome(), s.getNumero(), s.nomeServico(),
                        s.getQuantidade(), s.getMetroLinear())).toList(),
                d.getInformacoes() == null ? "" : d.getInformacoes(),
                hist, completo ? hist.size() : qtdHistorico,
                iso(d.getCriadaEm().toLocalDate()), aviso, d.getMotivoCancelamento(),
                iso(d.getExcluidaEm()), id(d.getExcluidaPor()), d.getMotivoExclusao());
    }

    private static String id(Pessoa p) { return p == null ? null : String.valueOf(p.getId()); }

    private static String autor(Pessoa p) { return p == null ? "sistema" : String.valueOf(p.getId()); }
}
