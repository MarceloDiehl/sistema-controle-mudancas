package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.model.Perfil;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import br.jus.tjrs.ditic.mudancas.repository.PessoaRepository;
import br.jus.tjrs.ditic.mudancas.security.VerificadorSenha;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * Ao iniciar: cria o coordenador "admin" quando ele ainda não existe (com mudancas.admin.senha-inicial, trocada no
 * primeiro acesso) e atende o comando administrativo de redefinição de senha (mudancas.redefinir-senha=<usuário>),
 * para quando não há nenhum coordenador disponível.
 */
@Component
public class CargaInicial implements ApplicationRunner {

    public static final String LOGIN_ADMIN = "admin";
    private static final Logger LOG = LoggerFactory.getLogger(CargaInicial.class);

    private final PessoaRepository pessoas;
    private final VerificadorSenha senhas;
    private final FluxoDemanda fluxo;
    private final String senhaInicial;
    private final String redefinir;

    public CargaInicial(PessoaRepository pessoas, VerificadorSenha senhas, FluxoDemanda fluxo,
                        @Value("${mudancas.admin.senha-inicial:}") String senhaInicial,
                        @Value("${mudancas.redefinir-senha:}") String redefinir) {
        this.pessoas = pessoas;
        this.senhas = senhas;
        this.fluxo = fluxo;
        this.senhaInicial = senhaInicial;
        this.redefinir = redefinir;
    }

    @Override
    @Transactional
    public void run(ApplicationArguments args) {
        if (!pessoas.existsByLogin(LOGIN_ADMIN)) {
            if (senhaInicial.isBlank()) {
                LOG.warn("O coordenador \"admin\" não existe e mudancas.admin.senha-inicial está vazio: ninguém consegue entrar.");
            } else {
                Pessoa admin = new Pessoa();
                admin.setLogin(LOGIN_ADMIN);
                // o coordenador troca para o próprio nome em Equipe, e o histórico passa a mostrar quem fez cada coisa
                admin.setNome("Coordenador");
                admin.setNomeCurto("Coordenador");
                admin.setIniciais("CO");
                admin.setCor("#374151");
                admin.setPerfil(Perfil.COORDENADOR);
                admin.setSenhaHash(senhas.codificar(senhaInicial));
                admin.setDeveTrocarSenha(true);
                pessoas.save(admin);
                LOG.info("Coordenador \"admin\" criado. No primeiro acesso, ele cria a senha pessoal.");
            }
        }
        if (!redefinir.isBlank()) {
            Pessoa p = pessoas.findByLogin(redefinir.trim().toLowerCase()).orElse(null);
            if (p == null) {
                LOG.warn("mudancas.redefinir-senha: o usuário \"{}\" não existe.", redefinir);
                return;
            }
            String temporaria = senhas.gerarTemporaria();
            p.setSenhaHash(senhas.codificar(temporaria));
            p.setDeveTrocarSenha(true);
            p.setSenhaTemporariaExpiraEm(fluxo.agora().plusHours(24));
            p.setTentativasFalhas((short) 0);
            p.setBloqueadoAte(null);
            p.setAtivo(true);
            // o comando é do responsável pelo servidor: a senha vai só para o console, não passa pelo log da aplicação
            System.out.println("Senha temporária de " + p.getLogin() + " (válida por 24 horas): " + temporaria
                    + "\nTire mudancas.redefinir-senha da configuração antes de iniciar de novo.");
            LOG.warn("Senha de \"{}\" redefinida pelo comando administrativo.", p.getLogin());
        }
    }
}
