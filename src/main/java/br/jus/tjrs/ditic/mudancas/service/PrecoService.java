package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.dto.CatalogoDtos;
import br.jus.tjrs.ditic.mudancas.dto.DemandaDtos;
import br.jus.tjrs.ditic.mudancas.model.Demanda;
import br.jus.tjrs.ditic.mudancas.model.Empresa;
import br.jus.tjrs.ditic.mudancas.model.PrecoCds;
import br.jus.tjrs.ditic.mudancas.model.PrecoParametro;
import br.jus.tjrs.ditic.mudancas.model.Servico;
import br.jus.tjrs.ditic.mudancas.model.Subticket;
import br.jus.tjrs.ditic.mudancas.repository.DemandaRepository;
import br.jus.tjrs.ditic.mudancas.repository.PrecoCdsRepository;
import br.jus.tjrs.ditic.mudancas.repository.PrecoParametroRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/** Valores da tela Configuração e o custo do relatório. */
@Service
@Transactional
public class PrecoService {

    /** Infraestrutura sem metro linear: verba estimada com a média de 15 metros por sala (média de 1.221 salas). */
    public static final int METROS_ESTIMADOS = 15;
    private static final BigDecimal MAXIMO = new BigDecimal("9999999.99");

    private final PrecoCdsRepository precosCds;
    private final PrecoParametroRepository parametros;
    private final DemandaRepository demandas;

    public PrecoService(PrecoCdsRepository precosCds, PrecoParametroRepository parametros, DemandaRepository demandas) {
        this.precosCds = precosCds;
        this.parametros = parametros;
        this.demandas = demandas;
    }

    @Transactional(readOnly = true)
    public CatalogoDtos.Precos precos() {
        List<PrecoCds> ls = precosCds.listarComServico();
        List<String> regioes = ls.stream().map(PrecoCds::getRegiao).distinct().toList();
        Map<String, BigDecimal[]> porServico = new LinkedHashMap<>();
        for (PrecoCds p : ls) {
            porServico.computeIfAbsent(p.getServico().getNome(), k -> new BigDecimal[regioes.size()])[regioes.indexOf(p.getRegiao())] = p.getValor();
        }
        List<CatalogoDtos.PrecoServico> cds = porServico.entrySet().stream()
                .map(e -> new CatalogoDtos.PrecoServico(e.getKey(), List.of(e.getValue()))).toList();
        return new CatalogoDtos.Precos(regioes, cds, new CatalogoDtos.Wecom(
                parametro(PrecoParametro.WECOM_REALOCACAO), parametro(PrecoParametro.WECOM_INSTALACAO), parametro(PrecoParametro.WECOM_METRO_LINEAR)));
    }

    /** Grava os valores da Configuração; todos precisam ser maiores que zero. Devolve quantos mudaram. */
    public int salvar(CatalogoDtos.Precos novos) {
        if (novos == null || novos.cds() == null || novos.wecom() == null) throw RegraException.invalido("Valores incompletos.");
        int mudaram = 0;
        List<PrecoCds> ls = precosCds.listarComServico();
        for (CatalogoDtos.PrecoServico ps : novos.cds()) {
            if (ps.valores() == null || novos.regioes() == null || ps.valores().size() != novos.regioes().size())
                throw RegraException.invalido("Valores incompletos para " + ps.servico() + ".");
            for (int i = 0; i < ps.valores().size(); i++) {
                String regiao = novos.regioes().get(i);
                PrecoCds p = ls.stream().filter(x -> x.getRegiao().equals(regiao) && x.getServico().getNome().equals(ps.servico())).findFirst()
                        .orElseThrow(() -> RegraException.invalido("Região ou serviço da CDS desconhecido."));
                mudaram += trocar(p.getValor(), valor(ps.valores().get(i)), p::setValor);
            }
        }
        mudaram += trocarParametro(PrecoParametro.WECOM_REALOCACAO, novos.wecom().realocacao());
        mudaram += trocarParametro(PrecoParametro.WECOM_INSTALACAO, novos.wecom().instalacao());
        mudaram += trocarParametro(PrecoParametro.WECOM_METRO_LINEAR, novos.wecom().metro());
        return mudaram;
    }

    /**
     * Custo da demanda, em centavos, com os valores atuais. CDS: quantidade × preço do serviço na região do local.
     * WECOM: Realocação e Instalação por quantidade; Infraestrutura pelo metro linear do ticket ou, sem ele,
     * pela verba de 15 metros (uma por ticket). Ticket sem preço fica fora da soma, em "semPreco".
     */
    @Transactional(readOnly = true)
    public DemandaDtos.Custo custo(Long id) {
        Demanda d = demandas.findById(id).filter(x -> x.getExcluidaEm() == null)
                .orElseThrow(() -> RegraException.naoEncontrada("Demanda não encontrada."));
        String regiao = d.getLocal() == null ? null : d.getLocal().getRegiao();
        long metro = centavos(parametro(PrecoParametro.WECOM_METRO_LINEAR));
        long total = 0;
        long infra = 0;
        List<String> semPreco = new ArrayList<>();
        List<DemandaDtos.Verba> verbas = new ArrayList<>();
        for (Subticket s : d.getSubtickets()) {
            if (!s.getEmpresa().isPagaPorServico()) continue;
            Long c = custo(s, regiao, metro);
            if (c == null) {
                semPreco.add(s.getNumero());
                continue;
            }
            total += c;
            if (s.usaMetro()) {
                infra += c;
                if (s.getMetroLinear() == null) verbas.add(new DemandaDtos.Verba(s.getNumero(), c));
            }
        }
        return new DemandaDtos.Custo(total, infra, semPreco, verbas, metro, METROS_ESTIMADOS);
    }

    private Long custo(Subticket s, String regiao, long metro) {
        String servico = s.nomeServico();
        if (servico == null) return null;
        if (Empresa.WECOM.equals(s.getEmpresa().getNome())) {
            return switch (servico) {
                case Servico.REALOCACAO -> centavos(parametro(PrecoParametro.WECOM_REALOCACAO)) * s.getQuantidade();
                case Servico.INSTALACAO -> centavos(parametro(PrecoParametro.WECOM_INSTALACAO)) * s.getQuantidade();
                case Servico.INFRAESTRUTURA -> s.getMetroLinear() != null ? s.getMetroLinear() * metro : METROS_ESTIMADOS * metro;
                default -> null;
            };
        }
        if (regiao == null) return null;
        Optional<PrecoCds> p = precosCds.findByRegiaoAndServicoId(regiao, s.getServico().getId());
        return p.map(x -> centavos(x.getValor()) * s.getQuantidade()).orElse(null);
    }

    private BigDecimal parametro(String chave) {
        return parametros.findById(chave).map(PrecoParametro::getValor)
                .orElseThrow(() -> new IllegalStateException("Falta o valor " + chave + " em preco_parametro (rode o script do banco)."));
    }

    private int trocarParametro(String chave, BigDecimal novo) {
        PrecoParametro p = parametros.findById(chave).orElseThrow(() -> RegraException.invalido("Valor desconhecido: " + chave + "."));
        return trocar(p.getValor(), valor(novo), p::setValor);
    }

    private static int trocar(BigDecimal atual, BigDecimal novo, java.util.function.Consumer<BigDecimal> grava) {
        if (atual.compareTo(novo) == 0) return 0;
        grava.accept(novo);
        return 1;
    }

    private static BigDecimal valor(BigDecimal v) {
        if (v == null || v.signum() <= 0 || v.compareTo(MAXIMO) > 0 || v.stripTrailingZeros().scale() > 2)
            throw RegraException.invalido("Confira os valores: todos maiores que zero, no formato 125,00.");
        return v.setScale(2, RoundingMode.UNNECESSARY);
    }

    private static long centavos(BigDecimal v) { return v.movePointRight(2).longValueExact(); }
}
