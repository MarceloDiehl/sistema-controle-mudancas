package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.model.Demanda;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.time.LocalTime;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/** Conversões e validações de formato. */
class FormatosTest {

    @Test
    void dataAceitaSoDiasReaisDe2000a2100() {
        assertThat(Formatos.data("2026-11-12")).isEqualTo(LocalDate.of(2026, 11, 12));
        assertThat(Formatos.data("")).isNull();
        assertThat(Formatos.data(null)).isNull();
        assertThatThrownBy(() -> Formatos.data("2026-02-30")).isInstanceOf(RegraException.class);
        assertThatThrownBy(() -> Formatos.data("1999-12-31")).isInstanceOf(RegraException.class);
        assertThatThrownBy(() -> Formatos.data("12/11/2026")).isInstanceOf(RegraException.class);
    }

    @Test
    void horaVaiDe0000a2359() {
        assertThat(Formatos.hora("09:30")).isEqualTo(LocalTime.of(9, 30));
        assertThat(Formatos.hora(" ")).isNull();
        assertThatThrownBy(() -> Formatos.hora("24:00")).isInstanceOf(RegraException.class);
        assertThatThrownBy(() -> Formatos.hora("9:30")).isInstanceOf(RegraException.class);
    }

    @Test
    void seiETicketTemFormatoFixo() {
        assertThat(Formatos.SEI.matcher("8.2026.9745/000342-7").matches()).isTrue();
        assertThat(Formatos.SEI.matcher("8.2026.9745/00342-7").matches()).isFalse();
        assertThat(Formatos.TICKET.matcher("18313601").matches()).isTrue();
        assertThat(Formatos.TICKET.matcher("183136").matches()).isFalse();
        assertThat(Formatos.TICKET.matcher("183136012").matches()).isFalse();
    }

    @Test
    void agendaPorExtenso() {
        Demanda d = new Demanda();
        assertThat(Formatos.agendaComHora(d)).isEqualTo("Sem data agendada");
        d.setDataInicio(LocalDate.of(2026, 11, 12));
        d.setHorario(LocalTime.of(9, 0));
        assertThat(Formatos.agendaComHora(d)).isEqualTo("12/11/2026 às 09:00");
        d.setDataFim(LocalDate.of(2026, 11, 13));
        assertThat(Formatos.agendaComHora(d)).isEqualTo("12/11/2026 às 09:00 até 13/11/2026");
    }

    @Test
    void textoRespeitaOLimite() {
        assertThat(Formatos.texto("  Sala   1001  ", 20, "Campo")).isEqualTo("Sala 1001");
        assertThat(Formatos.texto("   ", 20, "Campo")).isNull();
        assertThatThrownBy(() -> Formatos.texto("x".repeat(21), 20, "Campo")).isInstanceOf(RegraException.class);
        assertThat(Formatos.normal("São Gabriel")).isEqualTo("sao gabriel");
    }
}
