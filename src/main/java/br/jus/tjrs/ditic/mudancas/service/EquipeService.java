package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.dto.EquipeDtos;
import br.jus.tjrs.ditic.mudancas.model.Demanda;
import br.jus.tjrs.ditic.mudancas.model.Perfil;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import br.jus.tjrs.ditic.mudancas.model.Situacao;
import br.jus.tjrs.ditic.mudancas.model.TipoHistorico;
import br.jus.tjrs.ditic.mudancas.repository.DemandaRepository;
import br.jus.tjrs.ditic.mudancas.repository.PessoaRepository;
import br.jus.tjrs.ditic.mudancas.security.UsuarioLogado;
import br.jus.tjrs.ditic.mudancas.security.VerificadorSenha;
import br.jus.tjrs.ditic.mudancas.service.FluxoDemanda.Responsavel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import static br.jus.tjrs.ditic.mudancas.service.Formatos.iso;

/** Equipe e contas. Ninguém é excluído, para não perder o histórico. */
@Service
@Transactional
public class EquipeService {

    private static final Logger LOG = LoggerFactory.getLogger(EquipeService.class);
    private static final Pattern LOGIN = Pattern.compile("^[a-z0-9][a-z0-9._-]{1,59}$");
    private static final Pattern COR = Pattern.compile("^#[0-9A-Fa-f]{6}$");
    private static final String COR_PADRAO = "#5A6370";
    private static final int HORAS_SENHA_TEMPORARIA = 24;

    private final PessoaRepository pessoas;
    private final DemandaRepository demandas;
    private final VerificadorSenha senhas;
    private final FluxoDemanda fluxo;

    public EquipeService(PessoaRepository pessoas, DemandaRepository demandas, VerificadorSenha senhas, FluxoDemanda fluxo) {
        this.pessoas = pessoas;
        this.demandas = demandas;
        this.senhas = senhas;
        this.fluxo = fluxo;
    }

    /** Todos (técnicos e coordenadores, ativos ou não): os nomes aparecem no histórico e nas demandas antigas. */
    @Transactional(readOnly = true)
    public List<EquipeDtos.Pessoa> listar() {
        return pessoas.findAllByOrderByNomeAsc().stream().map(EquipeService::dto).toList();
    }

    public EquipeDtos.SenhaTemporaria criar(EquipeDtos.NovaPessoa req, UsuarioLogado u) {
        Pessoa p = new Pessoa();
        p.setLogin(login(req.login()));
        if (pessoas.existsByLogin(p.getLogin())) throw RegraException.conflito("Já existe uma conta com esse usuário.");
        definirNome(p, req.nome());
        p.setCor(cor(req.cor()));
        p.setPerfil(perfil(req.perfil()));
        String senha = senhaTemporaria(p);
        pessoas.save(p);
        LOG.info("Conta \"{}\" ({}) criada por \"{}\".", p.getLogin(), p.getPerfil(), u.login());
        return new EquipeDtos.SenhaTemporaria(dto(p), senha, iso(p.getSenhaTemporariaExpiraEm()));
    }

    public EquipeDtos.Pessoa editar(Long id, EquipeDtos.Edicao req) {
        Pessoa p = carregar(id);
        definirNome(p, req.nome());
        if (req.cor() != null) p.setCor(cor(req.cor()));
        return dto(p);
    }

    public EquipeDtos.Pessoa desativar(Long id, UsuarioLogado u) {
        Pessoa p = carregar(id);
        if (p.getId().equals(u.id())) throw RegraException.conflito("Você não pode desativar a própria conta.");
        if (p.coordenador() && pessoas.countByPerfilAndAtivoTrue(Perfil.COORDENADOR) <= 1)
            throw RegraException.conflito("É preciso manter ao menos um coordenador ativo.");
        if (!abertas(p).isEmpty()) throw RegraException.conflito(p.getNome() + " tem demandas em aberto. Transfira antes de desativar.");
        p.setAtivo(false);
        LOG.info("Conta \"{}\" desativada por \"{}\".", p.getLogin(), u.login());
        return dto(p);
    }

    public EquipeDtos.Pessoa reativar(Long id) {
        Pessoa p = carregar(id);
        p.setAtivo(true);
        return dto(p);
    }

    /**
     * Passa as demandas em aberto marcadas para outra pessoa. Ao desativar, as desmarcadas vão para o Coordenador:
     * ninguém desativado fica com demanda em aberto. Devolve quantas foram transferidas e quantas foram ao Coordenador.
     */
    public Map<String, Integer> transferir(Long id, EquipeDtos.Transferencia req, UsuarioLogado u) {
        Pessoa de = carregar(id);
        if (de.getPerfil() != Perfil.TECNICO) throw RegraException.invalido("Só os técnicos ficam com demandas.");
        List<Long> marcadas = req.demandas() == null ? List.of() : req.demandas();
        boolean semDestino = req.para() == null || req.para().isBlank();
        if (semDestino && (!marcadas.isEmpty() || !req.desativar())) throw RegraException.invalido("Escolha para quem transferir.");
        if (marcadas.isEmpty() && !req.desativar()) throw RegraException.invalido("Marque ao menos uma demanda.");
        Responsavel para = semDestino ? Responsavel.COORDENADORES : fluxo.responsavel(req.para());
        if (para.tecnico() != null && para.tecnico().getId().equals(de.getId())) throw RegraException.invalido("Escolha outra pessoa.");
        if (req.desativar() && de.getId().equals(u.id())) throw RegraException.conflito("Você não pode desativar a própria conta.");
        Pessoa autor = pessoas.getReferenceById(u.id());
        List<Demanda> abertas = abertas(de);
        int transferidas = 0;
        for (Demanda d : abertas) {
            if (!marcadas.contains(d.getId())) continue;
            fluxo.atribuir(d, para, autor, null);
            fluxo.registrar(d, TipoHistorico.RESPONSAVEL, "Demanda transferida de " + de.getNome() + " para " + FluxoDemanda.nome(para) + ".", autor);
            transferidas++;
        }
        if (transferidas != marcadas.size()) throw RegraException.conflito("Alguma demanda marcada não está mais em aberto com " + de.getNome() + ". Recarregue a página.");
        int paraCoordenador = 0;
        if (req.desativar()) {
            for (Demanda d : abertas) {
                if (marcadas.contains(d.getId())) continue;
                fluxo.atribuir(d, Responsavel.COORDENADORES, autor, null);
                fluxo.registrar(d, TipoHistorico.RESPONSAVEL, "Demanda transferida de " + de.getNome() + " para o Coordenador (" + de.getNomeCurto() + " foi desativado(a)).", autor);
                paraCoordenador++;
            }
            de.setAtivo(false);
            LOG.info("Conta \"{}\" desativada por \"{}\".", de.getLogin(), u.login());
        }
        return Map.of("transferidas", transferidas, "paraCoordenador", paraCoordenador);
    }

    /** Gera senha temporária (24 horas). A senha anterior deixa de valer e as sessões da pessoa caem. */
    public EquipeDtos.SenhaTemporaria redefinirSenha(Long id, UsuarioLogado u) {
        Pessoa p = carregar(id);
        if (p.getId().equals(u.id())) throw RegraException.conflito("Peça a outro coordenador para redefinir a sua senha.");
        String senha = senhaTemporaria(p);
        p.setTentativasFalhas((short) 0);
        p.setBloqueadoAte(null);
        LOG.info("Senha de \"{}\" redefinida por \"{}\".", p.getLogin(), u.login());
        return new EquipeDtos.SenhaTemporaria(dto(p), senha, iso(p.getSenhaTemporariaExpiraEm()));
    }

    /** Conta nova (Equipe ou solicitação aprovada), com senha temporária. */
    EquipeDtos.SenhaTemporaria criarConta(String nome, String login, String perfil, String cor, UsuarioLogado u) {
        return criar(new EquipeDtos.NovaPessoa(nome, login, perfil, cor), u);
    }

    public static String login(String txt) {
        String l = txt == null ? "" : txt.trim().toLowerCase();
        if (!LOGIN.matcher(l).matches())
            throw RegraException.invalido("Usuário: de 2 a 60 caracteres, só letras minúsculas sem acento, números, ponto, hífen e sublinhado.");
        return l;
    }

    public static String nome(String txt) {
        return Formatos.obrigatorio(txt, 60, "Informe o nome.", "Nome");
    }

    public static EquipeDtos.Pessoa dto(Pessoa p) {
        String acesso = !p.isAtivo() ? "desativado" : p.getUltimoAcesso() == null ? "aguardando" : "ativo";
        return new EquipeDtos.Pessoa(String.valueOf(p.getId()), p.getLogin(), p.getNome(), p.getNomeCurto(), p.getIniciais(), p.getCor(),
                p.getPerfil().name(), p.isAtivo(), acesso, iso(p.getUltimoAcesso()));
    }

    private void definirNome(Pessoa p, String txt) {
        String nome = nome(txt);
        boolean repetido = pessoas.findAll().stream()
                .anyMatch(x -> !x.getId().equals(p.getId()) && Formatos.normal(x.getNome()).equals(Formatos.normal(nome)));
        if (repetido) throw RegraException.conflito("Já existe alguém com esse nome na equipe.");
        p.setNome(nome);
        String primeiro = nome.split(" ")[0];
        p.setNomeCurto(primeiro.length() > 30 ? primeiro.substring(0, 30) : primeiro);
        p.setIniciais(iniciais(nome));
    }

    private String senhaTemporaria(Pessoa p) {
        String senha = senhas.gerarTemporaria();
        p.setSenhaHash(senhas.codificar(senha));
        p.setDeveTrocarSenha(true);
        p.setSenhaTemporariaExpiraEm(fluxo.agora().plusHours(HORAS_SENHA_TEMPORARIA));
        return senha;
    }

    private List<Demanda> abertas(Pessoa p) { return demandas.comTecnico(p.getId(), Situacao.ABERTAS); }

    private Pessoa carregar(Long id) {
        return pessoas.findById(id).orElseThrow(() -> RegraException.naoEncontrada("Pessoa não encontrada."));
    }

    /** Primeira letra do primeiro e do último nome (ou as duas primeiras, com um nome só). */
    static String iniciais(String nome) {
        String[] p = nome.trim().split("\\s+");
        String a = p[0];
        String b = p.length > 1 ? p[p.length - 1].substring(0, 1) : a.length() > 1 ? a.substring(1, 2) : "";
        return (a.charAt(0) + b).toUpperCase();
    }

    private static String cor(String txt) { return txt != null && COR.matcher(txt).matches() ? txt.toUpperCase() : COR_PADRAO; }

    private static Perfil perfil(String txt) { return "COORDENADOR".equals(txt) ? Perfil.COORDENADOR : Perfil.TECNICO; }
}
