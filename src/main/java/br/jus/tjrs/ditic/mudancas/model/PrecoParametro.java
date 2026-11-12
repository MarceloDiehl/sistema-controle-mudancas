package br.jus.tjrs.ditic.mudancas.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;

/** Valores avulsos do custo: WECOM_REALOCACAO, WECOM_INSTALACAO e WECOM_METRO_LINEAR. */
@Entity
@Table(name = "preco_parametro")
@Getter
@Setter
public class PrecoParametro {

    public static final String WECOM_REALOCACAO = "WECOM_REALOCACAO";
    public static final String WECOM_INSTALACAO = "WECOM_INSTALACAO";
    public static final String WECOM_METRO_LINEAR = "WECOM_METRO_LINEAR";

    @Id
    @Column(length = 40)
    private String chave;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal valor;
}
