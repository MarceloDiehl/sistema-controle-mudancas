package br.jus.tjrs.ditic.mudancas.service;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/** Regras de formato das contas da Equipe. */
class EquipeServiceTest {

    @Test
    void iniciaisDoPrimeiroEDoUltimoNome() {
        assertThat(EquipeService.iniciais("Ana Souza")).isEqualTo("AS");
        assertThat(EquipeService.iniciais("Marcelo Luis da Silva Diehl")).isEqualTo("MD");
        assertThat(EquipeService.iniciais("Bruno")).isEqualTo("BR");
    }

    @Test
    void usuarioEmMinusculasSemAcento() {
        assertThat(EquipeService.login("  Ana.Souza ")).isEqualTo("ana.souza");
        assertThatThrownBy(() -> EquipeService.login("a")).isInstanceOf(RegraException.class);
        assertThatThrownBy(() -> EquipeService.login("joão")).isInstanceOf(RegraException.class);
        assertThatThrownBy(() -> EquipeService.login("ana souza")).isInstanceOf(RegraException.class);
    }

    @Test
    void nomeObrigatorio() {
        assertThat(EquipeService.nome("  Ana   Souza ")).isEqualTo("Ana Souza");
        assertThatThrownBy(() -> EquipeService.nome(" ")).isInstanceOf(RegraException.class);
    }
}
