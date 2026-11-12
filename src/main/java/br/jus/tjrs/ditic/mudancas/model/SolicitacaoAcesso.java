package br.jus.tjrs.ditic.mudancas.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
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

/** Pedido de acesso feito na tela de login; o coordenador aprova (cria a conta) ou recusa. */
@Entity
@Table(name = "solicitacao_acesso")
@Getter
@Setter
public class SolicitacaoAcesso {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 60)
    private String login;

    @Column(nullable = false, length = 60)
    private String nome;

    @Column(name = "pedida_em", nullable = false)
    private LocalDateTime pedidaEm;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private SituacaoSolicitacao situacao = SituacaoSolicitacao.PENDENTE;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "decidida_por")
    private Pessoa decididaPor;

    @Column(name = "decidida_em")
    private LocalDateTime decididaEm;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "pessoa_id")
    private Pessoa pessoa;
}
