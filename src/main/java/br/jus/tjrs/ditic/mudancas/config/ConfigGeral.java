package br.jus.tjrs.ditic.mudancas.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;

import java.time.Clock;
import java.time.ZoneId;

@Configuration
@EnableScheduling
public class ConfigGeral {

    public static final ZoneId FUSO = ZoneId.of("America/Sao_Paulo");

    /** Hoje e agora sempre no horário de Brasília, qualquer que seja o fuso do servidor. */
    @Bean
    public Clock relogio() {
        return Clock.system(FUSO);
    }
}
