package br.jus.tjrs.ditic.mudancas.dto;

import java.math.BigDecimal;
import java.util.List;

/** Catálogos e valores do custo do relatório. */
public final class CatalogoDtos {

    private CatalogoDtos() { }

    public record Catalogo(List<Local> locais, List<Empresa> empresas) { }

    /** tipo: "PREDIO_POA" ou "COMARCA". */
    public record Local(String nome, String tipo, String regiao) { }

    public record Empresa(String nome, boolean pagaPorServico, List<String> servicos) { }

    /** cds: um item por serviço, com um valor por região, na ordem de "regioes". */
    public record Precos(List<String> regioes, List<PrecoServico> cds, Wecom wecom) { }

    public record PrecoServico(String servico, List<BigDecimal> valores) { }

    /** metro: valor do metro linear da Infraestrutura. */
    public record Wecom(BigDecimal realocacao, BigDecimal instalacao, BigDecimal metro) { }
}
