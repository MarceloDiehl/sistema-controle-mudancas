package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.dto.EquipeDtos;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import br.jus.tjrs.ditic.mudancas.model.SituacaoSolicitacao;
import br.jus.tjrs.ditic.mudancas.model.SolicitacaoAcesso;
import br.jus.tjrs.ditic.mudancas.repository.PessoaRepository;
import br.jus.tjrs.ditic.mudancas.repository.SolicitacaoAcessoRepository;
import br.jus.tjrs.ditic.mudancas.security.UsuarioLogado;
import br.jus.tjrs.ditic.mudancas.security.VerificadorSenha;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;

import static br.jus.tjrs.ditic.mudancas.service.Formatos.iso;

/** Entrada, troca de senha e solicitações de acesso. */
@Service
@Transactional
public class AcessoService {

    private static final Logger LOG = LoggerFactory.getLogger(AcessoService.class);
    private static final int TENTATIVAS = 5;
    private static final Duration BLOQUEIO = Duration.ofMinutes(15);
    private static final int MAX_PENDENTES = 100;
    private static final String ERRO_LOGIN = "Usuário ou senha incorretos.";

    private final PessoaRepository pessoas;
    private final SolicitacaoAcessoRepository solicitacoes;
    private final VerificadorSenha senhas;
    private final EquipeService equipe;
    private final FluxoDemanda fluxo;

    public AcessoService(PessoaRepository pessoas, SolicitacaoAcessoRepository solicitacoes, VerificadorSenha senhas,
                         EquipeService equipe, FluxoDemanda fluxo) {
        this.pessoas = pessoas;
        this.solicitacoes = solicitacoes;
        this.senhas = senhas;
        this.equipe = equipe;
        this.fluxo = fluxo;
    }

    /** As tentativas erradas ficam gravadas mesmo quando a entrada é recusada (noRollbackFor). */
    @Transactional(noRollbackFor = RegraException.class)
    public UsuarioLogado entrar(EquipeDtos.Login req) {
        String login = req.usuario() == null ? "" : req.usuario().trim().toLowerCase();
        LocalDateTime agora = fluxo.agora();
        Pessoa p = login.isEmpty() ? null : pessoas.findByLogin(login).orElse(null);
        if (p != null && p.getBloqueadoAte() != null && p.getBloqueadoAte().isAfter(agora)) {
            long min = Math.max(1, Duration.between(agora, p.getBloqueadoAte()).toMinutes() + 1);
            throw new RegraException(HttpStatus.TOO_MANY_REQUESTS, "Acesso bloqueado por excesso de tentativas. Tente de novo em " + min + (min == 1 ? " minuto." : " minutos."));
        }
        if (!senhas.confere(p, req.senha())) {
            if (p != null) {
                p.setTentativasFalhas((short) (p.getTentativasFalhas() + 1));
                if (p.getTentativasFalhas() >= TENTATIVAS) {
                    p.setBloqueadoAte(agora.plus(BLOQUEIO));
                    p.setTentativasFalhas((short) 0);
                    LOG.warn("Entrada de \"{}\" bloqueada por {} minutos depois de {} tentativas erradas.", login, BLOQUEIO.toMinutes(), TENTATIVAS);
                }
            }
            LOG.warn("Entrada recusada para \"{}\".", login);
            throw new RegraException(HttpStatus.UNAUTHORIZED, ERRO_LOGIN);
        }
        if (!p.isAtivo()) {
            LOG.warn("Entrada recusada para \"{}\": conta desativada.", login);
            throw RegraException.proibido("Conta desativada. Procure o coordenador.");
        }
        if (p.isDeveTrocarSenha() && p.getSenhaTemporariaExpiraEm() != null && p.getSenhaTemporariaExpiraEm().isBefore(agora)) {
            throw new RegraException(HttpStatus.UNAUTHORIZED, "A senha temporária expirou. Peça ao coordenador uma nova.");
        }
        p.setTentativasFalhas((short) 0);
        p.setBloqueadoAte(null);
        p.setUltimoAcesso(agora);
        LOG.info("Entrada de \"{}\".", login);
        return UsuarioLogado.de(p);
    }

    /** Primeiro acesso ou senha temporária: a pessoa cria a senha pessoal. Devolve o usuário com a nova credencial. */
    public UsuarioLogado trocarSenha(UsuarioLogado u, EquipeDtos.TrocaSenha req) {
        Pessoa p = pessoas.findById(u.id()).orElseThrow(() -> RegraException.naoEncontrada("Conta não encontrada."));
        if (!senhas.confere(p, req.atual())) throw RegraException.invalido("A senha atual está incorreta.");
        String nova = req.nova() == null ? "" : req.nova();
        if (nova.length() < 8) throw RegraException.invalido("A nova senha precisa ter pelo menos 8 caracteres.");
        if (nova.length() > 72) throw RegraException.invalido("A nova senha pode ter até 72 caracteres.");
        if (nova.equals(req.atual())) throw RegraException.invalido("A nova senha precisa ser diferente da senha atual.");
        p.setSenhaHash(senhas.codificar(nova));
        p.setDeveTrocarSenha(false);
        p.setSenhaTemporariaExpiraEm(null);
        LOG.info("\"{}\" criou a senha pessoal.", p.getLogin());
        return UsuarioLogado.de(p);
    }

    /** Pedido feito na tela de login, sem sessão. Fica pendente até um coordenador aprovar em Equipe. */
    public void solicitar(EquipeDtos.PedidoAcesso req) {
        String login = EquipeService.login(req.login());
        String nome = EquipeService.nome(req.nome());
        if (pessoas.existsByLogin(login)) throw RegraException.conflito("Já existe uma conta com esse usuário. Procure o coordenador.");
        if (solicitacoes.existsByLoginAndSituacao(login, SituacaoSolicitacao.PENDENTE)) throw RegraException.conflito("Já há um pedido de acesso pendente com esse usuário.");
        if (solicitacoes.countBySituacao(SituacaoSolicitacao.PENDENTE) >= MAX_PENDENTES)
            throw new RegraException(HttpStatus.TOO_MANY_REQUESTS, "Há muitos pedidos pendentes. Procure o coordenador.");
        SolicitacaoAcesso s = new SolicitacaoAcesso();
        s.setLogin(login);
        s.setNome(nome);
        s.setPedidaEm(fluxo.agora());
        solicitacoes.save(s);
        LOG.info("Pedido de acesso de \"{}\".", login);
    }

    @Transactional(readOnly = true)
    public List<EquipeDtos.Solicitacao> pendentes() {
        return solicitacoes.findBySituacaoOrderByPedidaEmAsc(SituacaoSolicitacao.PENDENTE).stream()
                .map(s -> new EquipeDtos.Solicitacao(s.getId(), s.getNome(), s.getLogin(), iso(s.getPedidaEm()))).toList();
    }

    public EquipeDtos.SenhaTemporaria aprovar(Long id, EquipeDtos.Aprovacao req, UsuarioLogado u) {
        SolicitacaoAcesso s = pendente(id);
        EquipeDtos.SenhaTemporaria conta = equipe.criarConta(s.getNome(), s.getLogin(), req.perfil(), req.cor(), u);
        decidir(s, SituacaoSolicitacao.APROVADA, u);
        s.setPessoa(pessoas.getReferenceById(Long.valueOf(conta.pessoa().id())));
        return conta;
    }

    public void recusar(Long id, UsuarioLogado u) {
        decidir(pendente(id), SituacaoSolicitacao.RECUSADA, u);
    }

    private SolicitacaoAcesso pendente(Long id) {
        return solicitacoes.findById(id).filter(s -> s.getSituacao() == SituacaoSolicitacao.PENDENTE)
                .orElseThrow(() -> RegraException.naoEncontrada("Pedido de acesso não encontrado ou já decidido."));
    }

    private void decidir(SolicitacaoAcesso s, SituacaoSolicitacao situacao, UsuarioLogado u) {
        s.setSituacao(situacao);
        s.setDecididaPor(pessoas.getReferenceById(u.id()));
        s.setDecididaEm(fluxo.agora());
    }
}
