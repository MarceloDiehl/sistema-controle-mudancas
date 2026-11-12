package br.jus.tjrs.ditic.mudancas.model;

import jakarta.persistence.CascadeType;
import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OrderBy;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Demanda de mudança, do expediente SEI à conclusão. As regras ficam em DemandaService. */
@Entity
@Table(name = "demanda")
@Getter
@Setter
public class Demanda {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** null = fora do SEI. */
    @Column(length = 20)
    private String sei;

    @Column(nullable = false, length = 250)
    private String descricao;

    /** Local escolhido na lista (dá a região do preço da CDS). */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "local_id")
    private Local local;

    @Column(name = "local_texto", nullable = false, length = 120)
    private String localTexto;

    @Column(name = "data_inicio")
    private LocalDate dataInicio;

    /** null = atendimento de um dia só. */
    @Column(name = "data_fim")
    private LocalDate dataFim;

    @Column(name = "horario")
    private LocalTime horario;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Situacao situacao = Situacao.NOVA;

    @Column(name = "motivo_cancelamento", length = 100)
    private String motivoCancelamento;

    /** Preenchido = está na lixeira. */
    @Column(name = "excluida_em")
    private LocalDateTime excluidaEm;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "excluida_por_id")
    private Pessoa excluidaPor;

    @Column(name = "motivo_exclusao", length = 100)
    private String motivoExclusao;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Carga carga = Carga.COORDENADOR;

    /** Responsável (carga TECNICO) ou o técnico que atendeu (carga COORDENADOR ou SETOR). */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "tecnico_id")
    private Pessoa tecnico;

    @Column(name = "ticket_principal", columnDefinition = "char(8)")
    private String ticketPrincipal;

    @Column(name = "ticket_em")
    private LocalDateTime ticketEm;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "ticket_por_id")
    private Pessoa ticketPor;

    @Column(name = "acionada_em")
    private LocalDate acionadaEm;

    @Column(length = 100)
    private String informacoes;

    @Enumerated(EnumType.STRING)
    @Column(name = "aviso_tipo")
    private TipoAviso avisoTipo;

    /** 'COORDENADOR' ou o id do técnico. */
    @Column(name = "aviso_para", length = 60)
    private String avisoPara;

    @Column(name = "aviso_em")
    private LocalDateTime avisoEm;

    @Column(name = "criada_em", nullable = false)
    private LocalDateTime criadaEm;

    @Column(name = "atualizada_em", nullable = false)
    private LocalDateTime atualizadaEm;

    @OneToMany(mappedBy = "demanda", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("id")
    private List<Subticket> subtickets = new ArrayList<>();

    @OneToMany(mappedBy = "demanda", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("id")
    private List<Historico> historico = new ArrayList<>();

    /** Técnicos por quem a demanda já passou: decide entre os avisos "nova" e "retornou". */
    @ElementCollection
    @CollectionTable(name = "demanda_tecnico_passou", joinColumns = @JoinColumn(name = "demanda_id"))
    @Column(name = "tecnico_id")
    private Set<Long> passou = new HashSet<>();

    /** Fim do período: a Data para Conclusão ou, sem ela, a Data de Início. */
    public LocalDate fimDoPeriodo() { return dataFim != null ? dataFim : dataInicio; }

    public Pessoa responsavelTecnico() { return carga == Carga.TECNICO ? tecnico : null; }
}
