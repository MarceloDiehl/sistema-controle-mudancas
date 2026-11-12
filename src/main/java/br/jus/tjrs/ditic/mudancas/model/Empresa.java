package br.jus.tjrs.ditic.mudancas.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

/** Empresa contratada. As pagas por serviço (CDS e WECOM) entram no custo do relatório. */
@Entity
@Table(name = "empresa")
@Getter
@Setter
public class Empresa {

    /** A WECOM tem valores próprios (preco_parametro); as demais pagas por serviço usam o preço por região. */
    public static final String WECOM = "WECOM";

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 30)
    private String nome;

    @Column(name = "paga_por_servico", nullable = false)
    private boolean pagaPorServico;
}
