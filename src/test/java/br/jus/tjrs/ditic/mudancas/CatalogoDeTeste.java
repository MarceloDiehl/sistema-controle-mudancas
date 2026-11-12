package br.jus.tjrs.ditic.mudancas;

import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Nos testes (banco H2 vazio), carrega os catálogos e os preços do próprio script do banco, o trecho entre as marcas
 * [dados-iniciais] e [/dados-iniciais]: assim os testes usam exatamente os dados que vão para o MySQL.
 */
@Component
@Order(0)
public class CatalogoDeTeste implements ApplicationRunner {

    private static final Path SCRIPT = Path.of("db", "ditic_mudancas_db.sql");

    private final JdbcTemplate jdbc;

    public CatalogoDeTeste(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public void run(ApplicationArguments args) throws IOException {
        Integer n = jdbc.queryForObject("select count(*) from `local`", Integer.class);
        if (n != null && n > 0) return;
        String sql = Files.readString(SCRIPT, StandardCharsets.UTF_8);
        String trecho = sql.substring(sql.indexOf("-- [dados-iniciais]"), sql.indexOf("-- [/dados-iniciais]"));
        for (String comando : trecho.split(";\\s*\\n")) {
            String limpo = comando.lines().filter(l -> !l.strip().startsWith("--")).reduce("", (a, b) -> a + "\n" + b).strip();
            if (!limpo.isEmpty()) jdbc.execute(limpo);
        }
    }
}
