package br.jus.tjrs.ditic.mudancas;

import br.jus.tjrs.ditic.mudancas.dto.DemandaDtos;
import br.jus.tjrs.ditic.mudancas.service.AutomacaoService;
import br.jus.tjrs.ditic.mudancas.service.DemandaService;
import br.jus.tjrs.ditic.mudancas.service.PrecoService;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * O script db/dados_ficticios.sql roda sobre o banco do script principal e deixa as demandas coerentes com as regras:
 * a automação de status não muda nada logo depois da carga. Usa um banco H2 só dele.
 */
@SpringBootTest(properties = "spring.datasource.url=jdbc:h2:mem:ficticios;MODE=MySQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1")
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class DadosFicticiosTest {

    @Autowired JdbcTemplate jdbc;
    @Autowired DemandaService demandas;
    @Autowired AutomacaoService automacao;
    @Autowired PrecoService precos;

    @BeforeAll
    void carregar() throws Exception {
        String sql = Files.readString(Path.of("db", "dados_ficticios.sql"), StandardCharsets.UTF_8);
        for (String comando : sql.split(";\\s*\\n")) {
            String limpo = comando.lines().filter(l -> !l.strip().startsWith("--")).collect(Collectors.joining("\n")).strip();
            if (limpo.isEmpty() || limpo.startsWith("USE ") || limpo.startsWith("SET NAMES")) continue;
            jdbc.execute(limpo);
        }
    }

    @Test
    void carregaTodasAsSituacoesECoerentesComAsDatas() {
        Map<String, Long> antes = porSituacao(demandas.listar());
        assertThat(antes).containsEntry("nova", 6L).containsEntry("acionada", 5L).containsEntry("atendimento", 4L)
                .containsEntry("pendente", 5L).containsEntry("concluida", 5L).containsEntry("cancelada", 3L);
        // as datas foram montadas para o dia em que o script roda: a automação não tem o que mudar
        automacao.executar();
        assertThat(porSituacao(demandas.listar())).isEqualTo(antes);
        assertThat(demandas.lixeira()).hasSize(1);
    }

    @Test
    void ticketsDe7DigitosECustoCalculavel() {
        List<DemandaDtos.Demanda> ls = demandas.listar();
        assertThat(ls).allSatisfy(d -> {
            if (d.ticketPrincipal() != null) assertThat(d.ticketPrincipal()).matches("\\d{7}");
            d.subtickets().forEach(s -> assertThat(s.numero()).matches("\\d{7}"));
            assertThat(d.regiao()).as("local do catálogo").isNotNull();
            precos.custo(d.id());
        });
        assertThat(ls.stream().filter(d -> "pendente".equals(d.situacao())).mapToLong(d -> precos.custo(d.id()).total()).sum()).isPositive();
    }

    private static Map<String, Long> porSituacao(List<DemandaDtos.Demanda> ls) {
        return ls.stream().collect(Collectors.groupingBy(DemandaDtos.Demanda::situacao, Collectors.counting()));
    }
}
