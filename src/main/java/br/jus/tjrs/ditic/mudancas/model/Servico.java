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

@Entity
@Table(name = "servico")
@Getter
@Setter
public class Servico {

    /** Serviços da WECOM com regra própria de custo; só a Infraestrutura usa o metro linear. */
    public static final String REALOCACAO = "Realocação";
    public static final String INSTALACAO = "Instalação";
    public static final String INFRAESTRUTURA = "Infraestrutura";

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "empresa_id", nullable = false)
    private Empresa empresa;

    @Column(nullable = false, length = 40)
    private String nome;

    /** Metro linear: só WECOM em Infraestrutura. */
    public static boolean usaMetro(String empresa, String servico) {
        return Empresa.WECOM.equals(empresa) && INFRAESTRUTURA.equals(servico);
    }
}
