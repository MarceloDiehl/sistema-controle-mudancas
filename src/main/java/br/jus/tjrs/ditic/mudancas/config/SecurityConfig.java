package br.jus.tjrs.ditic.mudancas.config;

import br.jus.tjrs.ditic.mudancas.repository.PessoaRepository;
import br.jus.tjrs.ditic.mudancas.security.ContaFilter;
import br.jus.tjrs.ditic.mudancas.security.RespostaJson;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.access.intercept.AuthorizationFilter;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.security.web.context.SecurityContextRepository;
import org.springframework.security.web.csrf.CsrfException;
import org.springframework.security.web.header.writers.ReferrerPolicyHeaderWriter;

/**
 * Tudo fica atrás do login, menos a tela, a entrada e o pedido de acesso.
 * Sessão no servidor com cookie protegido e proteção CSRF (o JavaScript devolve o cookie XSRF-TOKEN no
 * cabeçalho X-XSRF-TOKEN). As ações só do coordenador são barradas aqui; o cancelamento, na regra da demanda.
 */
@Configuration
public class SecurityConfig {

    static final String CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
            + "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'";

    @Bean
    public SecurityContextRepository repositorioContexto() {
        return new HttpSessionSecurityContextRepository();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http, PessoaRepository pessoas, SecurityContextRepository repositorio) throws Exception {
        http
                .csrf(csrf -> csrf.spa())
                .securityContext(c -> c.securityContextRepository(repositorio))
                .sessionManagement(s -> s.sessionFixation(f -> f.migrateSession()))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(HttpMethod.GET, "/", "/index.html", "/css/**", "/js/**", "/fonts/**", "/vendor/**", "/favicon.ico").permitAll()
                        .requestMatchers("/error").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/sessao").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/login", "/api/acesso/solicitar").permitAll()
                        .requestMatchers("/api/equipe/**", "/api/lixeira/**", "/api/acesso/solicitacoes/**").hasRole("COORDENADOR")
                        .requestMatchers(HttpMethod.PUT, "/api/precos").hasRole("COORDENADOR")
                        .requestMatchers(HttpMethod.DELETE, "/api/mudancas/*").hasRole("COORDENADOR")
                        .anyRequest().authenticated())
                .exceptionHandling(e -> e
                        .authenticationEntryPoint((req, res, ex) -> RespostaJson.enviar(res, HttpServletResponse.SC_UNAUTHORIZED, "Entre com o seu usuário para continuar."))
                        .accessDeniedHandler((req, res, ex) -> RespostaJson.enviar(res, HttpServletResponse.SC_FORBIDDEN, ex instanceof CsrfException
                                ? "A página ficou desatualizada. Recarregue e tente de novo."
                                : "Somente o coordenador pode fazer isso.")))
                .logout(l -> l.logoutUrl("/api/logout").logoutSuccessHandler((req, res, a) -> res.setStatus(HttpServletResponse.SC_NO_CONTENT)))
                .headers(h -> h
                        .contentSecurityPolicy(c -> c.policyDirectives(CSP))
                        .referrerPolicy(r -> r.policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.NO_REFERRER)))
                .addFilterBefore(new ContaFilter(pessoas), AuthorizationFilter.class);
        return http.build();
    }
}
