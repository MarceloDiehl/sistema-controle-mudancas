package br.jus.tjrs.ditic.mudancas.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

/** Chamado do 4Biz para uma empresa e um serviço, com a quantidade de serviços. */
@Entity
@Table(name = "subticket")
@Getter
@Setter
public class Subticket {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "demanda_id", nullable = false)
    private Demanda demanda;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "empresa_id", nullable = false)
    private Empresa empresa;

    @Column(nullable = false, unique = true, columnDefinition = "char(8)")
    private String numero;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "servico_id")
    private Servico servico;

    @Column(nullable = false)
    private short quantidade = 1;

    /** Só WECOM em Infraestrutura; opcional (conhecido depois da obra). */
    @Column(name = "metro_linear")
    private Integer metroLinear;

    public String nomeServico() { return servico == null ? null : servico.getNome(); }

    public boolean usaMetro() { return Servico.usaMetro(empresa.getNome(), nomeServico()); }
}
