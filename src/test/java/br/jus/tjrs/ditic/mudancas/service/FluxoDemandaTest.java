package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.model.Carga;
import br.jus.tjrs.ditic.mudancas.model.Demanda;
import br.jus.tjrs.ditic.mudancas.model.Perfil;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import br.jus.tjrs.ditic.mudancas.model.Situacao;
import br.jus.tjrs.ditic.mudancas.model.Subticket;
import br.jus.tjrs.ditic.mudancas.model.TipoAviso;
import br.jus.tjrs.ditic.mudancas.model.TipoHistorico;
import br.jus.tjrs.ditic.mudancas.service.FluxoDemanda.Responsavel;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.LocalDate;
import java.time.ZoneId;

import static org.assertj.core.api.Assertions.assertThat;

/** Mudança automática de status pelas datas e troca de responsável, com o relógio parado em 12/11/2026. */
class FluxoDemandaTest {

    private static final ZoneId FUSO = ZoneId.of("America/Sao_Paulo");
    private static final LocalDate HOJE = LocalDate.of(2026, 11, 12);
    private final FluxoDemanda fluxo = new FluxoDemanda(Clock.fixed(HOJE.atTime(10, 0).atZone(FUSO).toInstant(), FUSO), null);

    private static Demanda demanda(Situacao s, LocalDate inicio, LocalDate fim) {
        Demanda d = new Demanda();
        d.setSituacao(s);
        d.setDataInicio(inicio);
        d.setDataFim(fim);
        return d;
    }

    private static void comTickets(Demanda d, LocalDate registro) {
        d.setTicketPrincipal("18315742");
        d.setTicketEm(registro.atTime(8, 0));
        Subticket s = new Subticket();
        s.setNumero("18313601");
        d.getSubtickets().add(s);
    }

    @Test
    void acionadaEntraEmAtendimentoNaDataDeInicio() {
        Demanda d = demanda(Situacao.ACIONADA, HOJE, HOJE.plusDays(1));
        assertThat(fluxo.automatizar(d)).isTrue();
        assertThat(d.getSituacao()).isEqualTo(Situacao.EM_ATENDIMENTO);
        assertThat(d.getAvisoTipo()).isEqualTo(TipoAviso.ATENDIMENTO);
        assertThat(d.getHistorico()).singleElement().satisfies(h -> {
            assertThat(h.getTipo()).isEqualTo(TipoHistorico.STATUS_AUTOMATICO);
            assertThat(h.getAutor()).isNull();
        });
    }

    @Test
    void vaiParaValidacaoUmDiaDepoisDaConclusao() {
        Demanda ontem = demanda(Situacao.EM_ATENDIMENTO, HOJE.minusDays(3), HOJE.minusDays(1));
        assertThat(fluxo.automatizar(ontem)).isTrue();
        assertThat(ontem.getSituacao()).isEqualTo(Situacao.PARA_VALIDACAO);
        // a conclusão é hoje: ainda está em atendimento
        Demanda hoje = demanda(Situacao.EM_ATENDIMENTO, HOJE.minusDays(3), HOJE);
        assertThat(fluxo.automatizar(hoje)).isFalse();
        assertThat(hoje.getSituacao()).isEqualTo(Situacao.EM_ATENDIMENTO);
    }

    @Test
    void novaSoAvancaComTicketPrincipalESubticket() {
        Demanda sem = demanda(Situacao.NOVA, HOJE.minusDays(2), null);
        assertThat(fluxo.automatizar(sem)).isFalse();
        assertThat(sem.getSituacao()).isEqualTo(Situacao.NOVA);

        // demanda antiga: com os tickets, vai direto a Para Validação; o acionamento não fica depois do início
        Demanda antiga = demanda(Situacao.NOVA, HOJE.minusDays(10), HOJE.minusDays(9));
        comTickets(antiga, HOJE);
        assertThat(fluxo.automatizar(antiga)).isTrue();
        assertThat(antiga.getSituacao()).isEqualTo(Situacao.PARA_VALIDACAO);
        assertThat(antiga.getAcionadaEm()).isEqualTo(HOJE.minusDays(10));
    }

    @Test
    void paraValidacaoNuncaVolta() {
        Demanda d = demanda(Situacao.PARA_VALIDACAO, HOJE.plusDays(5), null);
        assertThat(fluxo.automatizar(d)).isFalse();
        assertThat(d.getSituacao()).isEqualTo(Situacao.PARA_VALIDACAO);
    }

    @Test
    void futuraOuNaLixeiraNaoMuda() {
        assertThat(fluxo.automatizar(demanda(Situacao.ACIONADA, HOJE.plusDays(2), null))).isFalse();
        Demanda excluida = demanda(Situacao.ACIONADA, HOJE.minusDays(1), null);
        excluida.setExcluidaEm(HOJE.atStartOfDay());
        assertThat(fluxo.automatizar(excluida)).isFalse();
        assertThat(excluida.getSituacao()).isEqualTo(Situacao.ACIONADA);
    }

    @Test
    void inicioCorrigidoParaAntesPuxaOAcionamento() {
        Demanda d = demanda(Situacao.ACIONADA, HOJE.plusDays(1), null);
        d.setAcionadaEm(HOJE.plusDays(3));
        assertThat(fluxo.automatizar(d)).isTrue();
        assertThat(d.getAcionadaEm()).isEqualTo(HOJE.plusDays(1));
    }

    @Test
    void trocarResponsavelAvisaERegistra() {
        Pessoa ana = new Pessoa();
        ana.setId(7L);
        ana.setNome("Ana Souza");
        ana.setPerfil(Perfil.TECNICO);
        Demanda d = demanda(Situacao.NOVA, HOJE.plusDays(5), null);

        assertThat(fluxo.atribuir(d, new Responsavel(Carga.TECNICO, ana), null, "")).isTrue();
        assertThat(d.getAvisoTipo()).isEqualTo(TipoAviso.NOVA);
        assertThat(d.getAvisoPara()).isEqualTo("7");
        assertThat(d.getHistorico().get(0).getTexto()).isEqualTo("Responsável alterado: Coordenador → Ana Souza.");

        fluxo.atribuir(d, Responsavel.COORDENADORES, null, "");
        assertThat(d.getAvisoPara()).isEqualTo(FluxoDemanda.AVISO_COORDENADOR);
        // voltou para quem já esteve com ela: "retornou"
        fluxo.atribuir(d, new Responsavel(Carga.TECNICO, ana), null, "");
        assertThat(d.getAvisoTipo()).isEqualTo(TipoAviso.RETORNOU);
        // mesmo responsável: nada muda
        assertThat(fluxo.atribuir(d, new Responsavel(Carga.TECNICO, ana), null, "")).isFalse();
    }
}
