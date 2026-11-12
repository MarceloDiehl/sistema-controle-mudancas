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

import java.time.LocalDateTime;

/** Auditoria da exclusão e da remoção definitiva da lixeira (sobrevive à remoção da demanda). */
@Entity
@Table(name = "demanda_excluida")
@Getter
@Setter
public class DemandaExcluida {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "demanda_id", nullable = false)
    private Long demandaId;

    @Column(length = 20)
    private String sei;

    @Column(name = "local_texto", length = 120)
    private String localTexto;

    @Column(nullable = false, length = 20)
    private String situacao;

    @Column(name = "excluida_em", nullable = false)
    private LocalDateTime excluidaEm;

    /** null = o sistema (remoção definitiva depois de 30 dias). */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "excluida_por_id")
    private Pessoa excluidaPor;

    @Column(length = 100)
    private String motivo;

    @Column(length = 250)
    private String texto;
}
