package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.dto.DemandaDtos;
import br.jus.tjrs.ditic.mudancas.model.Carga;
import br.jus.tjrs.ditic.mudancas.model.Demanda;
import br.jus.tjrs.ditic.mudancas.model.DemandaExcluida;
import br.jus.tjrs.ditic.mudancas.model.Empresa;
import br.jus.tjrs.ditic.mudancas.model.Local;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import br.jus.tjrs.ditic.mudancas.model.Servico;
import br.jus.tjrs.ditic.mudancas.model.Situacao;
import br.jus.tjrs.ditic.mudancas.model.Subticket;
import br.jus.tjrs.ditic.mudancas.model.TipoAviso;
import br.jus.tjrs.ditic.mudancas.model.TipoHistorico;
import br.jus.tjrs.ditic.mudancas.repository.DemandaExcluidaRepository;
import br.jus.tjrs.ditic.mudancas.repository.DemandaRepository;
import br.jus.tjrs.ditic.mudancas.repository.EmpresaRepository;
import br.jus.tjrs.ditic.mudancas.repository.LocalRepository;
import br.jus.tjrs.ditic.mudancas.repository.PessoaRepository;
import br.jus.tjrs.ditic.mudancas.repository.ServicoRepository;
import br.jus.tjrs.ditic.mudancas.security.UsuarioLogado;
import br.jus.tjrs.ditic.mudancas.service.FluxoDemanda.Responsavel;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import static br.jus.tjrs.ditic.mudancas.service.Formatos.agendaComHora;
import static br.jus.tjrs.ditic.mudancas.service.Formatos.num4;

/** Regras da demanda. Qualquer técnico ou coordenador altera qualquer demanda em aberto. */
@Service
@Transactional
public class DemandaService {

    private static final Pattern PREFIXO_FORO = Pattern.compile("^foro da comarca de\\s+", Pattern.CASE_INSENSITIVE);
    private static final String MSG_ENCERRADA = "Demanda encerrada: somente consulta.";

    private final DemandaRepository demandas;
    private final DemandaExcluidaRepository excluidas;
    private final PessoaRepository pessoas;
    private final LocalRepository locais;
    private final EmpresaRepository empresas;
    private final ServicoRepository servicos;
    private final FluxoDemanda fluxo;

    public DemandaService(DemandaRepository demandas, DemandaExcluidaRepository excluidas, PessoaRepository pessoas,
                          LocalRepository locais, EmpresaRepository empresas, ServicoRepository servicos, FluxoDemanda fluxo) {
        this.demandas = demandas;
        this.excluidas = excluidas;
        this.pessoas = pessoas;
        this.locais = locais;
        this.empresas = empresas;
        this.servicos = servicos;
        this.fluxo = fluxo;
    }

    // ------------------------------------------------------------------ consulta

    /** Demandas fora da lixeira, sem o histórico (vem ao abrir o card), mas com a quantidade de registros. */
    @Transactional(readOnly = true)
    public List<DemandaDtos.Demanda> listar() {
        Map<Long, Long> qtd = new HashMap<>();
        demandas.contarHistorico().forEach(l -> qtd.put((Long) l[0], (Long) l[1]));
        return demandas.listarComSubtickets().stream()
                .sorted(Comparator.comparing(Demanda::getId))
                .map(d -> DemandaMapper.dto(d, qtd.getOrDefault(d.getId(), 0L).intValue())).toList();
    }

    @Transactional(readOnly = true)
    public DemandaDtos.Demanda buscar(Long id) {
        return completo(carregar(id));
    }

    @Transactional(readOnly = true)
    public List<DemandaDtos.Demanda> lixeira() {
        return demandas.listarLixeira().stream()
                .sorted(Comparator.comparing(Demanda::getExcluidaEm).reversed())
                .map(d -> DemandaMapper.dto(d, d.getHistorico().size())).toList();
    }

    // ------------------------------------------------------------------ inclusão e detalhes

    public DemandaDtos.Resposta criar(DemandaDtos.Nova req, UsuarioLogado u) {
        Pessoa autor = autor(u);
        Demanda d = new Demanda();
        d.setSei(sei(req.sei()));
        definirLocal(d, req.comarca());
        d.setDescricao(Formatos.obrigatorio(req.descricao(), 250, "Descreva a demanda.", "Descrição"));
        LocalDate inicio = Formatos.data(req.inicio());
        LocalDate fim = Formatos.data(req.fim());
        conferirPeriodo(inicio, fim);
        d.setDataInicio(inicio);
        d.setDataFim(Objects.equals(fim, inicio) ? null : fim);
        d.setHorario(Formatos.hora(req.hora()));
        d.setSituacao(Situacao.NOVA);
        d.setCriadaEm(fluxo.agora());
        d.setAtualizadaEm(d.getCriadaEm());
        Responsavel resp = fluxo.responsavel(req.responsavel());
        d.setCarga(resp.carga());
        d.setTecnico(resp.tecnico());
        if (resp.tecnico() != null) d.getPassou().add(resp.tecnico().getId());
        fluxo.registrar(d, TipoHistorico.CRIACAO, "Demanda registrada a partir do expediente SEI e " + FluxoDemanda.atribuidaA(resp) + ".", autor);
        fluxo.avisar(d, TipoAviso.NOVA);
        fluxo.automatizar(d);
        demandas.save(d);
        String atencao = d.getSei() == null ? null : demandas.findBySeiAndIdNotOrderById(d.getSei(), d.getId()).stream().findFirst()
                .map(x -> "Este SEI também está em outra demanda (" + x.getLocalTexto() + "). Confira se não é a mesma.").orElse(null);
        return new DemandaDtos.Resposta(completo(d), atencao, null);
    }

    public DemandaDtos.Resposta salvarDados(Long id, DemandaDtos.Dados req, UsuarioLogado u) {
        Demanda d = carregar(id);
        exigirAberta(d);
        Pessoa autor = autor(u);
        String sei = sei(req.sei());
        LocalDate inicio = Formatos.data(req.inicio());
        LocalDate fim = Formatos.data(req.fim());
        conferirPeriodo(inicio, fim);
        LocalDate hoje = fluxo.hoje();
        LocalDate fimPeriodo = fim != null ? fim : inicio;
        Situacao s = d.getSituacao();
        if (s != Situacao.NOVA && inicio == null) throw RegraException.invalido("Depois de acionada, a demanda precisa ter Data de Início.");
        if (s == Situacao.ACIONADA && fimPeriodo.isBefore(hoje)) throw RegraException.invalido("Em demanda acionada, o agendamento não pode estar no passado.");
        if (s == Situacao.EM_ATENDIMENTO && inicio.isAfter(hoje)) throw RegraException.invalido("Em atendimento, a Data de Início não pode ser depois de hoje.");
        if (s == Situacao.PARA_VALIDACAO && !fimPeriodo.isBefore(hoje)) throw RegraException.invalido("Em Para Validação, o período já terminou: a Data para Conclusão precisa ser anterior a hoje.");
        LocalTime hora = Formatos.hora(req.hora());
        String descricao = Formatos.obrigatorio(req.descricao(), 250, "Descreva a demanda.", "Descrição");
        String informacoes = Formatos.texto(req.informacoes(), 100, "Informações adicionais");
        Responsavel novo = fluxo.responsavel(req.responsavel());

        String seiAntes = d.getSei();
        boolean dadosMudaram = !Objects.equals(seiAntes, sei) || !Objects.equals(d.getDescricao(), descricao)
                || !Objects.equals(d.getInformacoes(), informacoes) || !Objects.equals(d.getLocalTexto(), cidade(req.comarca()));
        LocalDate fimGravado = Objects.equals(fim, inicio) ? null : fim;
        boolean agendaMudou = !Objects.equals(d.getDataInicio(), inicio) || !Objects.equals(d.getDataFim(), fimGravado) || !Objects.equals(d.getHorario(), hora);

        fluxo.atribuir(d, novo, autor, "");
        d.setSei(sei);
        definirLocal(d, req.comarca());
        d.setDescricao(descricao);
        d.setInformacoes(informacoes);
        d.setDataInicio(inicio);
        d.setDataFim(fimGravado);
        d.setHorario(hora);
        if (agendaMudou) fluxo.registrar(d, TipoHistorico.AGENDAMENTO, "Agendamento alterado para " + agendaComHora(d) + ".", autor);
        else if (dadosMudaram) fluxo.registrar(d, TipoHistorico.DADOS, "Dados da demanda atualizados.", autor);
        fluxo.automatizar(d);
        String atencao = sei == null || sei.equals(seiAntes) ? null : demandas.findBySeiAndIdNotOrderById(sei, d.getId()).stream().findFirst()
                .map(x -> "Atenção: este SEI também está na demanda " + num4(x.getId()) + " (" + x.getLocalTexto() + ").").orElse(null);
        return new DemandaDtos.Resposta(completo(d), atencao, null);
    }

    // ------------------------------------------------------------------ status

    public DemandaDtos.Resposta mudarSituacao(Long id, DemandaDtos.MudancaSituacao req, UsuarioLogado u) {
        Demanda d = carregar(id);
        Pessoa autor = autor(u);
        Situacao nova = Situacao.doId(req.situacao());
        if (nova == Situacao.ACIONADA) {
            exigirAberta(d);
            acionar(d, autor);
        } else if (nova == Situacao.CONCLUIDA) {
            concluir(d, autor);
        } else if (nova == Situacao.CANCELADA) {
            if (!u.coordenador()) throw RegraException.proibido("Somente o coordenador pode fazer isso.");
            cancelar(d, Formatos.obrigatorio(req.motivo(), 100, "Informe o motivo.", "Motivo"), autor);
        } else {
            throw RegraException.invalido("Esta mudança de status não é permitida.");
        }
        return new DemandaDtos.Resposta(completo(d), null, null);
    }

    /** Nova → Acionada, com ticket principal e Data de Início. Com o período já em curso, a automação segue adiante. */
    private void acionar(Demanda d, Pessoa autor) {
        if (d.getSituacao() != Situacao.NOVA) throw RegraException.conflito("Esta mudança de status não é mais permitida.");
        if (d.getTicketPrincipal() == null) throw RegraException.conflito("Para marcar como Acionada, registre antes o ticket principal e salve.");
        if (d.getDataInicio() == null) throw RegraException.conflito("Para marcar como Acionada, informe a Data de Início e salve.");
        d.setSituacao(Situacao.ACIONADA);
        d.setAcionadaEm(FluxoDemanda.dataAcionamento(fluxo.hoje(), d));
        fluxo.registrar(d, TipoHistorico.STATUS, "Empresas acionadas. Status alterado: Nova → Acionada.", autor);
        fluxo.avisar(d, TipoAviso.STATUS);
        fluxo.automatizar(d);
    }

    /** Para validação → Concluída: a demanda fica com o Setor e guarda o técnico que atendeu. */
    private void concluir(Demanda d, Pessoa autor) {
        if (d.getSituacao() != Situacao.PARA_VALIDACAO) throw RegraException.conflito("Só a demanda Para Validação pode ser concluída.");
        if (d.getTicketPrincipal() == null) throw RegraException.conflito("Para concluir, registre antes o ticket principal.");
        Responsavel antes = fluxo.responsavelAtual(d);
        Pessoa atendeu = d.getTecnico();
        d.setSituacao(Situacao.CONCLUIDA);
        fluxo.registrar(d, TipoHistorico.STATUS, "Status alterado: Para validação → Concluída" + (atendeu != null ? ". Atendida por " + atendeu.getNome() : "") + ".", autor);
        d.setCarga(Carga.SETOR);
        d.setTecnico(atendeu);
        fluxo.limparAviso(d);
        fluxo.registrar(d, TipoHistorico.RESPONSAVEL, "Responsável alterado: " + FluxoDemanda.nome(antes) + " → Setor (concluída, sem atribuição).", autor);
    }

    private void cancelar(Demanda d, String motivo, Pessoa autor) {
        exigirAberta(d);
        String de = d.getSituacao().rotulo();
        d.setSituacao(Situacao.CANCELADA);
        d.setMotivoCancelamento(motivo);
        fluxo.registrar(d, TipoHistorico.STATUS, "Status alterado: " + de + " → Cancelada. Motivo: " + motivo + ".", autor);
        fluxo.avisar(d, TipoAviso.STATUS);
    }

    // ------------------------------------------------------------------ tickets

    public DemandaDtos.Resposta registrarTicket(Long id, DemandaDtos.Ticket req, UsuarioLogado u) {
        Demanda d = carregar(id);
        exigirAberta(d);
        String bruto = req.numero() == null ? "" : req.numero().trim();
        String n = bruto.replaceAll("\\D", "");
        if (n.isEmpty()) throw RegraException.invalido("Informe o número do ticket.");
        if (!Formatos.TICKET.matcher(n).matches()) throw RegraException.invalido("O número do ticket tem 8 dígitos.");
        if (n.equals(d.getTicketPrincipal())) return new DemandaDtos.Resposta(completo(d), null, null);
        Pessoa autor = autor(u);
        d.setTicketPrincipal(n);
        d.setTicketEm(fluxo.agora());
        d.setTicketPor(autor);
        fluxo.registrar(d, TipoHistorico.TICKET, "Ticket principal " + n + " registrado.", autor);
        fluxo.automatizar(d);
        return new DemandaDtos.Resposta(completo(d), repetidos(List.of(n), d.getId()), null);
    }

    public DemandaDtos.Resposta incluirSubtickets(Long id, DemandaDtos.NovosSubtickets req, UsuarioLogado u) {
        Demanda d = carregar(id);
        exigirAberta(d);
        Empresa empresa = req.empresa() == null ? null : empresas.findByNome(req.empresa()).orElse(null);
        if (empresa == null) throw RegraException.invalido("Escolha a empresa.");
        List<String> nums = Arrays.stream((req.numeros() == null ? "" : req.numeros()).split("\\D+")).filter(x -> !x.isEmpty()).toList();
        if (nums.isEmpty()) throw RegraException.invalido("Informe ao menos um número de ticket (8 dígitos).");
        if (nums.stream().anyMatch(x -> x.length() != 8)) throw RegraException.invalido("Cada número de ticket tem 8 dígitos.");
        Servico servico = req.servico() == null ? null : servicos.findByEmpresaIdAndNome(empresa.getId(), req.servico()).orElse(null);
        if (servico == null) throw RegraException.invalido("Escolha o serviço do subticket.");
        Integer qtd = req.quantidade();
        if (qtd == null || qtd < 1 || qtd > 999) throw RegraException.invalido("Informe a quantidade de serviços (1 a 999).");
        Integer metro = Servico.usaMetro(empresa.getNome(), servico.getNome()) ? req.metro() : null;
        if (metro != null && (metro < 1 || metro > 9999)) throw RegraException.invalido("Informe o metro linear em número inteiro (1 a 9999).");
        List<String> novos = new LinkedHashSet<>(nums).stream()
                .filter(n -> d.getSubtickets().stream().noneMatch(s -> s.getNumero().equals(n))).toList();
        // o subticket é único: se já está em outra demanda (até na lixeira), nada é incluído
        String repetidos = novos.stream().map(n -> demandas.comSubticket(n, d.getId()).stream().findFirst()
                        .map(x -> n + " já está na demanda " + nomeDemanda(x)).orElse(null))
                .filter(Objects::nonNull).collect(Collectors.joining("; "));
        if (!repetidos.isEmpty()) throw RegraException.conflito("Subticket repetido: " + repetidos + ". Nenhum subticket foi incluído.");
        Pessoa autor = autor(u);
        for (String n : novos) {
            Subticket s = new Subticket();
            s.setDemanda(d);
            s.setEmpresa(empresa);
            s.setNumero(n);
            s.setServico(servico);
            s.setQuantidade(qtd.shortValue());
            s.setMetroLinear(metro);
            d.getSubtickets().add(s);
        }
        if (!novos.isEmpty()) {
            boolean varios = novos.size() > 1;
            fluxo.registrar(d, TipoHistorico.SUBTICKET, "Subticket" + (varios ? "s " : " ") + empresa.getNome() + " " + String.join(", ", novos)
                    + (varios ? " adicionados" : " adicionado") + " (" + servico.getNome() + ", " + qtd + (qtd == 1 ? " serviço" : " serviços")
                    + (metro != null ? ", " + metro + " m" : "") + ").", autor);
            fluxo.automatizar(d);
        }
        return new DemandaDtos.Resposta(completo(d), repetidos(novos, d.getId()), novos.size());
    }

    public DemandaDtos.Resposta alterarSubticket(Long id, String numero, DemandaDtos.CampoSubticket req, UsuarioLogado u) {
        Demanda d = carregar(id);
        exigirAberta(d);
        Subticket s = d.getSubtickets().stream().filter(x -> x.getNumero().equals(numero)).findFirst()
                .orElseThrow(() -> RegraException.naoEncontrada("Subticket não encontrado."));
        Pessoa autor = autor(u);
        String valor = req.valor() == null ? "" : req.valor().trim();
        String rotulo = "Subticket " + s.getEmpresa().getNome() + " " + s.getNumero() + ": ";
        switch (req.campo() == null ? "" : req.campo()) {
            case "servico" -> {
                Servico novo = valor.isEmpty() ? null : servicos.findByEmpresaIdAndNome(s.getEmpresa().getId(), valor)
                        .orElseThrow(() -> RegraException.invalido("Serviço não encontrado para " + s.getEmpresa().getNome() + "."));
                if (Objects.equals(s.getServico() == null ? null : s.getServico().getId(), novo == null ? null : novo.getId())) break;
                s.setServico(novo);
                if (!s.usaMetro()) s.setMetroLinear(null);
                fluxo.registrar(d, TipoHistorico.SUBTICKET, rotulo + "serviço " + (novo == null ? "não informado" : novo.getNome()) + ".", autor);
            }
            case "quantidade" -> {
                int q = inteiro(valor, 1, 999, "Informe a quantidade de serviços (1 a 999).");
                if (q == s.getQuantidade()) break;
                s.setQuantidade((short) q);
                fluxo.registrar(d, TipoHistorico.SUBTICKET, rotulo + "quantidade " + q + ".", autor);
            }
            case "metro" -> {
                if (!s.usaMetro()) throw RegraException.invalido("O metro linear é só da WECOM em Infraestrutura.");
                Integer m = valor.isEmpty() ? null : inteiro(valor, 1, 9999, "Informe o metro linear em número inteiro (1 a 9999).");
                if (Objects.equals(m, s.getMetroLinear())) break;
                s.setMetroLinear(m);
                fluxo.registrar(d, TipoHistorico.SUBTICKET, rotulo + "metro linear " + (m == null ? "não informado" : m + " m") + ".", autor);
            }
            default -> throw RegraException.invalido("Campo do subticket inválido.");
        }
        return new DemandaDtos.Resposta(completo(d), null, null);
    }

    public DemandaDtos.Resposta removerSubticket(Long id, String numero, UsuarioLogado u) {
        Demanda d = carregar(id);
        exigirAberta(d);
        Subticket s = d.getSubtickets().stream().filter(x -> x.getNumero().equals(numero)).findFirst()
                .orElseThrow(() -> RegraException.naoEncontrada("Subticket não encontrado."));
        d.getSubtickets().remove(s);
        fluxo.registrar(d, TipoHistorico.SUBTICKET, "Subticket " + s.getEmpresa().getNome() + " " + s.getNumero() + " removido.", autor(u));
        return new DemandaDtos.Resposta(completo(d), null, null);
    }

    // ------------------------------------------------------------------ histórico e textos

    /** Registrar andamento: vale também na demanda encerrada. */
    public DemandaDtos.Resposta registrarNota(Long id, DemandaDtos.Texto req, UsuarioLogado u) {
        Demanda d = carregar(id);
        fluxo.registrar(d, TipoHistorico.NOTA, Formatos.obrigatorio(req.texto(), 500, "Escreva o andamento.", "Andamento"), autor(u));
        return new DemandaDtos.Resposta(completo(d), null, null);
    }

    public DemandaDtos.Resposta registrarDocumento(Long id, DemandaDtos.Documento req, UsuarioLogado u) {
        Demanda d = carregar(id);
        String texto = switch (req.tipo() == null ? "" : req.tipo()) {
            case "relatorio" -> {
                if (d.getSituacao() != Situacao.PARA_VALIDACAO && d.getSituacao() != Situacao.CONCLUIDA)
                    throw RegraException.conflito("O relatório é gerado em Para Validação ou Concluída.");
                yield "Relatório de execução de mudança gerado (PDF).";
            }
            case "acionamento" -> "Informação de acionamento gerada e copiada.";
            default -> throw RegraException.invalido("Documento inválido.");
        };
        fluxo.registrar(d, TipoHistorico.DOCUMENTO, texto, autor(u));
        return new DemandaDtos.Resposta(completo(d), null, null);
    }

    /** O card foi aberto: a bolinha azul some, para todos. */
    public void marcarVisto(Long id) {
        fluxo.limparAviso(carregar(id));
    }

    // ------------------------------------------------------------------ exclusão e lixeira (coordenador)

    public void excluir(Long id, DemandaDtos.Motivo req, UsuarioLogado u) {
        Demanda d = carregar(id);
        if (d.getSituacao() == Situacao.CONCLUIDA) throw RegraException.conflito("Demanda concluída não pode ser excluída.");
        String motivo = Formatos.obrigatorio(req == null ? null : req.motivo(), 100, "Informe o motivo.", "Motivo");
        Pessoa autor = autor(u);
        fluxo.registrar(d, TipoHistorico.DADOS, "Demanda excluída. Motivo: " + motivo + ".", autor);
        d.setExcluidaEm(fluxo.agora());
        d.setExcluidaPor(autor);
        d.setMotivoExclusao(motivo);
        DemandaExcluida reg = new DemandaExcluida();
        reg.setDemandaId(d.getId());
        reg.setSei(d.getSei());
        reg.setLocalTexto(d.getLocalTexto());
        reg.setSituacao(d.getSituacao().name());
        reg.setExcluidaEm(d.getExcluidaEm());
        reg.setExcluidaPor(autor);
        reg.setMotivo(motivo);
        excluidas.save(reg);
    }

    public DemandaDtos.Demanda restaurar(Long id, UsuarioLogado u) {
        Demanda d = demandas.findById(id).filter(x -> x.getExcluidaEm() != null)
                .orElseThrow(() -> RegraException.naoEncontrada("Demanda não encontrada na lixeira."));
        Pessoa autor = autor(u);
        d.setExcluidaEm(null);
        d.setExcluidaPor(null);
        d.setMotivoExclusao(null);
        fluxo.registrar(d, TipoHistorico.DADOS, "Demanda restaurada da lixeira.", autor);
        // quem estava com ela foi desativado enquanto ela estava na lixeira: volta para o Coordenador
        if (d.getSituacao().aberta() && d.getCarga() == Carga.TECNICO && !d.getTecnico().isAtivo()) {
            fluxo.atribuir(d, Responsavel.COORDENADORES, autor, "responsável desativado");
        }
        fluxo.avisar(d, TipoAviso.RETORNOU);
        fluxo.automatizar(d);
        return completo(d);
    }

    // ------------------------------------------------------------------ apoio

    private Demanda carregar(Long id) {
        return demandas.findById(id).filter(d -> d.getExcluidaEm() == null)
                .orElseThrow(() -> RegraException.naoEncontrada("Demanda não encontrada. Ela pode ter sido excluída."));
    }

    private static void exigirAberta(Demanda d) {
        if (!d.getSituacao().aberta()) throw RegraException.conflito(MSG_ENCERRADA);
    }

    private Pessoa autor(UsuarioLogado u) { return pessoas.getReferenceById(u.id()); }

    private static DemandaDtos.Demanda completo(Demanda d) { return DemandaMapper.dto(d, -1); }

    private static String sei(String txt) {
        String s = txt == null ? "" : txt.trim();
        if (s.isEmpty()) return null;
        if (!Formatos.SEI.matcher(s).matches()) throw RegraException.invalido("Número incompleto. O formato é 8.AAAA.NNNN/NNNNNN-D.");
        return s;
    }

    private static String cidade(String txt) {
        return PREFIXO_FORO.matcher(txt == null ? "" : txt.trim()).replaceFirst("").replaceAll("\\s+", " ");
    }

    /** O local é escolhido na lista (catálogo): texto que não está nela é recusado. */
    private void definirLocal(Demanda d, String txt) {
        String nome = Formatos.obrigatorio(cidade(txt), 120, "Informe a comarca ou o prédio.", "Local");
        Local local = locais.findByNome(nome)
                .orElseThrow(() -> RegraException.invalido("Escolha o local na lista: \"" + nome + "\" não é uma comarca nem um prédio do catálogo."));
        d.setLocal(local);
        d.setLocalTexto(local.getNome());
    }

    private static String nomeDemanda(Demanda x) {
        return (x.getSei() != null ? x.getSei() : num4(x.getId())) + " (" + x.getLocalTexto() + ")";
    }

    private static void conferirPeriodo(LocalDate inicio, LocalDate fim) {
        if (fim != null && inicio == null) throw RegraException.invalido("Informe a data de início antes da data para conclusão.");
        if (fim != null && fim.isBefore(inicio)) throw RegraException.invalido("A data para conclusão não pode ser antes da data de início.");
    }

    private static int inteiro(String txt, int min, int max, String mensagem) {
        try {
            int v = Integer.parseInt(txt);
            if (v >= min && v <= max) return v;
        } catch (NumberFormatException e) {
            // cai na mensagem abaixo
        }
        throw RegraException.invalido(mensagem);
    }

    /** Ticket principal ou subticket de outra demanda com o mesmo número do ticket principal: só avisa, não bloqueia. */
    private String repetidos(List<String> numeros, Long id) {
        String ls = numeros.stream().map(n -> demandas.comTicket(n, id).stream().findFirst()
                        .map(x -> "o ticket " + n + " também está em " + (x.getSei() != null ? x.getSei() : "demanda " + num4(x.getId()))).orElse(null))
                .filter(Objects::nonNull).collect(Collectors.joining("; "));
        return ls.isEmpty() ? null : "Atenção: " + ls + ".";
    }
}
